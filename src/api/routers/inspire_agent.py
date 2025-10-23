"""
Inspire Agent API 端點

提供 Inspire Creative Agent 的 REST API 接口。

Version: 2.0.0
Date: 2025-10-22
"""

import os
import uuid
import logging
from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI

from agents import Agent, Runner, function_tool, set_default_openai_key, ModelSettings
from openai.types.shared import Reasoning
from openai import AsyncOpenAI
from typing import List, Dict, Any as typing_Any, Optional

# 導入配置
from config import settings

# 導入我們的模型
from models.inspire_models import (
    InspireStartRequest,
    InspireContinueRequest,
    InspireFeedbackRequest,
    InspireStartResponse,
    InspireContinueResponse,
    InspireStatusResponse,
    InspireErrorResponse,
    SessionMetadata,
    InspireSession,
)

# 導入服務
from services.inspire_session_manager import get_session_manager, create_inspire_session
from services.inspire_db_wrapper import InspireDBWrapper
from tools.inspire_tools import (
    understand_intent,
    search_examples,
    generate_ideas,
    validate_quality,
    finalize_prompt,
)

# 導入 System Prompt
from prompts import get_system_prompt

# 設定日誌
logger = logging.getLogger(__name__)

# ============================================================================
# Router 設定
# ============================================================================

