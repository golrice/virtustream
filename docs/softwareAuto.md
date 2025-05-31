# 自动化文档

| 版本号 | 日期       | 修改人 | 描述               |
| ------ | ---------- | ------ | ------------------ |
| 1.0    | 2025-04-27 | 利嘉烽 | 初版，确认基本需求 |

---

## 1. 代码组织结构

```bash
virtustream/
│
├── main.py                # 主入口
├── llm/                   # LLM 封装模块
├── signals.py             # 事件总线实现
├── stt.py                 # 语音转文本
├── tts.py                 # 文本转语音
├── constant.py            # 常量定义
├── requirements.txt       # Python 依赖包列表
└── docs/                  # 文档目录
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

| 工具       | 用途           |
| ---------- | -------------- |
| VSCode     | 推荐开发编辑器 |
| `autopep8` | 代码自动格式化 |
| `pylint`   | 静态代码检查   |
| `pytest`   | 单元测试框架   |
| `loguru`   | 日志打印       |

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
```

---

### 3.3 合并流程（管理员或负责人操作）

```bash
git checkout main
git pull origin main # 获取最新的远端代码
git merge dev # 将本地的开发内容加入到main分支
git push origin main # 推送到远端
git checkout dev
git rebase main
```

---

## 4. 调试方式

### 4.1 本地运行

```bash
python outerServer.py
python main.py
```

确保所有模块通过 `if __name__ == "__main__":` 方式可独立运行调试。

### 4.2 日志输出建议

使用内置的`logging`模块代替一般的print需求，
将问题暴露在日志当中。

---

## 5. 自动化测试

使用 `pytest`：

### 5.1 安装

```bash
pip install pytest
```

### 5.2 编写测试

```python
# tests/test_basic.py

def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
```

### 5.3 运行测试

```bash
pytest
```

你也可以指定测试模块或函数：

```bash
pytest tests/test_basic.py::test_add
```

---

## 6. 持续集成（CI）

> 可选项，适用于团队合作和生产级自动化部署。

建议配置 GitHub Actions / GitLab CI 做以下工作：

* 自动运行 `pytest`，保证提交代码通过测试
* 使用 `black` 或 `flake8` 做代码风格检查
* 部署构建 docker 镜像或压缩包到服务器/云平台

📄 示例 GitHub Actions 工作流（`.github/workflows/python.yml`）：

```yaml
name: Python CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
```

---

## 7. 运行部署建议（非正式）

建议后期整理部署手册，内容可包含：

* docker-compose 启动多个模块（SocketIO、LLM、TTS）
* 使用 supervisor 管理后台服务
* 模块部署拓扑图（可参考物理视图）
* 模块健康检查和日志收集脚本

---

