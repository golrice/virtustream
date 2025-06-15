# 测试文档

| 版本号 | 日期       | 修改人 | 描述               |
| ------ | ---------- | ------ | ------------------ |
| 1.0    | 2025-04-27 | 利嘉烽 | 初版，确认基本需求 |
| 2.0    | 2025-06-02 | 张宇晨 | 添加TTS,LLM模块测试日志 |
| 3.0    | 2025-06-03 | 吴阳天朗 |添加VTuber模块测试日志|
| 4.0    | 2025-06-05 | 王祎铭 | 添加B站API直播房间管理测试(room_manager)和ProtoBuf协议日志   |
| 5.0    | 2025-06-08 | 李源卿 | 添加game模块(lichess-bot)测试日志 |
| 6.0    | 2025-06-10 | 利嘉烽 | 添加client和signals总线管理调度层测试日志|
| 7.0    | 2025-06-14 | 张宇晨 | 整理测试文档和集成测试 |
## 0.项目信息
- 项目名称：VirtuStream
- 测试时间：2025-06-11
- 测试环境：Windows 11
- Python版本：3.9


## 1. 测试指引

本项目采用 [`pytest`](https://docs.pytest.org/en/stable/) 作为测试框架，具有轻量、灵活、易用等优点。

在各自进行相对独立的模块测试时,也可以使用python自带的unittest进行单元模块测试。

* 依赖已在 `requirements.txt` 中声明，安装即可使用。
* 支持断言、测试夹具、参数化测试、插件扩展等高级功能。

---

### 1.1 测试环境准备

确保已安装项目依赖并激活虚拟环境：

```bash
# 激活虚拟环境（以Linux为例）
source venv/bin/activate

# 安装依赖（包含pytest）
pip install -r requirements.txt
```

---

## 1.2 测试代码组织规范

* 测试文件命名规则：`test_*.py` 或 `*_test.py`
* 测试函数命名规则：以 `test_` 开头
* 测试代码一般放在项目根目录的 `tests/` 文件夹中，和源代码分开管理。

目录结构：

```
virtustream/
│
├── docs/
│   └── test.md   # 测试文档
├── tests/
│   ├── test_client.py                  # client模块测试
│   ├── test_textLLMWraper.py           # 文本LLM模块测试
│   ├── test_vtuber.py                  # VTuber模块测试
│   ├── test_tts.py                     # TTS模块测试
|   ├── test_game.py                    # 游戏game模块测试
|   ├── test_room_manager.py            # bilibili直播房间管理测试
│   ├── test_proto.py                   # ProtoBuf协议测试
│   └── test_integration.py             # 集成测试
└── README.md
```

---

### 1.3 编写测试用例示例

```python
# tests/test_add.py

def add(x, y):
    return x + y

def test_add_positive():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, -1) == -2
```

* `assert` 用于断言期望结果与实际结果相等。
* 失败时，pytest 会输出详细的错误信息，方便定位问题。

---

### 1.4 运行测试

进入项目根目录，执行：

```bash
pytest
```

默认会自动查找所有 `test_*.py` 文件并执行其中所有以 `test_` 开头的函数。

你也可以指定运行某个测试文件或某个测试函数：

```bash
pytest tests/test_add.py
pytest tests/test_add.py::test_add_positive
```
或者
```bash
python -m unittest tests/test_tts.py
``` 
在运行`test/`目录下的测试用例时,提前在命令行中声明:
```bash
$env:PYTHONPATH = "your_project_root_dir;$env:PYTHONPATH"  #将your_project_root_dir替换为你的项目根目录
```
---

### 1.5 常用命令参数

| 参数                 | 作用                                |
| -------------------- | ----------------------------------- |
| `-v` / `--verbose`   | 显示更详细的测试过程信息            |
| `-q` / `--quiet`     | 安静模式，只输出简要结果            |
| `--maxfail=N`        | 测试失败时最多显示 N 个失败信息     |
| `--tb=short`         | 简短错误回溯信息                    |
| `--disable-warnings` | 禁用警告输出                        |
| `--capture=no`       | 不捕获输出，适合调试时查看print内容 |

示例：

```bash
pytest -v --maxfail=3 --tb=short
```

---

### 1.6 生成测试报告

* 可集成插件 [`pytest-html`](https://pytest-html.readthedocs.io/en/latest/) 生成 HTML 格式测试报告。
* 安装：

```bash
pip install pytest-html
```

* 运行并生成报告：

```bash
pytest --html=report.html
```

报告会保存为 `report.html`，双击浏览器打开即可查看测试结果的详细图形化界面。

---

### 1.7 质量保证

* 每个模块至少写覆盖其核心功能的单元测试。
* 新增功能必须配套新增测试用例。
* 定期在 CI 环境运行自动测试，保证代码质量。
* 合理使用断言，确保测试结果准确。

---

## 2. 模块单元测试

### 2.1 TTS模块测试
#### 测试目的
验证TTS模块的功能完整性和稳定性，确保文本转语音功能正常工作。
#### 测试计划
- WebSocket连接管理
- 文本转语音功能
- 音频播放功能
- 错误处理机制

#### 测试用例
代码详见 `tests/test_tts.py`

| 用例ID | 测试项 | 输入 | 预期输出 | 验证点 |
|--------|--------|------|-----------|--------|
| TTS-001| 初始化 | TTS类实例化 | 成功创建实例 | 配置加载正确 |
| TTS-002| URL生成 | 调用_create_url() | 返回有效URL | URL格式正确 |
| TTS-003| 空文本处理 | text_to_speech("") | 返回空数组 | 边界条件处理 |

#### 执行方法
```bash
python -m unittest tests/test_tts.py -v
```
#### 测试结果
```bash
test_create_url (__main__.TestTTS.test_create_url)                                              
测试WebSocket URL生成 ... ok
test_ensure_ws_connection (__main__.TestTTS.test_ensure_ws_connection)
测试WebSocket连接确保机制 ... ok
test_error_handling (__main__.TestTTS.test_error_handling)
测试错误处理 ... 2025-06-15 14:02:23 | ERROR | tts | WebSocket错误: 测试错误
WebSocket错误: 测试错误
ok
test_init (__main__.TestTTS.test_init)
测试TTS类初始化 ... ok
test_on_message_handling (__main__.TestTTS.test_on_message_handling)
测试WebSocket消息处理 ... 2025-06-15 14:02:23 | INFO | tts | tts parsing message
ok
test_process_queue (__main__.TestTTS.test_process_queue)
测试消息队列处理 ... ok
test_text_to_speech (__main__.TestTTS.test_text_to_speech)
测试文本转语音功能 ... 2025-06-15 14:02:23 | INFO | tts | tts trying
2025-06-15 14:02:24 | INFO | tts | WebSocket连接已建立
2025-06-15 14:02:24 | INFO | tts | tts checking
2025-06-15 14:02:24 | INFO | tts | tts collecting
2025-06-15 14:02:24 | INFO | tts | tts parsing message
2025-06-15 14:02:24 | INFO | tts | tts parsing message
2025-06-15 14:02:24 | INFO | tts | tts parsing message
2025-06-15 14:02:24 | INFO | tts | tts parsing message
2025-06-15 14:02:24 | INFO | tts | WebSocket连接关闭
2025-06-15 14:02:24 | INFO | tts | tts trying
2025-06-15 14:02:24 | INFO | tts | WebSocket连接已建立
2025-06-15 14:02:24 | INFO | tts | tts checking
2025-06-15 14:02:24 | INFO | tts | tts collecting
2025-06-15 14:02:25 | INFO | tts | tts parsing message
2025-06-15 14:02:25 | ERROR | tts | 合成失败: 10907, tts text len is 0;code=10109
2025-06-15 14:02:30 | INFO | tts | WebSocket连接关闭
2025-06-15 14:02:39 | ERROR | tts | 等待音频数据超时
ok

----------------------------------------------------------------------
Ran 7 tests in 16.095s

OK
```

### 2.2 Client客户端模块测试
#### 测试目的
客⼾端内容client测试主要是处理聊天消息的事件处理逻辑，包括消息⻓度限制、消息存储等。
#### 测试计划
* 聊天消息⻓度限制：超过限制的消息会被丢弃，未超过限制的消息会被存储。
* 聊天消息存储：测试消息存储是否符合预期。
#### 测试用例
代码详见 `tests/test_client.py`
| 用例ID | 测试项 | 输入 | 预期输出 | 验证点 |
|--------|--------|------|-----------|--------|
| CLI-001| 消息处理(未达上限) | chat_message事件{"msg": "hello"} | recentMessages新增消息 | 消息正确添加到列表 |
| CLI-002| 消息处理(达到上限) | chat_message事件{"msg": "new"} | 最早消息被移除，新消息添加到末尾 | 消息队列长度维持在上限以内 |
#### 执行方法
```bash
pytest tests/test_client.py -v
```
#### 测试结果
```bash
===================================== test session starts =====================================
platform win32 -- Python 3.12.5, pytest-8.3.5, pluggy-1.6.0 -- E:\virtustream\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\virtustream
plugins: anyio-4.9.0, hydra-core-1.3.2
collected 2 items                                                                              

tests/test_client.py::test_chat_message_under_limit SKIPPED (async def function and ...) [ 50%] 
tests/test_client.py::test_chat_message_over_limit SKIPPED (async def function and n...) [100%] 
```
### 2.3 LLM模块测试

#### 测试目的
textLLMWrapper测试主要是处理⽂本⽣成模块的事件处理逻辑，包括模块加载、模块注⼊、模块清理
等。
#### 测试计划
* 模块加载：测试模块加载是否符合预期。
* 模块注⼊：测试模块注⼊是否符合预期。
* 模块清理：测试模块清理是否符合预期。
#### 测试用例
代码详见 `tests/test_textLLMWrapper.py`
#### 测试用例
| 用例ID | 测试项 | 输入 | 预期输出 | 验证点 |
|--------|--------|------|-----------|--------|
| LLM-001 | 空模块注入 | 无模块的 LLM 实例 | 空列表 [] | 确保无模块时正确处理 |
| LLM-002 | 多模块注入排序 | 两个优先级不同的模块注入 (priority=1,2) | 按优先级排序的注入列表 | 1. 注入正确排序<br>2. cleanup()被调用 |
| LLM-003 | 低优先级过滤 | priority=-1的模块注入 | 空列表 [] | 正确过滤低优先级注入 |
| LLM-004 | 外部注入合并 | 1个模块注入+1个外部注入 | 合并后的有序注入列表 | 外部注入正确合并并排序 |
#### 执行方法
```bash
pytest tests/test_textLLMWrapper.py -v
```
#### 测试结果
```bash
===================================== test session starts =====================================
platform win32 -- Python 3.12.5, pytest-8.3.5, pluggy-1.6.0 -- E:\virtustream\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\virtustream
plugins: anyio-4.9.0, hydra-core-1.3.2
collected 4 items                                                                              

tests/test_textLLMWrapper.py::test_assemble_injections_with_no_modules PASSED            [ 25%]
tests/test_textLLMWrapper.py::test_assemble_injections_with_modules PASSED               [ 50%]
tests/test_textLLMWrapper.py::test_assemble_injections_filters_low_priority PASSED       [ 75%]
tests/test_textLLMWrapper.py::test_assemble_injections_with_external_injections PASSED   [100%]

====================================== 4 passed in 3.25s ======================================
```

### 2.4 VTuber模块测试
#### 测试目的
测试针对模块是虚拟 ai 主播的 vtuber 模型控制模块。这个模块
包含两个核心功能，第一个是常运行的无输入循环，用来不停的随
机播放制作好的动作组，这些多样的动作可以看起来 vtuber 像一个
真正的人一样晃动，另一个模块用来接收服务器的大模型传来的表
情标签，监听它并且控制 vtuber 做出对应的表情。这个插件通过
vtuber studio 提供的 api 来控制 vtuber。同时这个项目模块包含了
很多的 live2D 模型动作组和一些参数设置。
本计划主要针对两个核心功能能否自然运行，动作是否流畅以
及两个核心功能配合是否恰当。
#### 测试计划
软件需求：vtuber studio
测试环境：python windows/linux
基本计划：对于第一个核心功能只需要常运行并持续观察一段时间即可，主要观察模型运动是流畅，模型网络连接及操控是否稳定。第二个核心功能需要编写一系列信号模拟来观察表情反应是否正确，最后两种共同运行观察适配情况。
测试方案:
1. 模型动作操控：常运行 10 分钟，观察模型状态及网络连接情况。最后观察模块能否检测信号组中的终止信号结束。
2. 模型表情操控：编写时长十分钟的信号组。信号中有两种主要信号，即模型是否在说话，以及当前表情。这个信号组要尽可能模拟真实场景并能够测试一些特殊情况，如一句话多个表情，服务器信号延迟等。
3. 核心功能适配：上述两个测试方案在两个线程中共同运行，观察动作与表情适配情况。

#### 测试用例
| 用例ID | 测试项 | 输入 | 预期输出 | 验证点 |
|--------|--------|------|-----------|--------|
| VTB-001| VTuber表情状态转换 | 1. 坏笑表情<br>2. speaking=True<br>3. 等待7秒<br>4. 生气表情 | 1. 正确切换表情<br>2. 说话状态正确同步 | 1. 表情切换正确性<br>2. 说话状态同步<br>3. 时序正确 |
| VTB-002| VTuber持续对话测试 | 连续三组表情和说话状态变化：<br>1. 坏笑->生气<br>2. 高兴->无语<br>3. 害羞 | 1. 每组表情正确切换<br>2. 说话状态正确切换<br>3. 持续约90秒 | 1. 长时间稳定性<br>2. 状态切换准确性<br>3. 线程同步正确性 |
| VTB-003| VTuber资源清理 | 发送终止信号 | 1. 所有线程正常退出<br>2. 资源正确释放 | 1. 线程清理完整性<br>2. 退出过程正确性 |
#### 执行方法
注意:在本地运行`tests/test_vtuber.py`文件时,开始测试后要立即进入vtuber studio中同意两次插件接入!
#### 测试结果
结果:
* 动作操控模块：十分钟内 api 控制连接稳定，没有断开。模型动作较为真实流畅。
* 表情操控模块：表情反应正确，但是表情之间区别度不高，且如果一段时间没有表情信号更新，连接容易断开。
* 两种模块适配：当某种表情热键播放时播放了某种待机动作时，参数重叠部分会导致控制冲突，导致表情被覆盖。
  
原因分析：
* 表情区别度不高：模型是免费开源模型，身体控制参数不多 ，表情积极度不高时看起来较为相似。
* 连接断开：一段时间内可能模型没有说话，这时候 api 网络连接可能一段时间不会有交互，vts 可能会判定为连接断开。
* 参数冲突：动作和表情均通过热键控制，参数覆盖与播放先后有关，当参数冲突时就会被覆盖。
  
改进方案：
* 表情区别度不高：找一些小挂件比如生气时的脑袋上的“囧”符号，当表情播放时一同现实。
* 连接断开：每段时间固定传输一些确认连接的信息保持网络连接。
### 2.5 Game模块测试
#### 测试目的
* 接口实现正确性：验证 Game 模块所需的接口均已按照设计要求正确实现，可以正确响应用户输入的指令，推动游戏流程顺利进行或执行相应操作。
* 运行稳定性：确保 Game 模块在不同的测试环境和多种场景下，均能保持稳定运行，不会出现异常崩溃、卡顿或无响应等情况。
* 低故障率：保证模块在正常使用过程中，出现的问题和缺陷处于可接受的范围之内，不存在严重影响游戏体验或导致游戏无法正常进行的重大 bug。
#### 测试计划
测试工具和运行环境
* 运行环境： Windows 10
* 测试工具： pytest +人工
  
测试方法
* 由于该 Game 模块是通过调用第三方软件的API来匹配对手和游玩，所以有大部分的测试无法使用程序进行，只能登录第三方网站查看游戏的实际情况，观察实际情况是否和用户命令一致；同时观察游戏的实际情况和回传给LLM的信息是否匹配
* 部分前端的处理（如非用户指令过滤）可以使用 pytest 来测试
#### 测试用例
代码详见 `tests/test_game.py`
| 用例ID | 测试项 | 输入 | 预期输出 | 验证点 |
|--------|--------|------|-----------|--------|
| GAME-001 | 正确棋步指令 | 1. "xx用户：请这样下棋：a1a2"<br>2. 50次随机合法坐标指令 | 1. step_from_user=["a1a2"]<br>2. recentMessages=[]<br>3. 每次随机指令都被正确记录 | 1. 指令解析正确性<br>2. 合法坐标识别<br>3. 状态更新准确性 |
| GAME-002 | 错误棋步指令 | 1. "请这样下棋："<br>2. "a1a2"<br>3. 50次随机非法坐标指令 | 1. step_from_user=[]<br>2. recentMessages包含错误提示<br>3. 超出范围提示正确 | 1. 错误指令处理<br>2. 提示信息正确<br>3. 非法坐标检测 |
#### 执行方法
```bash
pytest tests/test_game.py -v
```
#### 测试结果
```bash
(venv) PS C:\Users\31169\Desktop\SFHW\virtustream> pytest tests/test_game.py
C:\Users\31169\Desktop\SFHW\venv\Lib\site-packages\pytest_asyncio\plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"
 "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
====================================================================== test session starts ======================================================================= 
platform win32 -- Python 3.11.2, pytest-8.3.5, pluggy-1.6.0
rootdir: C:\Users\31169\Desktop\SFHW\virtustream
plugins: anyio-4.9.0, hydra-core-1.3.2, asyncio-1.0.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items                                                                                                                                                  

tests\test_game.py ..                                                                                                                                       [100%] 

======================================================================= 2 passed in 0.50s ===============================
```
### 2.6 ProtoBuf协议测试
#### 测试目的
验证 ProtoBuf 协议的序列化和反序列化功能是否正常，确保数据传输的正确性和效率。
#### 测试计划
- 测试包头解析
- 测试包体长度限制  
#### 测试用例
代码详见 `tests/test_proto.py`
#### 测试用例
| 用例ID | 测试项 | 输入 | 预期输出 | 验证点 |
|--------|--------|------|-----------|--------|
| PROTO-001 | 有效数据包解包 | packet_len=20<br>header_len=16<br>ver=0<br>op=1<br>seq=123<br>body="test" | 1. 正确解析所有字段<br>2. 调用回调函数 | 1. 字段值正确性<br>2. 回调函数执行 |
| PROTO-002 | 包头长度不足 | buf=b'short'<br>(小于16字节) | 打印错误信息："包头不够" | 包头长度检查机制 |
| PROTO-003 | 无效包长度 | packet_len=3000<br>(超过maxBody) | 打印错误信息：<br>"包体长不对 packetLen:3000 maxBody:2048" | 包体长度限制检查 |
| PROTO-004 | 负数包长度 | packet_len=-1 | 打印错误信息：<br>"包体长不对 packetLen:-1 maxBody:2048" | 负数长度处理 |
| PROTO-005 | 空body处理 | packet_len=16<br>(仅包头) | body=b''<br>(空字节数组) | 空包体处理机制 |
| PROTO-006 | 非零版本号 | ver=1<br>(非0版本) | 1. 正确解析字段<br>2. 不调用回调函数 | 版本兼容性处理 |
#### 执行方法
```bash
pytest tests/test_proto.py -v
```
#### 测试结果
```bash
===================================== test session starts =====================================
platform win32 -- Python 3.12.5, pytest-8.3.5, pluggy-1.6.0 -- E:\virtustream\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\virtustream
plugins: anyio-4.9.0, hydra-core-1.3.2
collected 6 items                                                                              

tests/test_proto.py::test_proto_unpack_valid_packet PASSED                               [ 16%] 
tests/test_proto.py::test_proto_unpack_insufficient_header PASSED                        [ 33%] 
tests/test_proto.py::test_proto_unpack_invalid_packet_length PASSED                      [ 50%] 
tests/test_proto.py::test_proto_unpack_negative_packet_length PASSED                     [ 66%] 
tests/test_proto.py::test_proto_unpack_empty_body PASSED                                 [ 83%] 
tests/test_proto.py::test_proto_unpack_version_not_zero PASSED                           [100%]

====================================== 6 passed in 0.08s ====================================== 
```
### 2.7 BilibiliAPI直播房间管理测试
#### 测试目的
针对AI虚拟主播与直播平台的连接模块，包括直播数据流上⾏以及直播平台直播间信息下⾏的功能模块。验证直播间数据获取模块能够：
1. 正确连接B站直播接⼝并获取实时数据
2. 准确解析弹幕、礼物等不同消息类型
3. 可靠地将解析后的事件分发给监视器
4. 处理各种异常情况（⽹络中断、数据格式异常等）
#### 测试计划
1. 直播信息获取，包括直播间基本信息，弹幕评论信息以及礼物信息等
2. 直播推流功能，测试推流是否成功进⾏。

测试方案:总体测试⽅案即使⽤真实测试环境，将本项⽬连接到为本项⽬准备的具体直播间，并使⽤其他账号进⾏常规直播间交互模拟，具体⽅案如下：
1. 在真实直播环境下，测试该模块是否可以正确获取并输出直播间基本信息。
2. 使⽤其他账号测试输入弹幕，发送礼物，查看控制台是否返回正确信息。
3. 使⽤突然断⽹并重连⽅案，测试该监视模块是否可以⾃动恢复以及正确汇报错误。
4. 模拟直播，测试推流软件是否可以正常使⽤

测试环境:
直播平台： Bilibili直播 开发语⾔： python 推流⼯具： OBS Studio 直播⼯具： Bilibili直播姬 测试平台： Bilibili⽹⻚版
#### 测试用例
代码详见 `tests/test_room_manager.py`
#### 执行方法
```bash
pytest tests/test_room_manager.py -v
```
#### 测试结果
```bash
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
============================================================= test session starts ==============================================================
platform linux -- Python 3.10.15, pytest-8.3.5, pluggy-1.6.0 -- /home/golrice/projects/homework/virtustream/venv/bin/python
cachedir: .pytest_cache
metadata: {'Python': '3.10.15', 'Platform': 'Linux-6.6.87.1-microsoft-standard-WSL2-x86_64-with-glibc2.39', 'Packages': {'pytest': '8.3.5', 'pluggy': '1.6.0'}, 'Plugins': {'html': '4.1.1', 'metadata': '3.1.1', 'asyncio': '1.0.0', 'hydra-core': '1.3.2', 'anyio': '4.9.0'}}
rootdir: /home/golrice/projects/homework/virtustream
plugins: html-4.1.1, metadata-3.1.1, asyncio-1.0.0, hydra-core-1.3.2, anyio-4.9.0
asyncio: mode=strict, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 11 items

tests/test_room_manager.py::test_handle_dm_message PASSED                                                                                [  9%]
tests/test_room_manager.py::test_handle_gift_message PASSED                                                                              [ 18%]
tests/test_room_manager.py::test_handle_super_chat_message PASSED                                                                        [ 27%]
tests/test_room_manager.py::test_handle_guard_message PASSED                                                                             [ 36%]
tests/test_room_manager.py::test_handle_unknown_message PASSED                                                                           [ 45%]
tests/test_room_manager.py::te
```
## 3. 集成测试
#### 测试目的
#### 测试计划
#### 测试用例
#### 执行方法
#### 测试结果







## 4. 维护说明

### 4.1 测试用例维护
- 定期更新测试用例
- 及时添加新功能测试
- 保持测试文档同步

### 4.2 问题追踪
使用 GitHub Issues 追踪问题：
- 标签：bug, enhancement, test
- 优先级：high, medium, low
- 状态：open, in progress, resolved