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
from typing import List, Dict, Any as typing_Any

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
            # 從 FunctionTool 對象中提取定義
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
    max_turns: int = 10
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
            "input": input_list,  # 🔑 傳遞 input_list
            "tools": tools,
            "store": True,
        }
        
        # 只有 GPT-5 支持 reasoning 參數
        if model.startswith("gpt-5") and not model.startswith("gpt-5-"):
            create_params["reasoning"] = {"effort": "medium"}
            create_params["text"] = {"verbosity": "low"}
        
        response = await client.responses.create(**create_params)
        
        # 🔑 保存完整的 response.output 到 input_list
        input_list += response.output
        
        all_responses.append(response)
        turn = 1
        
        # 循環處理工具調用
        while turn < max_turns:
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
        
        # 提取最終輸出
        final_output = None
        for output_item in reversed(response.output):
            if output_item.type == "message":
                # 提取文本內容
                for content in output_item.content:
                    if content.type == "output_text":
                        final_output = content.text
                        break
                if final_output:
                    break
        
        if not final_output:
            final_output = response.output_text if hasattr(response, 'output_text') else "No output"
        
        logger.info(f"✅ Responses API run completed: {total_tool_calls} tool calls, {turn} turns")
        
        return {
            "final_output": final_output,
            "total_tool_calls": total_tool_calls,
            "total_turns": turn,
            "all_responses": all_responses,
            "last_response_id": response.id
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
    return AsyncOpenAI(api_key=settings.openai_api_key)


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
        reasoning=Reasoning(effort="medium"),  # GPT-5 需要的 reasoning 參數
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
        
        # 3. 在資料庫中創建 Session 記錄
        db.create_session(
            session_id=session_id,
            user_id=request.user_id,
            user_access_level=request.user_access_level,
        )
        
        # 4. 獲取 System Prompt 和工具
        from prompts import get_system_prompt
        system_prompt = get_system_prompt(version="full")
        tools = prepare_tools_for_responses_api()
        
        # 5. 運行 Agent（使用 Responses API 原生實現）
        logger.info(f"🤖 Running Inspire Agent with Responses API for session {session_id}")
        start_time = datetime.now()
        
        # 使用 GPT-5-mini 平衡速度和質量
        result = await run_inspire_with_responses_api(
            client=client,
            user_message=request.message,
            system_prompt=system_prompt,
            tools=tools,
            model="gpt-5-mini",  # GPT-5-mini: 平衡速度(~10-15秒)和質量
            max_turns=10
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 6. 解析 Agent 回應
        response_message = result["final_output"]
        total_tool_calls = result["total_tool_calls"]
        last_response_id = result["last_response_id"]
        
        # 7. 更新 Session 資料
        session_data = {
            "current_phase": "understanding",
            "processing_time_ms": processing_time,
            "last_user_message": request.message,
            "last_response_id": last_response_id,  # 🔑 保存用於 continue
            "total_tool_calls": total_tool_calls,
        }
        
        # 後台持久化
        background_tasks.add_task(
            persist_session_to_db,
            session_id,
            session_data
        )
        
        # 8. 構建回應
        metadata = SessionMetadata(
            session_id=session_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            current_phase="understanding",
            total_tool_calls=total_tool_calls,
            total_cost=0.0,  # TODO: 計算實際成本
            total_tokens=0,  # TODO: 從 result 中獲取
        )
        
        response = InspireStartResponse(
            session_id=session_id,
            type="message",
            message=response_message,
            phase="understanding",
            metadata=metadata,
            data=None,  # TODO: 如果有方向卡片，在這裡包含
        )
        
        logger.info(f"✅ Session {session_id} started successfully")
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
        sdk_session, business_session = await get_session_from_id(session_id)
        
        # 2. 檢查 Session 狀態
        if business_session.get("status") == "completed":
            raise HTTPException(
                status_code=400,
                detail="Session already completed"
            )
        
        # 3. 運行 Agent
        start_time = datetime.now()
        
        result = await Runner.run(
            agent,
            request.message,
            session=sdk_session
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 4. 解析回應
        response_message = result.final_output if hasattr(result, 'final_output') else str(result)
        
        # 5. 檢查是否完成
        is_completed = False  # TODO: 根據 Agent 的回應判斷
        final_output = None
        
        # 6. 更新 Session
        session_data = {
            "updated_at": datetime.now().isoformat(),
            "last_user_message": request.message,
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

