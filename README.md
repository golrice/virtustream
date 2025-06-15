# VirtuStream - AI 虚拟主播系统

## 项目概述

VirtuStream 是一个基于人工智能的虚拟主播系统，整合了语音识别（STT）、自然语言处理（LLM）、语音合成（TTS）及虚拟形象渲染等技术，实现具备实时聊天交互、多模态内容输出和小游戏互动能力的虚拟主播解决方案。

## 主要功能

- 🎤 **实时语音交互**：通过STT/TTS实现自然语音对话
- 🎭 **表情动作同步**：根据对话内容驱动虚拟形象表情变化
- ♟️ **游戏互动**：支持观众通过弹幕参与国际象棋游戏
- 📺 **直播平台适配**：兼容Bilibili等主流直播平台
- 🚀 **模块化设计**：各功能组件可独立替换和扩展

## 技术架构

采用事件驱动架构（EDA）和分层设计：
- **交互层**：处理直播平台API和用户输入
- **业务层**：协调LLM、游戏等核心逻辑
- **模型层**：集成STT/TTS/虚拟形象等AI组件

## 快速开始

### 环境准备

- Python 3.10+
- [VTube Studio](https://denchisoft.com/)（虚拟形象控制）
- 直播姬（Bilibili直播客户端）

### 安装与运行

1. 克隆仓库：
   ```bash
   git clone https://github.com/your-repo/virtustream.git
   cd virtustream
   ```

2. 设置虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   复制`.env.template`为`.env`并填写您的API密钥：
   ```
   TTS_API_KEY=your_api_key
   LLM_API_KEY=your_api_key
   ```

4. 启动系统：
   ```bash
   python main.py
   ```

### Docker 部署
```bash
docker build -t virtustream .
docker run -p 8000:8000 virtustream
```

## 许可证

本项目采用 [MIT 许可证](LICENSE)

## 反馈与贡献

欢迎提交Issue或Pull Request！对于重大变更，请先开启讨论说明您计划进行的更改。

---

**提示**：首次使用前请确保已安装所有依赖项并正确配置API密钥。直播测试建议先在非公开环境下进行。