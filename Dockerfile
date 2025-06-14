FROM python:3.10-slim

WORKDIR /app
COPY . .  # 拷贝 requirements.txt 和代码

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run_all.py"]
