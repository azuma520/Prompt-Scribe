"""
Inspire Agent 狀態機

管理 Agent 的狀態轉換和中止條件

Version: 1.0.0
Date: 2025-01-27
"""

import time
import logging
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class InspirePhase(str, Enum):
    """Inspire Agent 階段"""
    UNDERSTANDING = "understanding"    # 理解階段
    EXPLORING = "exploring"            # 探索階段（搜尋、生成）
    REFINING = "refining"              # 精煉階段（迭代優化）
    FINALIZING = "finalizing"          # 定稿階段（嚴格驗證）
    COMPLETED = "completed"            # 完成
    ABORTED = "aborted"                # 中止


class InspireStateMachine:
    """
    Inspire Agent 狀態機
    
    管理狀態轉換、成本追蹤、中止條件檢查
    """
    
    # 預設限制（P0）
    DEFAULT_LIMITS = {
        "max_cost": 0.015,           # 最大成本 $0.015
        "max_turns": 15,             # 最大輪次
        "max_tool_calls_per_type": 5,  # 單工具最大調用次數
        "timeout_seconds": 120,      # 超時時間（秒）
        "convergence_threshold": 3,  # 收斂閾值（連續相同反饋次數）
    }
    
    def __init__(
        self,
        session_id: str,
        db,
        limits: Optional[Dict[str, Any]] = None,
        phase: Optional[str] = None
    ):
        """
        初始化狀態機
        
        Args:
            session_id: Session ID
            db: 資料庫實例（InspireDBWrapper）
            limits: 限制條件（可選，會與預設值合併）
            phase: 初始階段（可選，預設為 UNDERSTANDING）
        """
        self.session_id = session_id
        self.db = db
        
        # 合併限制條件
        self.limits = {**self.DEFAULT_LIMITS}
        if limits:
            self.limits.update(limits)
        
        # 初始狀態
        self.phase = InspirePhase(phase) if phase else InspirePhase.UNDERSTANDING
        
        # 追蹤狀態
        self.total_cost = 0.0
        self.total_turns = 0
        self.tool_calls: Dict[str, int] = {}  # {"search": 2 calls, "generate": 1}
        self.last_feedback: List[str] = []  # 最後幾次反饋（用於收斂檢測）
        self.start_time = time.time()
        
        # 最佳結果快取（用於中止時返回）
        self.best_result: Optional[Dict[str, Any]] = None
        
        logger.info(f"✅ State machine initialized: {self.session_id}, phase: {self.phase}")
    
    def record_tool_call(self, named_tool: str):
        """
        記錄工具調用
        
        Args:
            named_tool: 工具名稱（如 "understand_intent", "generate_ideas"）
        """
        self.tool_calls[named_tool] = self.tool_calls.get(named_tool, 0) + 1
        logger.debug(f"🔧 Tool call recorded: {named_tool} (total: {self.tool_calls[named_tool]})")
    
    def add_cost(self, cost: float):
        """
        累加成本
        
        Args:
            cost: 本次成本（美元）
        """
        self.total_cost += cost
        logger.debug(f"💰 Cost added: ${cost:.6f} (total: ${self.total_cost:.6f})")
    
    def record_feedback(self, feedback: str):
        """
        記錄使用者反饋（用於收斂檢測）
        
        Args:
            feedback: 使用者反饋文字
        """
        self.last_feedback.append(feedback)
        # 只保留最後 convergence_threshold + 1 次
        max_keep = self.limits["convergence_threshold"] + 1
        if len(self.last_feedback) > max_keep:
            self.last_feedback = self.last_feedback[-max_keep:]
    
    def increment_turn(self):
        """增加輪次計數"""
        self.total_turns += 1
        logger.debug(f"📊 Turn incremented: {self.total_turns}/{self.limits['max_turns']}")
    
    def should_abort(self) -> Tuple[bool, str]:
        """
        檢查是否應該中止
        
        Returns:
            (should_abort, reason)
        """
        # 檢查 1: 成本超限
        if self.total_cost >= self.limits["max_cost"]:
            return True, f"成本已達上限（${self.total_cost:.6f} >= ${self.limits['max_cost']:.6f}）"
        
        # 檢查 2: 輪次超限
        if self.total_turns >= self.limits["max_turns"]:
            return True, f"輪次已達上限（{self.total_turns} >= {self.limits['max_turns']}）"
        
        # 檢查 3: 超時
        elapsed = time.time() - self.start_time
        if elapsed >= self.limits["timeout_seconds"]:
            return True, f"處理時間超時（{elapsed:.1f}s >= {self.limits['timeout_seconds']}s）"
        
        # 檢查 4: 工具調用過多
        max_tool_calls = self.limits["max_tool_calls_per_type"]
        for tool_name, count in self.tool_calls.items():
            if count >= max_tool_calls:
                return True, f"工具 '{tool_name}' 調用次數過多（{count} >= {max_tool_calls}）"
        
        # 檢查 5: 收斂（連續相同反饋）
        threshold = self.limits["convergence_threshold"]
        if len(self.last_feedback) >= threshold:
            # 檢查最後 threshold 次反饋是否相同
            last_n = self.last_feedback[-threshold:]
            if len(set(last_n)) == 1:  # 全部相同
                return True, f"檢測到收斂：連續 {threshold} 次相同反饋"
        
        return False, ""
    
    async def transition(self, to_phase: InspirePhase, reason: str = ""):
        """
        狀態轉換
        
        Args:
            to_phase: 目標階段
            reason: 轉換原因（可選）
        """
        old_phase = self.phase
        self.phase = to_phase
        
        logger.info(f"🔄 State transition: {old_phase.value} → {to_phase.value} ({reason})")
        
        # 更新資料庫
        try:
            self.db.update_session_phase(self.session_id, to_phase.value)
        except Exception as e:
            logger.error(f"❌ Failed to update phase in database: {e}")
    
    def update_best_result(self, result: Dict[str, Any]):
        """
        更新最佳結果（用於中止時返回）
        
        Args:
            result: 結果字典
        """
        # 簡單策略：如果有品質分數，保留分數最高的
        if "quality_score" in result:
            current_score = result.get("quality_score", 0)
            if self.best_result is None or self.best_result.get("quality_score", 0) < current_score:
                self.best_result = result.copy()
        else:
            # 沒有品質分數時，總是更新
                self.best_result = result.copy()
    
    def get_best_result(self) -> Optional[Dict[str, Any]]:
        """獲取最佳結果"""
        return self.best_result
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計資訊"""
        elapsed = time.time() - self.start_time
        return {
            "session_id": self.session_id,
            "phase": self.phase.value,
            "total_cost": self.total_cost,
            "total_turns": self.total_turns,
            "tool_calls": self.tool_calls.copy(),
            "elapsed_seconds": elapsed,
            "limits": self.limits.copy(),
        }
    
    @classmethod
    async def from_session(
        cls,
        session_id: str,
        db,
        limits: Optional[Dict[str, Any]] = None
    ) -> "InspireStateMachine":
        """
        從資料庫恢復狀態機
        
        Args:
            session_id: Session ID
            db: 資料庫實例
            limits: 限制條件（可選）
            
        Returns:
            InspireStateMachine 實例
        """
        try:
            # 從資料庫獲取 Session 資訊
            session_data = db.get_session(session_id)
            
            if not session_data:
                raise ValueError(f"Session {session_id} not found")
            
            # 創建狀態機
            state_machine = cls(
                session_id=session_id,
                db=db,
                limits=limits,
                phase=session_data.get("current_phase")
            )
            
            # 恢復追蹤狀態
            state_machine.total_cost = session_data.get("total_cost", 0.0)
            state_machine.total_turns = session_data.get("total_tool_calls", 0)
            
            logger.info(f"✅ State machine restored from session: {session_id}")
            return state_machine
            
        except Exception as e:
            logger.error(f"❌ Failed to restore state machine: {e}")
            raise
    
    def get_abort_message(self, reason: str) -> str:
        """
        生成友好的中止訊息（不暴露技術細節）
        
        Args:
            reason: 中止原因
            
        Returns:
            友好的訊息
        """
        # 映射技術原因到友好訊息
        friendly_messages = {
            "成本": "已達到處理上限",
            "輪次": "對話輪次已達上限",
            "超時": "處理時間過長",
            "工具": "系統資源已用盡",
            "收斂": "檢測到重複反饋",
        }
        
        # 嘗試匹配
        for key, message in friendly_messages.items():
            if key in reason:
                return f"對話已結束：{message}。您可以使用當前最佳結果，或重新開始對話。"
        
        # 預設訊息
        return "對話已結束。您可以使用當前最佳結果，或重新開始對話。"

