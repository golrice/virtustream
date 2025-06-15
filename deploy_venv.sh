#!/bin/bash

# 设置变量
VENV_DIR="venv"

echo "检查虚拟环境..."
if [ ! -d "$VENV_DIR" ]; then
    echo "创建新的 venv 环境..."
    python3 -m venv $VENV_DIR
fi

source venv/bin/activate

echo "安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

#项目运行要与其他软件同时运行并操作

 
