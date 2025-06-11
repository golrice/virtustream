import pytest
from unittest.mock import MagicMock, patch
from LLM.textLLMWrapper import TextLLMWrapper
from modules.injection import Injection
from signals import Signals
import logging

@pytest.fixture
def mock_signals():
    logger = logging.getLogger("test")
    return Signals(logger)

@pytest.fixture
def mock_tts():
    return MagicMock()

@pytest.fixture
def text_llm_wrapper(mock_signals, mock_tts):
    return TextLLMWrapper(mock_signals, mock_tts, modules={})

def test_assemble_injections_with_no_modules(text_llm_wrapper):
    result = text_llm_wrapper.assemble_injections()
    assert result == []

def test_assemble_injections_with_modules(text_llm_wrapper):
    # 模拟两个模块
    mock_module1 = MagicMock()
    mock_module1.get_prompt_injection.return_value = Injection("text1", name="role1", priority=2)
    
    mock_module2 = MagicMock()
    mock_module2.get_prompt_injection.return_value = Injection("text2", name="role2", priority=1)
    
    # 更新 modules
    text_llm_wrapper.modules = {
        "module1": mock_module1,
        "module2": mock_module2
    }
    
    result = text_llm_wrapper.assemble_injections()
    
    # 验证 Injection 按优先级排序
    assert result == [
        {"role": "role2", "content": "text2"},  
        {"role": "role1", "content": "text1"}   
    ]
    
    # 验证 cleanup() 被调用
    mock_module1.cleanup.assert_called_once()
    mock_module2.cleanup.assert_called_once()

def test_assemble_injections_filters_low_priority(text_llm_wrapper):
    """测试 priority=-1 的 Injection 被过滤"""
    mock_module = MagicMock()
    mock_module.get_prompt_injection.return_value = Injection("text", name="role", priority=-1)
    
    text_llm_wrapper.modules = {"module": mock_module}
    result = text_llm_wrapper.assemble_injections()
    
    assert result == []  # priority=-1 被过滤

def test_assemble_injections_with_external_injections(text_llm_wrapper):
    """测试额外传入的 Injection 被合并"""
    external_injection = Injection("external", name="role_external", priority=0)
    
    mock_module = MagicMock()
    mock_module.get_prompt_injection.return_value = Injection("module", name="role_module", priority=1)
    
    text_llm_wrapper.modules = {"module": mock_module}
    result = text_llm_wrapper.assemble_injections([external_injection])
    
    assert result == [
        {"role": "role_external", "content": "external"},  # priority=0 (更高)
        {"role": "role_module", "content": "module"}       # priority=1
    ]
