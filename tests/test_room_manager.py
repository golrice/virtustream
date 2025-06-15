import pytest
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock, patch
from room_manager import BiliClient, Config
from socketio import AsyncServer


@pytest.fixture
def mock_connect_server():
    """模拟连接服务器"""
    server = MagicMock(spec=AsyncServer)
    server.emit = AsyncMock()
    return server

@pytest.fixture
def bili_client(mock_connect_server):
    """创建BiliClient实例"""
    return BiliClient(
        idCode="test_id",
        appId=12345,
        key="test_key",
        secret="test_secret",
        host="https://test.api.com",
        connect_server=mock_connect_server
    )

@pytest.mark.asyncio
async def test_handle_dm_message(bili_client, mock_connect_server):
    """测试处理普通弹幕消息"""
    # 构造普通弹幕消息数据
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_DM",
        "data": {
            "uname": "测试用户",
            "msg": "这是一条测试弹幕"
        }
    }
    
    with patch('builtins.print') as mock_print:
        await bili_client.handleMassage(resp_body)
    
    # 验证消息格式化正确
    expected_msg = "测试用户 说: 这是一条测试弹幕"
    mock_print.assert_called_with(f"[BiliClient] 收到消息: {expected_msg}")
    
    # 验证消息被发送到连接服务器
    mock_connect_server.emit.assert_called_once_with('chat_message', expected_msg)

@pytest.mark.asyncio
async def test_handle_gift_message(bili_client, mock_connect_server):
    """测试处理礼物消息"""
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_SEND_GIFT",
        "data": {
            "uname": "土豪用户",
            "gift_name": "火箭",
            "num": 5
        }
    }
    
    with patch('builtins.print') as mock_print:
        await bili_client.handleMassage(resp_body)
    
    expected_msg = "土豪用户 送出了 5 个 火箭"
    mock_print.assert_called_with(f"[BiliClient] 收到消息: {expected_msg}")
    mock_connect_server.emit.assert_called_once_with('chat_message', expected_msg)

@pytest.mark.asyncio
async def test_handle_super_chat_message(bili_client, mock_connect_server):
    """测试处理付费聊天消息"""
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_SUPER_CHAT",
        "data": {
            "uname": "付费用户",
            "message": "这是付费消息内容",
            "rmb": 30
        }
    }
    
    with patch('builtins.print') as mock_print:
        await bili_client.handleMassage(resp_body)
    
    expected_msg = "付费用户 发送了付费聊天: 这是付费消息内容 (金额: 30元)"
    mock_print.assert_called_with(f"[BiliClient] 收到消息: {expected_msg}")
    mock_connect_server.emit.assert_called_once_with('chat_message', expected_msg)

@pytest.mark.asyncio
async def test_handle_guard_message(bili_client, mock_connect_server):
    """测试处理上舰消息"""
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_GUARD",
        "data": {
            "user_info": {
                "uname": "舰长用户"
            },
            "guard_level": "舰长"
        }
    }
    
    with patch('builtins.print') as mock_print:
        await bili_client.handleMassage(resp_body)
    
    # 注意：原代码中有个变量名错误，unmae应该是uname
    # 这里测试的是实际代码的行为
    expected_msg = "舰长用户 成为了 舰长 舰长"
    mock_print.assert_called_with(f"[BiliClient] 收到消息: {expected_msg}")
    mock_connect_server.emit.assert_called_once_with('chat_message', expected_msg)

@pytest.mark.asyncio
async def test_handle_unknown_message(bili_client, mock_connect_server):
    """测试处理未知类型消息"""
    resp_body = {
        "cmd": "UNKNOWN_MESSAGE_TYPE",
        "data": {
            "some_field": "some_value"
        }
    }
    
    with patch('builtins.print') as mock_print:
        await bili_client.handleMassage(resp_body)
    
    # 未知消息类型不应该产生任何输出或emit调用
    mock_print.assert_not_called()
    mock_connect_server.emit.assert_not_called()

@pytest.mark.asyncio
async def test_handle_message_with_missing_data(bili_client, mock_connect_server):
    """测试处理缺少数据字段的消息"""
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_DM",
        "data": {
            "uname": "测试用户"
            # 缺少msg字段
        }
    }
    
    # 这应该会引发KeyError异常
    with pytest.raises(KeyError):
        await bili_client.handleMassage(resp_body)

@pytest.mark.asyncio
async def test_handle_message_with_empty_data(bili_client, mock_connect_server):
    """测试处理空数据的消息"""
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_DM",
        "data": {
            "uname": "",
            "msg": ""
        }
    }
    
    with patch('builtins.print') as mock_print:
        await bili_client.handleMassage(resp_body)
    
    expected_msg = " 说: "
    mock_print.assert_called_with(f"[BiliClient] 收到消息: {expected_msg}")
    mock_connect_server.emit.assert_called_once_with('chat_message', expected_msg)

