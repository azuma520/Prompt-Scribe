"""
Inspire State Machine 測試

測試狀態機的所有功能：
1. 狀態轉換
2. 中止條件檢查（5 個）
3. 成本追蹤
4. 工具調用記錄
5. 收斂檢測

Version: 1.0.0
Date: 2025-01-27
"""

import pytest
import time
from unittest.mock import MagicMock
from src.api.services.inspire_state_machine import (
    InspireStateMachine,
    InspirePhase,
)


class TestInspireStateMachine:
    """InspireStateMachine 單元測試"""

    def test_initialization(self):
        """測試初始化"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine(
            session_id="test-123",
            db=mock_db
        )
        
        assert state_machine.session_id == "test-123"
        assert state_machine.phase == InspirePhase.UNDERSTANDING
        assert state_machine.total_cost == 0.0
        assert state_machine.total_turns == 0
        assert state_machine.tool_calls == {}

    def test_record_tool_call(self):
        """測試工具調用記錄"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine("test-123", mock_db)
        
        state_machine.record_tool_call("understand_intent")
        state_machine.record_tool_call("generate_ideas")
        state_machine.record_tool_call("understand_intent")
        
        assert state_machine.tool_calls["understand_intent"] == 2
        assert state_machine.tool_calls["generate_ideas"] == 1

    def test_add_cost(self):
        """測試成本累加"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine("test-123", mock_db)
        
        state_machine.add_cost(0.001)
        state_machine.add_cost(0.002)
        
        assert state_machine.total_cost == 0.003

    def test_increment_turn(self):
        """測試輪次計數"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine("test-123", mock_db)
        
        state_machine.increment_turn()
        state_machine.increment_turn()
        
        assert state_machine.total_turns == 2

    def test_should_abort_cost(self):
        """測試成本超限中止"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine(
            "test-123",
            mock_db,
            limits={"max_cost": 0.001}
        )
        
        state_machine.add_cost(0.0015)
        should_abort, reason = state_machine.should_abort()
        
        assert should_abort == True
        assert "成本" in reason

    def test_should_abort_turns(self):
        """測試輪次超限中止"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine(
            "test-123",
            mock_db,
            limits={"max_turns": 3}
        )
        
        state_machine.total_turns = 3
        should_abort, reason = state_machine.should_abort()
        
        assert should_abort == True
        assert "輪次" in reason

    def test_should_abort_timeout(self):
        """測試超時中止"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine(
            "test-123",
            mock_db,
            limits={"timeout_seconds": 1}
        )
        
        # 等待超過超時時間
        time.sleep(1.1)
        should_abort, reason = state_machine.should_abort()
        
        assert should_abort == True
        assert "超時" in reason or "時間" in reason

    def test_should_abort_tool_calls(self):
        """測試工具調用過多中止"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine(
            "test-123",
            mock_db,
            limits={"max_tool_calls_per_type": 3}
        )
        
        # 調用同一個工具超過限制
        for _ in range(4):
            state_machine.record_tool_call("generate_ideas")
        
        should_abort, reason = state_machine.should_abort()
        
        assert should_abort == True
        assert "工具" in reason or "generate_ideas" in reason

    def test_should_abort_convergence(self):
        """測試收斂中止"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine(
            "test-123",
            mock_db,
            limits={"convergence_threshold": 3}
        )
        
        # 記錄相同的反饋 3 次
        for _ in range(3):
            state_machine.record_feedback("要更夢幻")
        
        should_abort, reason = state_machine.should_abort()
        
        assert should_abort == True
        assert "收斂" in reason or "重複" in reason

    def test_should_abort_no_abort(self):
        """測試不應中止的情況"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine("test-123", mock_db)
        
        # 正常情況：成本低、輪次少、未超時
        state_machine.add_cost(0.0001)
        state_machine.total_turns = 2
        
        should_abort, reason = state_machine.should_abort()
        
        assert should_abort == False
        assert reason == ""

    @pytest.mark.asyncio
    async def test_transition(self):
        """測試狀態轉換"""
        mock_db = MagicMock()
        mock_db.update_session_phase = MagicMock()
        
        state_machine = InspireStateMachine("test-123", mock_db)
        
        await state_machine.transition(InspirePhase.EXPLORING, "清晰度足夠")
        
        assert state_machine.phase == InspirePhase.EXPLORING
        mock_db.update_session_phase.assert_called_once()

    def test_update_best_result(self):
        """測試更新最佳結果"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine("test-123", mock_db)
        
        # 沒有品質分數時，總是更新
        state_machine.update_best_result({"output": "result1"})
        assert state_machine.best_result == {"output": "result1"}
        
        # 有品質分數時，保留分數更高的
        state_machine.update_best_result({"quality_score": 80})
        assert state_machine.best_result["quality_score"] == 80
        
        state_machine.update_best_result({"quality_score": 70})
        assert state_machine.best_result["quality_score"] == 80  # 不應該更新
        
        state_machine.update_best_result({"quality_score": 90})
        assert state_machine.best_result["quality_score"] == 90  # 應該更新

    def test_get_stats(self):
        """測試獲取統計資訊"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine("test-123", mock_db)
        
        state_machine.add_cost(0.001)
        state_machine.total_turns = 5
        state_machine.record_tool_call("generate_ideas")
        
        stats = state_machine.get_stats()
        
        assert stats["session_id"] == "test-123"
        assert stats["phase"] == "understanding"
        assert stats["total_cost"] == 0.001
        assert stats["total_turns"] == 5
        assert stats["tool_calls"]["generate_ideas"] == 1

    def test_get_abort_message(self):
        """測試中止訊息生成"""
        mock_db = MagicMock()
        state_machine = InspireStateMachine("test-123", mock_db)
        
        # 測試各種中止原因
        messages = [
            state_machine.get_abort_message("成本已達上限"),
            state_machine.get_abort_message("輪次已達上限"),
            state_machine.get_abort_message("處理時間超時"),
            state_machine.get_abort_message("工具調用過多"),
            state_machine.get_abort_message("檢測到收斂"),
        ]
        
        # 所有訊息都應該不包含技術細節
        for msg in messages:
            assert "成本已達上限" not in msg or "$" not in msg  # 允許友好訊息包含 $ 符號
            assert "輪次已達上限" not in msg
            assert "處理時間超時" not in msg
            assert "工具調用過多" not in msg
            assert "檢測到收斂" not in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