router = APIRouter(
    prefix="/api/inspire",
    tags=["Inspire Agent"],
    responses={
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)

# ============================================================================
# Responses API 原生實現
# ============================================================================

def prepare_tools_for_responses_api() -> List[Dict[str, typing_Any]]:
    """
    準備工具定義（Responses API 格式）
    
    根據官方遷移文檔，Responses API 的工具定義格式：
    {
        "type": "function",
        "name": "tool_name",
        "description": "...",
        "parameters": { ... }
    }
    
    注意：不需要外層的 "function" 包裝（內部標記）
    """
    
    from tools.inspire_tools import INSPIRE_TOOLS
    from agents import FunctionTool
    
    # INSPIRE_TOOLS 是已經準備好的工具列表
    tools = []
    
    for tool in INSPIRE_TOOLS:
        if isinstance(tool, FunctionTool):
            # 從 FunctionTool 對象中提取定義（Responses API 格式）
            tools.append({
                "type": "function",
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.params_json_schema or {"type": "object", "properties": {}}
            })
        else:
            logger.warning(f"⚠️ Unknown tool type: {type(tool)}")
    
    logger.info(f"✅ Prepared {len(tools)} tools for Responses API")
    return tools


async def run_inspire_with_responses_api(
    client: AsyncOpenAI,
    user_message: str,
    system_prompt: str,
    tools: List[Dict[str, typing_Any]],
    model: str = "gpt-5",
    max_turns: int = 10,
    previous_response_id: Optional[str] = None,
    first_turn_mode: bool = False,
    force_tool_name: Optional[str] = None,
    stop_on_first_tool: bool = False
) -> Dict[str, typing_Any]:
    """
    使用 Responses API 原生方式運行 Inspire Agent
    
    核心策略（根據官方文檔）：
    1. 構建完整的 input_list（包含所有對話歷史）
    2. 每次請求都傳遞完整的 input_list
    3. 手動處理工具調用循環
    
    參考：https://platform.openai.com/docs/guides/function-calling
    
    Args:
        client: AsyncOpenAI 客戶端
        user_message: 用戶輸入
        system_prompt: 系統提示
        tools: 工具列表
        model: 模型名稱
        max_turns: 最大輪次
        
    Returns:
        包含 final_output、tool_calls、metadata 的字典
    """
    
    logger.info(f"🚀 Starting Responses API native run")
    
    # 統計數據
    total_tool_calls = 0
    all_responses = []
    
    # 🔑 構建完整的 input_list（官方推薦方式）
    input_list = [{"role": "user", "content": user_message}]
    
    try:
        # 第一輪：用戶輸入
        logger.info(f"📤 Turn 1: User input")
        
        # 根據模型決定參數
        create_params = {
            "model": model,
            "instructions": system_prompt,
            "input": input_list if not previous_response_id else user_message,  # 🔑 如果有 previous_response_id，只傳新訊息
            "tools": tools,
            "store": True,
            "timeout": 30.0,  # 添加 30 秒 timeout
        }
        
        # 如果有 previous_response_id，添加到參數中
        if previous_response_id:
            create_params["previous_response_id"] = previous_response_id
            logger.info(f"🔗 Using previous_response_id: {previous_response_id}")
        
        # 只有 GPT-5 支持 reasoning 參數
        if model.startswith("gpt-5") and not model.startswith("gpt-5-"):
            create_params["reasoning"] = {"effort": "low"}  # 降低 effort 以提升速度
            create_params["text"] = {"verbosity": "low"}
        
        # 如需強制首輪執行指定工具（僅在無 previous_response_id 時生效）
        if (not previous_response_id) and force_tool_name:
            # 確認工具名稱存在
            tool_names = [t.get("name", "") for t in tools]
            logger.info(f"Available tools: {tool_names}")
            if force_tool_name in tool_names:
                create_params["tool_choice"] = {"type": "function", "name": force_tool_name}
                logger.info(f"Forcing first tool call: {force_tool_name}")
            else:
                logger.warning(f"Tool {force_tool_name} not found in available tools: {tool_names}")

        response = await client.responses.create(**create_params)
        
        # 🔑 保存完整的 response.output 到 input_list
        input_list += response.output
        
        all_responses.append(response)
        turn = 1
        
        # 🔑 關鍵修復：處理強制 tool call
        for item in response.output:
            if item.type == "function_call":
                logger.info(f"🔧 Processing forced tool call: {item.name}")
                
                # 解析工具參數
                import json
                tool_args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                
                # 執行工具
                try:
                    from tools.inspire_tools import execute_tool_by_name
                    tool_result = execute_tool_by_name(item.name, tool_args)
                    logger.info(f"✅ Tool {item.name} executed successfully")
                    logger.info(f"📤 Tool result: {tool_result}")
                    
                    # 🔑 基於官方文檔：正確的 function_call_output 格式
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(tool_result, ensure_ascii=False)
                    })
                    
                    total_tool_calls += 1
                    
                except Exception as e:
                    logger.error(f"❌ Tool execution failed: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    
                    # 添加錯誤結果
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({"error": str(e), "status": "failed"})
                    })
        
        # 首輪即回傳：僅回傳第一輪模型輸出（或一次工具）
        if first_turn_mode:
            logger.info("First-turn mode enabled: returning after first response")
        else:
            # 🔑 基於官方文檔：實現完整的 5 步工具調用流程
            if stop_on_first_tool and any(item.type == "function_call" for item in response.output):
                logger.info("Stop on first tool enabled, implementing official 5-step tool calling flow")
                
                # 步驟 3-4: 執行工具並添加結果到 input_list
                for item in response.output:
                    if item.type == "function_call":
                        try:
                            from tools.inspire_tools import execute_tool_by_name
                            import json
                            tool_args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                            tool_result = execute_tool_by_name(item.name, tool_args)
                            
                            # 基於官方文檔：添加 function_call_output
                            input_list.append({
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": json.dumps(tool_result, ensure_ascii=False)
                            })
                            
                            total_tool_calls += 1
                            
                        except Exception as e:
                            logger.error(f"Tool execution failed: {e}")
                            input_list.append({
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": json.dumps({"error": str(e)}, ensure_ascii=False)
                            })
                
                # 步驟 5: 發送工具結果給模型獲取最終響應
                final_response = await client.responses.create(
                    model=model,
                    input=input_list,
                    tools=tools,
                    timeout=30.0
                )
                
                # 提取最終輸出
                final_output = ""
                for item in final_response.output:
                    if item.type == "message":
                        # 確保 content 是字符串
                        if isinstance(item.content, str):
                            final_output = item.content
                        elif isinstance(item.content, list):
                            final_output = str(item.content)
                        else:
                            final_output = str(item.content)
                        break
                
                # 提取 directions 數據
                directions = None
                for item in input_list:
                    if isinstance(item, dict) and item.get("type") == "function_call_output":
                        try:
                            output_data = json.loads(item.get("output", "{}"))
                            if "directions" in output_data:
                                directions = output_data["directions"]
                                logger.info(f"Extracted directions from function_call_output: {len(directions)} items")
                                break
                        except Exception as e:
                            logger.warning(f"Could not parse function_call_output for directions: {e}")
                            continue
                
                # 確保 directions 被正確設置
                if directions:
                    logger.info(f"Directions successfully extracted: {len(directions)} items")
                else:
                    logger.warning("No directions found in function_call_output")
                
                return {
                    "message": final_output,
                    "final_output": final_output,
                    "total_tool_calls": total_tool_calls,
                    "turn_count": 1,
                    "all_responses": [response, final_response],
                    "last_response_id": final_response.id,
                    "is_completed": True,
                    "directions": directions,
                    "phase": "exploring" if directions else "understanding",
                    "input_list": input_list  # 基於官方文檔：傳遞 input_list 用於數據提取
                }
        
            # 🔑 關鍵修復：如果強制 tool call 且已處理，直接返回
            if force_tool_name and any(item.type == "function_call" for item in response.output):
                logger.info("Forced tool call processed, returning results")
            else:
                # 循環處理工具調用
                while (turn < max_turns) and (not first_turn_mode):
                    # 檢查最後一個輸出是否是工具調用
                    last_output = response.output[-1] if response.output else None
                    
                    if not last_output or last_output.type != "function_call":
                        # 沒有工具調用，對話完成
                        logger.info(f"✅ Conversation completed after {turn} turns")
                        break
                    
                    # 有工具調用
                    function_call = last_output
                    tool_name = function_call.name
                    tool_args_raw = function_call.arguments
                    
                    # 🔍 詳細日誌：打印完整的 function_call 對象
                    logger.info(f"🔧 Turn {turn + 1}: Tool call - {tool_name}")
                    logger.info(f"📋 Function call ID: {function_call.id}")
                    logger.info(f"📋 Function call object: {function_call}")
                    
                    # 解析工具參數（Responses API 返回的是 JSON 字符串）
                    import json
                    if isinstance(tool_args_raw, str):
                        tool_args = json.loads(tool_args_raw)
                    else:
                        tool_args = tool_args_raw
                    
                    logger.info(f"📋 Tool args (parsed): {tool_args}")
                    total_tool_calls += 1
                    
                    # 執行工具
                    try:
                        from tools.inspire_tools import execute_tool_by_name
                        
                        tool_result = execute_tool_by_name(tool_name, tool_args)
                        logger.info(f"✅ Tool {tool_name} executed successfully")
                        logger.info(f"📤 Tool result: {tool_result}")
                        
                    except Exception as e:
                        logger.error(f"❌ Tool execution failed: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        tool_result = {"error": str(e)}
                    
                    # 下一輪：添加工具輸出到 input_list
                    turn += 1
                    logger.info(f"📤 Turn {turn}: Sending tool output")
                    
                    # 將工具結果轉換為 JSON 字符串
                    import json
                    tool_output_str = json.dumps(tool_result, ensure_ascii=False)
                    
                    # 🔑 添加工具輸出到 input_list（官方推薦方式）
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": function_call.call_id,
                        "output": tool_output_str  # JSON 字符串
                    })
                    
                    logger.info(f"📤 Sending function_call_output:")
                    logger.info(f"   - call_id: {function_call.call_id}")
                    logger.info(f"   - output (JSON string): {tool_output_str[:200]}...")
                    logger.info(f"   - input_list length: {len(input_list)}")
                    
                    # 🔑 第二次請求：傳遞完整的 input_list（不使用 previous_response_id）
                    response = await client.responses.create(
                        model=model,
                        instructions=system_prompt,  # 保持 instructions
                        input=input_list,  # 🔑 完整的對話歷史
                        tools=tools,
                        store=True
                    )
                    
                    # 🔑 保存新的 response.output 到 input_list
                    input_list += response.output
                    
                    all_responses.append(response)
        
        # 提取最終輸出和方向數據
        final_output = None
        directions = None
        phase = "understanding"
        
        # 🔑 從 Context 中提取數據（工具執行結果）
        from contextvars import ContextVar
        session_context = ContextVar('inspire_session', default={})
        ctx = session_context.get()
        
        if "generated_directions" in ctx:
            directions = ctx["generated_directions"]
            phase = "exploring"
            logger.info(f"🎯 Found directions from context: {len(directions)} items")
        else:
            # 如果 Context 中沒有，嘗試從工具執行結果中提取
            logger.info(f"🔍 Context keys: {list(ctx.keys())}")
            logger.info(f"🔍 Looking for directions in tool results...")
            
            # 從 input_list 中查找 function_call_output (基於最佳實踐)
            for item in input_list:
                # 檢查是否是字典類型
                if isinstance(item, dict) and item.get("type") == "function_call_output":
                    try:
                        import json
                        output_data = json.loads(item.get("output", "{}"))
                        if "directions" in output_data and output_data["directions"]:
                            directions = output_data["directions"]
                            phase = "exploring"
                            logger.info(f"Found directions from tool output: {len(directions)} items")
                            break
                    except Exception as e:
                        logger.warning(f"Could not parse tool output: {e}")
                else:
                    # 如果不是字典，跳過
                    logger.debug(f"Skipping non-dict item: {type(item)}")
        
        # 從所有工具調用結果中提取數據
        for response in all_responses:
            for output_item in response.output:
                if output_item.type == "function_call":
                    # 解析工具調用參數
                    try:
                        import json
                        if isinstance(output_item.arguments, str):
                            tool_args = json.loads(output_item.arguments)
                        else:
                            tool_args = output_item.arguments
                        
                        # 檢查是否是 generate_ideas 工具的結果
                        if "ideas" in tool_args:
                            directions = tool_args["ideas"]
                            phase = "exploring"
                            logger.info(f"🎯 Found directions: {len(directions)} items")
                        
                        # 檢查是否是最終 prompt
                        if "final_prompt" in tool_args:
                            phase = "completed"
                            logger.info(f"✅ Found final prompt")
                            
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"⚠️ Could not parse tool output: {e}")
        
        # 提取最終文本輸出
        for response in reversed(all_responses):
            for output_item in reversed(response.output):
                if output_item.type == "message":
                    # 提取文本內容
                    for content in output_item.content:
                        if content.type == "output_text":
                            final_output = content.text
                            break
                    if final_output:
                        break
            if final_output:
                break
        
        if not final_output:
            final_output = response.output_text if hasattr(response, 'output_text') else "No output"
        
        logger.info(f"✅ Responses API run completed: {total_tool_calls} tool calls, {turn} turns")
        logger.info(f"📊 Final phase: {phase}, directions: {len(directions) if directions else 0}")
        logger.info(f"🔍 Debug - directions type: {type(directions)}, value: {directions}")
        logger.info(f"🔍 Debug - phase: {phase}")
        
        return {
            "message": final_output,  # 給 continue 端點使用
            "final_output": final_output,  # 給 start 端點使用（兼容性）
            "total_tool_calls": total_tool_calls,
            "turn_count": turn,
            "all_responses": all_responses,
            "last_response_id": response.id,
            "is_completed": False,  # continue 時默認不完成
            "directions": directions,  # 新增：方向數據
            "phase": phase,  # 新增：當前階段
        }
        
    except Exception as e:
        logger.error(f"❌ Responses API run failed: {e}")
        raise