@pytest.mark.asyncio
async def test_handle_multiple_message_types_sequence(bili_client, mock_connect_server):
    """测试连续处理多种类型的消息"""
    messages = [
        {
            "cmd": "LIVE_OPEN_PLATFORM_DM",
            "data": {"uname": "用户1", "msg": "消息1"}
        },
        {
            "cmd": "LIVE_OPEN_PLATFORM_SEND_GIFT",
            "data": {"uname": "用户2", "gift_name": "鲜花", "num": 1}
        },
        {
            "cmd": "LIVE_OPEN_PLATFORM_SUPER_CHAT",
            "data": {"uname": "用户3", "message": "付费消息", "rmb": 10}
        }
    ]
    
    expected_messages = [
        "用户1 说: 消息1",
        "用户2 送出了 1 个 鲜花",
        "用户3 发送了付费聊天: 付费消息 (金额: 10元)"
    ]
    
    with patch('builtins.print') as mock_print:
        for msg in messages:
            await bili_client.handleMassage(msg)
    
    # 验证所有消息都被正确处理
    assert mock_print.call_count == 3
    assert mock_connect_server.emit.call_count == 3
    
    # 验证每个消息的内容
    for i, expected_msg in enumerate(expected_messages):
        mock_connect_server.emit.assert_any_call('chat_message', expected_msg)

@pytest.mark.asyncio
async def test_handle_message_with_special_characters(bili_client, mock_connect_server):
    """测试处理包含特殊字符的消息"""
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_DM",
        "data": {
            "uname": "测试用户🎉",
            "msg": "这是包含特殊字符的消息：😀🎊💖"
        }
    }
    
    with patch('builtins.print') as mock_print:
        await bili_client.handleMassage(resp_body)
    
    expected_msg = "测试用户🎉 说: 这是包含特殊字符的消息：😀🎊💖"
    mock_print.assert_called_with(f"[BiliClient] 收到消息: {expected_msg}")
    mock_connect_server.emit.assert_called_once_with('chat_message', expected_msg)

@pytest.mark.asyncio
async def test_handle_message_emit_failure(bili_client, mock_connect_server):
    """测试emit失败的情况"""
    # 模拟emit方法抛出异常
    mock_connect_server.emit.side_effect = Exception("连接失败")
    
    resp_body = {
        "cmd": "LIVE_OPEN_PLATFORM_DM",
        "data": {
            "uname": "测试用户",
            "msg": "测试消息"
        }
    }
    
    # 函数应该抛出异常，因为没有异常处理
    with pytest.raises(Exception, match="连接失败"):
        await bili_client.handleMassage(resp_body)


@pytest.fixture
def mock_connect_server():
    server = MagicMock(spec=AsyncServer)
    server.emit = AsyncMock()
    return server

@pytest.mark.asyncio
async def test_message_processing_workflow(mock_connect_server):
    """测试消息处理的完整工作流程"""
    bili_client = BiliClient(
        idCode="workflow_test",
        appId=54321,
        key="workflow_key",
        secret="workflow_secret",
        host="https://workflow.test.com",
        connect_server=mock_connect_server
    )
    
    # 模拟一系列真实的消息处理场景
    test_scenarios = [
        {
            "name": "新用户进入直播间发弹幕",
            "message": {
                "cmd": "LIVE_OPEN_PLATFORM_DM",
                "data": {"uname": "新用户123", "msg": "主播好！"}
            },
            "expected": "新用户123 说: 主播好！"
        },
        {
            "name": "用户送礼物",
            "message": {
                "cmd": "LIVE_OPEN_PLATFORM_SEND_GIFT",
                "data": {"uname": "土豪666", "gift_name": "跑车", "num": 1}
            },
            "expected": "土豪666 送出了 1 个 跑车"
        },
        {
            "name": "用户发送SC",
            "message": {
                "cmd": "LIVE_OPEN_PLATFORM_SUPER_CHAT",
                "data": {"uname": "支持者", "message": "主播加油！", "rmb": 50}
            },
            "expected": "支持者 发送了付费聊天: 主播加油！ (金额: 50元)"
        }
    ]
    
    with patch('builtins.print') as mock_print:
        for scenario in test_scenarios:
            await bili_client.handleMassage(scenario["message"])
    
    # 验证所有场景都被正确处理
    assert mock_connect_server.emit.call_count == len(test_scenarios)
    
    for scenario in test_scenarios:
        mock_connect_server.emit.assert_any_call('chat_message', scenario["expected"])
