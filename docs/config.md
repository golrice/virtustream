# 软件配置与运维文档

| 版本号 | 日期       | 修改人 | 说明     |
| ------ | ---------- | ------ | -------- |
| 1.0    | 2025-04-28 | 利嘉烽 | 初版整理 |
| 2.0    | 2025-06-14 | 吴阳天朗 | 完善文档 |

---

## 目录

1. 配置管理
2. 版本控制策略
3. 持续集成（CI）
4. 部署策略
5. 运维计划
6. 监控与日志
7. 故障应急与备份
8. 安全性管理

---

## 1. 配置管理

### 1.1 配置分类

| 配置类型      | 描述                              | 存储位置           |
| ------------- | --------------------------------- | ------------------ |
| 应用配置      | 各模块运行所需参数                | `config.yaml`      |
| 环境变量      | 数据库连接、密钥、Token等敏感数据 | `.env`             |
| 第三方依赖    | 所有Python库依赖项                | `requirements.txt` |
| 模型/资源路径 | 本地模型文件或在线链接            | `constants.py`     |

### 1.2 配置管理工具

* 使用 `.env` 文件管理开发环境配置，避免硬编码敏感信息。
* 引入 `pydantic` 或 `dynaconf` 统一管理配置读取与校验。

---

## 2. 版本控制策略

### 2.1 Git分支规范

| 分支名      | 用途                           |
| ----------- | ------------------------------ |
| `main`      | 稳定版本，部署用               |
| `dev`       | 主开发分支                     |
| `feature/*` | 新功能开发（每个功能一个分支） |
| `hotfix/*`  | 紧急修复                       |

### 2.2 提交规范

* 使用 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
* 示例：

```
feat(tts): 新增语音缓存机制
fix(stt): 修复语音识别中的重复字
docs: 更新README
```

### 2.3 标签和发布说明

* 每次发布打 Git Tag，例如 `v1.2.0`
* 使用 `CHANGELOG.md` 记录版本变更

---

## 3. 持续集成（CI）

### 3.1 工具

* GitHub Actions 

### 3.2 自动化流程建议

每次 `push` 或 `pull_request` 触发：

1. 安装依赖环境
2. 运行单元测试（pytest）
3. 运行代码检查

### 3.3 GitHub Actions 配置

`.github/workflows/ci.yml`:

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

---

## 4. 部署策略

### 4.1 部署环境

| 环境     | 描述        | 地址             |
| -------- | ----------- | ---------------- |
| 开发环境 | 本地  | localhost        |
| 测试环境 | CI 自动部署/本地 | localhost |
| 生产环境 | 本地    | localhost |

### 4.2 部署方式

* Docker 镜像部署（推荐）：

  * 本地构建：`docker build -t myapp:latest .`
  * 启动容器：`docker run -p 8000:8000 myapp`
* 使用自动部署脚本部署： `deploy_venv.sh`,`deploy_docker.sh`
* 支持使用 `docker-compose` 或 Kubernetes 进行多服务编排
* 若使用 PaaS（如 Railway、Heroku、Aliyun FC）请参照对应平台文档

---

## 5. 运维计划

### 5.1 日常任务

| 任务     | 周期      | 负责人 | 工具/说明        |
| -------- | --------- | ------ | ---------------- |
| 健康检查 | 每日      | 吴阳天朗   | curl, Prometheus |
| 日志查看 | 实时/每日 | 利嘉峰   | ELK / Logtail    |
| 性能分析 | 每周      | 张宇晨   | Grafana / py-spy |
| 数据备份 | 每日      | 自动   | rsync / cronjob  |

### 5.2 升级与回滚

* 使用 Docker 镜像版本控制部署
* 新镜像上线前保留旧容器，不直接清理
* 发生故障时快速切换旧版本：`docker tag old backup && docker run old`
* 自动回滚触发器：通过健康检查失败次数触发 rollback.sh
---

## 6. 监控与日志

### 6.1 日志

* 使用 `logging` 模块统一日志格式：
`[2025-06-14 15:03:21][INFO][user_service] 网络连接已建立`
* 日志等级按功能模块分类输出：`DEBUG`, `INFO`, `WARNING`, `ERROR`
* 可选接入 ELK 或 Loki + Promtail 聚合日志
* 日志保留策略：实时日志保存7天，归档日志压缩保留3个月

### 6.2 性能与服务监控

* Prometheus + Grafana 可用于性能可视化：

  * Prometheus 监控指标：
  `http_request_duration_seconds`,
  `process_cpu_seconds_total` ,
  `go_memstats_alloc_bytes`
  * Grafana 面板包含：QPS / 吞吐量，数据库慢查询统计，服务错误率趋势

* 使用 `watchdog` 或 `healthz` 接口检测服务存活：

  1. /healthz 返回 200
     ```
     #/healthz配置
     from fastapi import FastAPI
     from starlette.responses import JSONResponse

     app = FastAPI()

     @app.get("/healthz")
     async def healthz():
       server_healthy = check_outerserver_connection()
       game_healthy = check_game_connection()

       if db_healthy and redis_healthy:
         return JSONResponse(status_code=200, content={"status": "ok"})
       else:
         return JSONResponse(status_code=500, content={"status": "error"})
     ```
     在项目main.py中运行：`uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)`
  2. watchdog.sh 脚本定时 curl 检查关键端口
   
    * 可选告警策略（接入飞书）：
    CPU > 90% 持续 5min，
    接口错误率 > 1%，
    响应延迟 P95 > 1s 

---

## 7. 故障应急与备份

### 7.1 典型故障处理流程

1. 监控报警（钉钉/邮件）
2. 运维人员收到通知（5分钟内）
3. 复现问题（查看日志/重启容器）
4. 修复或回滚版本
5. 记录问题详情，提交至问题追踪系统（如Jira）
    * 问题记录模板：
  ```
  字段	内容示例
  时间	2025-06-14 14:52  
  模块	用户服务
  问题现象	注册接口 500 报错
  排查过程	检查日志、发现 DB 无法连接
  处理方式	重启数据库服务
  根因分析	数据库连接池未释放
  预防措施	增加连接池最大空闲时间配置
  ```
### 7.2 数据备份策略

* 定时任务自动备份数据库与配置文件
* 本地 + 云端双份存储
  * 本地备份目录：/data/backups/
  * 云端备份：阿里云 OSS / AWS S3
* 每日增量 + 每周全量备份并同步至云端

---

## 8. 安全性管理

* 所有敏感信息（密钥、密码）存储于 `.env` 或 CI 环境变量中，不提交到 Git
* 对外服务设置 API 限流，防止 DoS
* 所有访问日志记录 IP / UA / Token
* 所有服务启用HTTPS 通信 + JWT 验证
* 最小权限原则：每个模块只访问所需资源

---

## 附录

* CHANGELOG.md（版本更新日志）
* `.env.template`（环境变量模板）
* deploy_venv.sh（本机自动部署脚本）
* deploy_docker.sh（docker自动部署脚本）
* rollback.sh（回滚部署脚本）
* LICENSE、README.md、API 文档
