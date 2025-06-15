import pytest
import logging
from unittest.mock import MagicMock
from modules.game import Game
import random
MAX_MESSAGES_LEN = 10  
def generate_chess_command():
    # 生成两个小写字母
    letters = [random.choice('abcdefgh') for _ in range(2)]
    # 生成两个数字（1-8）
    numbers = [str(random.randint(1, 8)) for _ in range(2)]
    # 组合成坐标对
    coords = f"{letters[0]}{numbers[0]}{letters[1]}{numbers[1]}"
    # 构建完整字符串
    return f"请这样下棋:{coords}",coords
def generate_wrong_command():
    # 生成两个小写字母
    letters = [random.choice('ijklmnopqrstuvwxyz') for _ in range(2)]
    # 生成两个数字（1-8）
    numbers = [random.choice('09') for _ in range(2)]
    # 组合成坐标对
    coords = f"{letters[0]}{numbers[0]}{letters[1]}{numbers[1]}"
    # 构建完整字符串
    return f"请这样下棋:{coords}",coords
@pytest.mark.asyncio
async def test_correct_order(monkeypatch):
    # 模拟 recentMessages 属性
    mock_signals = MagicMock()
    mock_signals.recentMessages = []

    logger = logging.getLogger("test_game")

    game = Game(mock_signals, enable=True)

    handler = game._io.handlers['/']['chat_message']
    await handler("xx用户：请这样下棋：a1a2")
    assert game.step_from_user == ["a1a2"]
    assert mock_signals.recentMessages == []
    game.step_from_user.clear()

    for i  in range(50):
        order,Str = generate_chess_command()
        await handler(order)
        assert game.step_from_user == [Str]
        assert mock_signals.recentMessages == []
        game.step_from_user.clear()

@pytest.mark.asyncio
async def test_wrong_order():
    mock_signals = MagicMock()
    mock_signals.recentMessages = []

    logger = logging.getLogger("test")
    game = Game(mock_signals, enable=True)

    handler = game._io.handlers['/']['chat_message']
    await handler("请这样下棋：")

    assert mock_signals.recentMessages == ['用户使用了错误的指令，可以告诉他们正确的使用样例是：请这样下棋：a1a2\n']
    assert game.step_from_user == []
    mock_signals.recentMessages.clear()

    await handler("a1a2")
    assert mock_signals.recentMessages == ['用户使用了错误的指令，可以告诉他们正确的使用样例是：请这样下棋：a1a2\n']
    assert game.step_from_user == []

    mock_signals.recentMessages.clear()
    for i in range(50):
        order,Str = generate_wrong_command()
        await handler(order)
        assert game.step_from_user == []
        assert mock_signals.recentMessages == ["用户使用了超出棋盘范围的坐标，可以调侃观众：棋子飞出棋盘啦，飞出棋盘的棋子记得放到盖子里哦~"]
        mock_signals.recentMessages.clear()
