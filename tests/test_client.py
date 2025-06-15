import pytest
import logging
from unittest.mock import MagicMock
from modules.client import Client

MAX_MESSAGES_LEN = 10  

@pytest.mark.asyncio
async def test_chat_message_under_limit(monkeypatch):
    # 模拟 recentMessages 属性
    mock_signals = MagicMock()
    mock_signals.recentMessages = []

    client = Client(mock_signals, enable=True)

    handler = client._io.handlers['/']['chat_message']

    # 执行事件处理逻辑
    await handler({"msg": "hello"})

    assert mock_signals.recentMessages == [{"msg": "hello"}]

@pytest.mark.asyncio
async def test_chat_message_over_limit():
    mock_signals = MagicMock()
    mock_signals.recentMessages = [{"msg": f"m{i}"} for i in range(MAX_MESSAGES_LEN)]

    client = Client(mock_signals, enable=True)

    handler = client._io.handlers['/']['chat_message']
    await handler({"msg": "new"})

    # 最早的消息被踢出，最新的消息在末尾
    assert mock_signals.recentMessages == [{"msg": f"m{i}"} for i in range(1, MAX_MESSAGES_LEN)] + [{"msg": "new"}]
