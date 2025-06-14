#!/bin/bash

# 设置变量
APP_NAME="myapp"
IMAGE_NAME="myapp:latest"
CONTAINER_NAME="myapp_container"

echo "正在构建 Docker 镜像..."
docker build -t $IMAGE_NAME .

# 停止并删除旧容器
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    echo " 正在清理旧容器..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

#项目运行要与其他软件同时运行并操作
echo "正在启动新容器..."
docker run -d --name $CONTAINER_NAME -p 8000:8000 $IMAGE_NAME