# ============================================================================
# 依賴注入 (Dependencies)
# ============================================================================

def get_openai_client() -> AsyncOpenAI:
    """獲取 OpenAI 客戶端"""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured"
        )
    
    # 配置超時和重試
    import httpx
    timeout = httpx.Timeout(settings.openai_timeout)
    
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=timeout,
        max_retries=2  # 減少重試次數
    )


def get_db_wrapper() -> InspireDBWrapper:
    """獲取資料庫封裝層實例"""
    return InspireDBWrapper()


def get_inspire_agent(
    client: Annotated[AsyncOpenAI, Depends(get_openai_client)]
) -> Agent:
    """
    獲取 Inspire Agent 實例
    
    Note: 這裡創建的是完整配置的 Agent
    """
    
    # 設置 OpenAI API Key（確保 Agent 能讀取到）
    set_default_openai_key(settings.openai_api_key)
    
    # 獲取 System Prompt
    system_prompt = get_system_prompt(version="full")
    
    # 配置 GPT-5 Responses API 參數
    model_settings = ModelSettings(
        reasoning=Reasoning(effort="low"),  # 降低 reasoning effort 以提升速度
        verbosity="low",  # 降低冗長度
        extra_args={
            "service_tier": "flex",
            "user": "inspire_agent_user"
        }
    )
    
    # 創建 Agent
    agent = Agent(
        name="Inspire",
        instructions=system_prompt,
        model="gpt-5",  # 使用 GPT-5
        model_settings=model_settings,
        tools=[
            understand_intent,
            search_examples,
            generate_ideas,
            validate_quality,
            finalize_prompt,
        ]
    )
    
    logger.info("✅ Inspire Agent initialized with 5 tools")
    return agent


