# 测试文档

| 版本号 | 日期       | 修改人 | 描述               |
| ------ | ---------- | ------ | ------------------ |
| 1.0    | 2025-04-27 | 利嘉烽 | 初版，确认基本需求 |

## 1. 测试框架

本项目采用 [`pytest`](https://docs.pytest.org/en/stable/) 作为测试框架，具有轻量、灵活、易用等优点。

* 依赖已在 `requirements.txt` 中声明，安装即可使用。
* 支持断言、测试夹具、参数化测试、插件扩展等高级功能。

---

## 2. 测试环境准备

确保已安装项目依赖并激活虚拟环境：

```bash
# 激活虚拟环境（以Linux为例）
source venv/bin/activate

# 安装依赖（包含pytest）
pip install -r requirements.txt
```

---

## 3. 测试代码组织规范

* 测试文件命名规则：`test_*.py` 或 `*_test.py`
* 测试函数命名规则：以 `test_` 开头
* 测试代码一般放在项目根目录的 `tests/` 文件夹中，和源代码分开管理。

示例目录结构：

```
virtustream/
│
├── llm/
├── stt.py
├── tts.py
├── signals.py
├── tests/
│   ├── test_add.py
│   ├── test_llm.py
│   └── test_tts.py
```

---

## 4. 编写测试用例示例

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

## 5. 运行测试

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

---

## 6. 常用命令参数

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

## 7. 生成测试报告

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

## 8. 质量保证

* 每个模块至少写覆盖其核心功能的单元测试。
* 新增功能必须配套新增测试用例。
* 定期在 CI 环境运行自动测试，保证代码质量。
* 合理使用断言，确保测试结果准确。

---

## 9. 测试用例

---

## 10. 缺陷跟踪
