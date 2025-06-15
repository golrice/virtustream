# 自动化文档

| 版本号 | 日期       | 修改人 | 描述                           |
| ------ | ---------- | ------ | ------------------------------ |
| 1.0    | 2025-04-27 | 利嘉烽 | 初版，确认基本需求             |
| 2.0    | 2025-05-21 | 利嘉烽 | 完善开发过程所需内容、便于开发 |
| 2.1    | 2025-06-14 | 利嘉烽 | 修正部分错误内容               |

---

## 1. 代码组织结构

```bash
virtustream/
├── LLM/                # 语言模型
├── README.md           # 说明文档
├── assets              # 资源
├── constant.py         # 静态常量
├── docs                # 说明文档
├── lichess-bot         # 棋类游戏
├── main.py             # 程序主入口
├── modules             # 扩展模块
├── outerServer.py      # 直播平台交互
├── prompter.py         # 管理模型使用、提示词使用
├── proto.py            # 直播协议
├── requirements.txt    # 项目依赖项
├── room_manager.py     # 直播房间管理
├── room_manager.spec   # 直播房间管理
├── signals.py          # 共享信号量
├── stt.py              # 语音转文字
├── tests               # 测试文件夹
├── tts.py              # 文字转语音
├── utils.py            # 工具类
└── venv                # 虚拟环境
```

---

## 2. 开发环境配置

* Python 版本：`3.10+`
* 包管理工具：`pip`
* 虚拟环境：`venv`

### 虚拟环境搭建

```bash
# Linux / Mac
cd virtustream
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
# Windows
cd virtustream
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 常用开发工具

| 工具      | 用途           |
| --------- | -------------- |
| VSCode    | 推荐开发编辑器 |
| `pylint`  | 静态代码检查   |
| `pytest`  | 单元测试框架   |
| `logging` | 日志打印       |

---

## 3. Git 协作流程

> **严禁使用 `git push -f`，除非在个人分支、明确知晓风险**

### 3.1 克隆代码库

```bash
git clone <repo_url>
cd virtustream
```

或使用 GitHub Fork 工作流：

1. Fork 项目仓库
2. 在 Fork 仓库上开发功能
3. 提交 Pull Request 合并到主仓库

---

### 3.2 日常开发流程（开发分支）

```bash
git checkout -b dev   # 创建分支
# 修改代码...
git add .
git commit -m "feat: xxx"
git push origin dev:feature_xxx
```

---

### 3.3 合并流程（管理员或负责人操作）

```bash
git checkout dev
git fetch origin # 获取最新远端代码
git merge feature_xxx # 将某个分支的更新进行合并
git checkout main
git merge dev # 将刚才所有的合并都集中为一次合并到main中
git push origin main # 将合并推送到主分支
```

---

## 4. 调试方式

### 4.1 本地运行

```bash
python outerServer.py
python main.py
python ./lichess-bot/lichess-bot.py # 可选
```

确保所有模块通过 `if __name__ == "__main__":` 方式可独立运行调试。

### 4.2 日志输出建议

使用内置的`logging`模块代替一般的print需求，
将问题暴露在日志当中。

通过封装好的一个`get_logger`函数，可以保证每一个子模块都有单独的日志写入器。
这样每个模块都可以单独输出日志，快速找到问题所在。

```py
def get_logger(name: str = "default", level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger  

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, f"{name}.log"),
        when="midnight",
        interval=1,
        backupCount=7,  
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False  
    return logger
```

---

## 5. 自动化测试

使用 `pytest`：

### 5.1 安装

```bash
pip install pytest
```

### 5.2 编写测试

使用 `pytest` 编写测试用例时，遵循以下**四个简洁明了的基本原则**：

#### **测试函数命名以 `test_` 开头**

```python
def test_add():
    assert add(1, 2) == 3
```

- 这样 pytest 才能自动发现和运行它。

#### **使用 `assert` 断言**

```python
def test_uppercase():
    assert "hello".upper() == "HELLO"
```

- `pytest` 会自动展示断言失败的对比信息，不需要用 `unittest` 那套繁琐的 `self.assertEqual()`。

#### **保持测试独立，无副作用**

* 每个测试应**独立运行、不依赖其他测试或外部状态**。
* 可通过 `pytest` 的 fixture 实现隔离和资源管理。

```python
import pytest

@pytest.fixture
def sample_dict():
    return {"key": "value"}

def test_dict_access(sample_dict):
    assert sample_dict["key"] == "value"
```

#### **可读性优先，按“准备-执行-断言”结构**

```python
def test_discount_calculation():
    # 准备
    price = 100
    discount = 0.2

    # 执行
    final_price = price * (1 - discount)

    # 断言
    assert final_price == 80
```

#### 具体实例展示

```python
# tests/test_textLLMWrapper.py
@pytest.mark.asyncio
async def test_chat_message_over_limit():
    mock_signals = MagicMock()
    mock_signals.recentMessages = [{"msg": f"m{i}"} for i in range(MAX_MESSAGES_LEN)]

    logger = logging.getLogger("test")
    client = Client(mock_signals, enable=True, logger=logger)

    handler = client._io.handlers['/']['chat_message']
    await handler({"msg": "new"})

    # 最早的消息被踢出，最新的消息在末尾
    assert mock_signals.recentMessages == [{"msg": f"m{i}"} for i in range(1, MAX_MESSAGES_LEN)] + [{"msg": "new"}]
```

### 5.3 运行测试

```bash
pytest
```

也可以指定测试模块或函数：

```bash
pytest tests/test_textLLMWrapper.py::test_chat_message_over_limit
```

---

## 6. 持续集成（CI）

配置 GitHub Actions。
自动运行 `pytest`，保证提交代码通过测试。

```yaml
name: Run Pytest on Push

on: [push, pull_request]  # 触发条件：push 或 PR 时触发

jobs:
  test:
    runs-on: ubuntu-latest  # 在 GitHub 提供的 Ubuntu 虚拟机中运行

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3  # 拉取代码仓库

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'  

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests with pytest
      run: pytest  # 运行测试用例
```