async def get_session_from_id(session_id: str) -> tuple:
    """
    從 session_id 獲取 SDK Session 和業務 Session
    
    Returns:
        (sdk_session, business_session): SDK Session 和業務 Session
    
    Raises:
        HTTPException: 如果 Session 不存在
    """
    
    # 獲取 SDK Session（用於對話歷史）
    session_manager = get_session_manager()
    sdk_session = session_manager.create_session(session_id)
    
    # 獲取業務 Session（從資料庫）
    db = get_db_wrapper()
    business_session = db.get_session(session_id)
    
    if business_session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    return sdk_session, business_session


# ============================================================================
# Background Tasks
# ============================================================================

async def create_and_persist_session(
    session_id: str,
    business_data: dict,
    user_access_level: str = "all-ages"
):
    """
    後台任務：創建並持久化 Session 資料到資料庫
    
    Args:
        session_id: Session ID
        business_data: 業務資料
        user_access_level: 使用者權限級別
    """
    try:
        db = get_db_wrapper()
        # 先創建 session
        db.create_session(session_id, user_access_level=user_access_level)
        # 再更新資料
        db.update_session_data(session_id, **business_data)
        logger.info(f"✅ Session {session_id} created and persisted to database")
    except Exception as e:
        logger.error(f"❌ Failed to create/persist session {session_id}: {e}")


