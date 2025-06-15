# 基础镜像：Python 3.10 轻量版
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录（包括 requirements.txt 和代码）
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 更新apt-get索引并安装supervisor
RUN apt-get update && apt-get install -y supervisor

# 复制supervisord配置文件到容器指定目录
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 启动容器时运行supervisord（前台模式）
CMD ["supervisord", "-n"]