async def persist_session_to_db(
    session_id: str,
    business_data: dict
):
    """
    後台任務：將 Session 資料持久化到資料庫
    
    Args:
        session_id: Session ID
        business_data: 業務資料
    """
    try:
        db = get_db_wrapper()
        db.update_session_data(session_id, **business_data)
        logger.info(f"✅ Session {session_id} persisted to database")
    except Exception as e:
        logger.error(f"❌ Failed to persist session {session_id}: {e}")


async def log_session_completion(
    session_id: str,
    completion_reason: str
):
    """
    後台任務：記錄 Session 完成
    
    Args:
        session_id: Session ID
        completion_reason: 完成原因
    """
    try:
        db = get_db_wrapper()
        db.complete_session(
            session_id=session_id,
            completion_reason=completion_reason
        )
        logger.info(f"✅ Session {session_id} completed: {completion_reason}")
    except Exception as e:
        logger.error(f"❌ Failed to log completion for {session_id}: {e}")


# ============================================================================
# API 端點
# ============================================================================

@router.post(
    "/start",
    response_model=InspireStartResponse,
    status_code=status.HTTP_200_OK,
    summary="開始 Inspire 對話",
    description="開始一個新的 Inspire 創作對話 Session"
)
async def start_inspire_conversation(
    request: InspireStartRequest,
    background_tasks: BackgroundTasks,
    client: Annotated[AsyncOpenAI, Depends(get_openai_client)],
    db: Annotated[InspireDBWrapper, Depends(get_db_wrapper)],
):
    """
    開始 Inspire 對話
    
    **流程**：
    1. 創建新 Session
    2. 運行 Agent（理解意圖 + 可能的方向生成）
    3. 返回初始回應
    
    **範例**：
    ```json
    {
        "message": "櫻花樹下的和服少女，溫柔寧靜的氛圍",
        "user_access_level": "all-ages"
    }
    ```
    """
    
    try:
        # 1. 生成 Session ID
        session_id = str(uuid.uuid4())
        logger.info(f"🚀 Starting new Inspire session: {session_id}")
        
        # 2. 創建 SDK Session
        session_manager = get_session_manager()
        sdk_session = session_manager.create_session(session_id)
        
        # 3. 獲取 System Prompt 和工具
        from prompts import get_system_prompt
        system_prompt = get_system_prompt(version="full")
        tools = prepare_tools_for_responses_api()
        
        # 4. 運行 Agent（使用 Responses API 原生實現）
        logger.info(f"🤖 Running Inspire Agent with Responses API for session {session_id}")
        start_time = datetime.now()
        
        # 使用 GPT-4o-mini 並基於 Context7 最佳實踐
        result = await run_inspire_with_responses_api(
            client=client,
            user_message=request.message,
            system_prompt=system_prompt,
            tools=tools,
            model="gpt-4o-mini",  # GPT-4o-mini: 更快的響應速度(~5-8秒)
            max_turns=1,
            first_turn_mode=False,  # 允許一次工具回合以取得 directions
            force_tool_name="generate_ideas",
            # 基於 Context7 最佳實踐：使用 stop_on_first_tool 行為
            stop_on_first_tool=True
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 5. 解析 Agent 回應
        logger.info(f"Debug - result keys: {list(result.keys())}")
        
        response_message = result.get("final_output", "")
        logger.info(f"Debug - response_message type: {type(response_message)}, value: {response_message}")
        
        # 確保 response_message 是字符串
        if isinstance(response_message, list):
            # 如果是列表，提取文本內容
            text_parts = []
            for item in response_message:
                if hasattr(item, 'text'):
                    text_parts.append(item.text)
                elif hasattr(item, 'content'):
                    text_parts.append(item.content)
                else:
                    # 如果是 ResponseOutputText 對象，提取 text 屬性
                    if hasattr(item, 'text'):
                        text_parts.append(item.text)
                    else:
                        text_parts.append(str(item))
            response_message = " ".join(text_parts)
            logger.info(f"Debug - converted list to string: {response_message}")
        elif not isinstance(response_message, str):
            response_message = str(response_message)
            logger.info(f"Debug - converted to string: {response_message}")
        total_tool_calls = result["total_tool_calls"]
        last_response_id = result["last_response_id"]
        directions = result.get("directions")
        phase = result.get("phase", "understanding")
        
        # 🔑 基於 Context7 最佳實踐：實現自定義工具輸出提取器
        if not directions:
            logger.info("No directions found in result, implementing custom tool output extractor...")
            
            # 基於官方文檔的工具輸出提取器
            def extract_directions_from_tool_output(run_result):
                """基於官方文檔的工具輸出提取器"""
                # 步驟 1: 從 function_call_output 中提取
                for response in run_result.get("all_responses", []):
                    for item in response.output:
                        if hasattr(item, 'type') and item.type == "function_call_output":
                            try:
                                import json
                                # 基於官方文檔：解析 output 字段
                                output_data = json.loads(item.output) if isinstance(item.output, str) else item.output
                                if "directions" in output_data and output_data["directions"]:
                                    logger.info(f"Found directions from function_call_output: {len(output_data['directions'])} items")
                                    return output_data["directions"]
                            except Exception as e:
                                logger.warning(f"Could not parse function_call_output: {e}")
                
                # 步驟 2: 從 input_list 中的 function_call_output 提取
                for item in run_result.get("input_list", []):
                    if isinstance(item, dict) and item.get("type") == "function_call_output":
                        try:
                            import json
                            output_data = json.loads(item.get("output", "{}"))
                            if "directions" in output_data and output_data["directions"]:
                                logger.info(f"Found directions from input_list function_call_output: {len(output_data['directions'])} items")
                                return output_data["directions"]
                        except Exception as e:
                            logger.warning(f"Could not parse input_list function_call_output: {e}")
                
                return None
            
            # 使用自定義提取器
            extracted_directions = extract_directions_from_tool_output(result)
            if extracted_directions:
                directions = extracted_directions
                phase = "exploring"
        
        # 6. 準備 Session 資料
        # 確保 directions 被正確序列化
        if directions:
            import json
            # 確保 directions 是 JSON 可序列化的格式
            directions_json = json.loads(json.dumps(directions, ensure_ascii=False))
            logger.info(f"Debug - directions_json type: {type(directions_json)}, length: {len(directions_json)}")
        else:
            directions_json = None
            
        session_data = {
            "current_phase": phase,
            "processing_time_ms": processing_time,
            "last_user_message": request.message,
            "last_response_id": last_response_id,  # 🔑 保存用於 continue
            "total_tool_calls": total_tool_calls,
            "generated_directions": directions_json,  # 🔑 保存創意方向到資料庫
        }
        
        # 7. 同步創建並保存 Session 到資料庫（確保立即保存）
        try:
            logger.info(f"🔧 Creating session {session_id} with access level: {request.user_access_level}")
            # 先創建 session
            create_result = db.create_session(session_id, user_access_level=request.user_access_level)
            logger.info(f"🔧 Create session result: {create_result}")
            # 再更新資料
            update_result = db.update_session_data(session_id, **session_data)
            logger.info(f"🔧 Update session result: {update_result}")
            
            # 驗證 session 確實被保存
            verify_session = db.get_session(session_id)
            if verify_session:
                logger.info(f"Session {session_id} verified in database")
            else:
                logger.error(f"❌ Session {session_id} not found after creation")
                raise Exception("Session verification failed")
                
        except Exception as e:
            logger.error(f"❌ Failed to create/persist session {session_id}: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create session: {str(e)}"
            )
        
        # 8. 構建回應
        metadata = SessionMetadata(
            session_id=session_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            current_phase=phase,
            total_tool_calls=total_tool_calls,
            total_cost=0.0,  # TODO: 計算實際成本
            total_tokens=0,  # TODO: 從 result 中獲取
        )
        
        # 構建 data 對象
        data = None
        if directions:
            data = {"directions": directions}
        elif phase == "completed":
            data = {"final_output": response_message}
        
        response = InspireStartResponse(
            session_id=session_id,
            type="message" if not directions else "directions",
            message=response_message,
            phase=phase,
            metadata=metadata,
            data=data,
        )
        
        logger.info(f"Session {session_id} started successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error starting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start Inspire session: {str(e)}"
        )


@router.post(
    "/continue",
    response_model=InspireContinueResponse,
    status_code=status.HTTP_200_OK,
    summary="繼續 Inspire 對話",
    description="繼續現有的 Inspire 對話"
)
async def continue_inspire_conversation(
    request: InspireContinueRequest,
    background_tasks: BackgroundTasks,
    agent: Annotated[Agent, Depends(get_inspire_agent)],
    db: Annotated[InspireDBWrapper, Depends(get_db_wrapper)],
):
    """
    繼續 Inspire 對話
    
    **流程**：
    1. 獲取現有 Session
    2. 運行 Agent（繼續對話）
    3. 檢查是否完成
    4. 返回回應
    
    **範例**：
    ```json
    {
        "session_id": "abc123-def456",
        "message": "選擇第 2 個方向"
    }
    ```
    """
    
    try:
        session_id = request.session_id
        logger.info(f"🔄 Continuing session: {session_id}")
        
        # 1. 獲取 Session
        try:
            sdk_session, business_session = await get_session_from_id(session_id)
        except HTTPException as e:
            if e.status_code == 404:
                # Session 不存在，可能是資料庫連接問題
                logger.warning(f"⚠️ Session {session_id} not found in database, creating new session")
                # 創建一個基本的 business_session
                business_session = {
                    "session_id": session_id,
                    "created_at": datetime.now().isoformat(),
                    "current_phase": "understanding",
                    "total_tool_calls": 0,
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "status": "active"
                }
                # 獲取 SDK Session
                session_manager = get_session_manager()
                sdk_session = session_manager.create_session(session_id)
            else:
                raise e
        
        # 2. 檢查 Session 狀態
        if business_session.get("status") == "completed":
            raise HTTPException(
                status_code=400,
                detail="Session already completed"
            )
            
        # 3. 運行 Agent (使用原生 Responses API)
        start_time = datetime.now()
        
        # 從業務 Session 中獲取上一個 response_id
        previous_response_id = business_session.get("last_response_id")
        
        openai_client = get_openai_client()
        tools_prepared = prepare_tools_for_responses_api()
        
        result = await run_inspire_with_responses_api(
            client=openai_client,
            user_message=request.message,
            system_prompt=agent.instructions,
            tools=tools_prepared,
            model="gpt-5-mini",
            previous_response_id=previous_response_id,
            max_turns=1,
            first_turn_mode=True
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 4. 解析回應
        response_message = result.get("message", "")
        
        # 5. 檢查是否完成
        is_completed = result.get("is_completed", False)
        final_output = result.get("final_output") if is_completed else None
        
        # 6. 更新 Session
        session_data = {
            "updated_at": datetime.now().isoformat(),
            "last_user_message": request.message,
            "last_agent_message": response_message,
            "last_response_id": result.get("last_response_id"),
            "turn_count": result.get("turn_count", 0),
        }
        
        background_tasks.add_task(
            persist_session_to_db,
            session_id,
            session_data
        )
        
        # 如果完成，記錄
        if is_completed:
            background_tasks.add_task(
                log_session_completion,
                session_id,
                "user_satisfied"
            )
        
        # 7. 構建回應
        metadata = SessionMetadata(
            session_id=session_id,
            created_at=datetime.fromisoformat(business_session.get("created_at")),
            updated_at=datetime.now(),
            current_phase=business_session.get("current_phase", "understanding"),
            total_tool_calls=business_session.get("total_tool_calls", 0),
            total_cost=business_session.get("total_cost", 0.0),
            total_tokens=business_session.get("total_tokens", 0),
        )
        
        response = InspireContinueResponse(
            session_id=session_id,
            type="completed" if is_completed else "message",
            message=response_message,
            phase=business_session.get("current_phase", "understanding"),
            metadata=metadata,
            data=None,
            is_completed=is_completed,
            final_output=final_output,
        )
        
        logger.info(f"✅ Session {session_id} continued successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error continuing session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to continue session: {str(e)}"
        )


@router.get(
    "/status/{session_id}",
    response_model=InspireStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="查詢 Session 狀態",
    description="獲取指定 Session 的當前狀態和對話歷史"
)
async def get_inspire_status(
    session_id: str,
    db: Annotated[InspireDBWrapper, Depends(get_db_wrapper)],
):
    """
    查詢 Session 狀態
    
    **回應包含**：
    - Session 基本資訊
    - 當前狀態和階段
    - 對話歷史（最近 10 條）
    - 性能指標
    """
    
    try:
        logger.info(f"📊 Getting status for session: {session_id}")
        
        # 獲取 Session
        business_session = db.get_session(session_id)
        
        if business_session is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # 構建回應
        metadata = SessionMetadata(
            session_id=session_id,
            created_at=datetime.fromisoformat(business_session.get("created_at")),
            updated_at=datetime.fromisoformat(business_session.get("updated_at")),
            current_phase=business_session.get("current_phase", "understanding"),
            total_tool_calls=business_session.get("total_tool_calls", 0),
            total_cost=business_session.get("total_cost", 0.0),
            total_tokens=business_session.get("total_tokens", 0),
            quality_score=business_session.get("quality_score"),
            generated_directions=business_session.get("generated_directions"),  # 添加 generated_directions
        )
        
        response = InspireStatusResponse(
            session_id=session_id,
            status=business_session.get("status", "active"),
            metadata=metadata,
            conversation_history=business_session.get("conversation_history", [])[-10:],
        )
        
        logger.info(f"✅ Status retrieved for session {session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session status: {str(e)}"
        )


@router.post(
    "/feedback",
    status_code=status.HTTP_200_OK,
    summary="提交使用者反饋",
    description="提交對 Inspire 對話的滿意度和反饋"
)
async def submit_inspire_feedback(
    request: InspireFeedbackRequest,
    db: Annotated[InspireDBWrapper, Depends(get_db_wrapper)],
):
    """
    提交使用者反饋
    
    **用途**：
    - 收集使用者滿意度
    - 改進 Agent 品質
    - 數據分析
    """
    
    try:
        logger.info(f"📝 Submitting feedback for session: {request.session_id}")
        
        # 更新 Session
        feedback_data = {
            "user_satisfaction": request.satisfaction,
            "feedback_text": request.feedback_text,
            "would_use_again": request.would_use_again,
            "feedback_at": datetime.now().isoformat(),
        }
        
        db.update_session_data(request.session_id, feedback_data)
        
        logger.info(f"✅ Feedback submitted for session {request.session_id}")
        
        return {
            "success": True,
            "message": "感謝你的反饋！這將幫助我們改進 Inspire 🙏"
        }
        
    except Exception as e:
        logger.error(f"❌ Error submitting feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )


# ============================================================================
# 健康檢查
# ============================================================================

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Inspire Agent 健康檢查",
    description="檢查 Inspire Agent 服務狀態"
)
async def inspire_health_check():
    """
    健康檢查端點
    
    **檢查項目**：
    - OpenAI API 連接
    - Session Manager 狀態
    - 資料庫連接
    """
    
    try:
        # 檢查 Session Manager
        session_manager = get_session_manager()
        storage_info = session_manager.get_session_storage_info()
        
        # 檢查資料庫
        db = get_db_wrapper()
        # TODO: 添加資料庫 ping
        
        return {
            "status": "healthy",
            "service": "Inspire Agent",
            "version": "2.0.0",
            "storage": storage_info,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )

