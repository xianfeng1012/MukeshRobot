# 宝塔面板 Docker 部署指南

## 📍 服务器信息
- IP: 144.34.180.250
- 用户: root
- 宝塔面板地址: http://144.34.180.250:8888

## 🚀 部署步骤

### 第1步：准备部署文件

1. 登录宝塔面板
2. 打开 **文件管理器**，创建部署目录：
   ```
   /www/telegram-bot
   ```

3. 上传以下文件到该目录：
   - docker-compose.yml
   - .env
   - group_bot/ (完整目录)
   - miniapp_bot/ (完整目录)
   - shared_api/ (完整目录)
   - user_bot/ (完整目录)

### 第2步：在宝塔面板中创建Docker容器

#### 方案A：使用宝塔面板 Docker 模块创建（推荐）

1. **打开宝塔面板 → Docker 模块**
2. **点击"新建容器"或"导入Docker Compose"**
3. **分别创建6个容器**：

#### 容器1: MongoDB（数据库）
```
镜像: mongo:latest
容器名: telegram_bot_mongodb
端口映射: 27017:27017
环境变量:
  MONGO_INITDB_DATABASE=telegram_bot_db
数据卷:
  mongo_data:/data/db
重启策略: 总是重启
```

#### 容器2: Redis（缓存）
```
镜像: redis:alpine
容器名: telegram_bot_redis
端口映射: 6379:6379
数据卷:
  redis_data:/data
重启策略: 总是重启
命令: redis-server --appendonly yes
```

#### 容器3: shared-api（Flask API）
```
镜像: 需要构建 (dockerfile在 shared_api/)
容器名: telegram_bot_shared_api
端口映射: 5000:5000
环境变量:
  MONGO_URI=mongodb://telegram_bot_mongodb:27017
  MONGO_DB=telegram_bot_db
  REDIS_URL=redis://telegram_bot_redis:6379/0
  API_HOST=0.0.0.0
  API_PORT=5000
  API_DEBUG=False
  LOG_LEVEL=INFO
  GROUP_BOT_TOKEN=<你的token>
  MINIAPP_BOT_TOKEN=<你的token>
  USER_BOT_TOKEN=<你的token>
  API_BOT_TOKEN=<任意字符串>
  MINIAPP_URL=https://your-miniapp.com
  MINIAPP_SECRET=your-secret
  JWT_SECRET=your-jwt-secret
重启策略: 总是重启
依赖: MongoDB, Redis
```

#### 容器4: group-bot（群管理机器人）
```
镜像: 需要构建 (dockerfile在 group_bot/)
容器名: telegram_bot_group_bot
环境变量:
  GROUP_BOT_TOKEN=<你的token>
  SHARED_API_URL=http://telegram_bot_shared_api:5000/api
  API_BOT_TOKEN=<任意字符串>
  LOG_LEVEL=INFO
重启策略: 总是重启
依赖: shared-api
```

#### 容器5: miniapp-bot（小程序机器人）
```
镜像: 需要构建 (dockerfile在 miniapp_bot/)
容器名: telegram_bot_miniapp_bot
端口映射: 8000:8000
环境变量:
  MINIAPP_BOT_TOKEN=<你的token>
  SHARED_API_URL=http://telegram_bot_shared_api:5000/api
  API_BOT_TOKEN=<任意字符串>
  MINIAPP_URL=https://your-miniapp.com
  JWT_SECRET=your-jwt-secret
  LOG_LEVEL=INFO
重启策略: 总是重启
依赖: shared-api
```

#### 容器6: user-bot（用户管理机器人）
```
镜像: 需要构建 (dockerfile在 user_bot/)
容器名: telegram_bot_user_bot
环境变量:
  USER_BOT_TOKEN=<你的token>
  SHARED_API_URL=http://telegram_bot_shared_api:5000/api
  API_BOT_TOKEN=<任意字符串>
  LOG_LEVEL=INFO
重启策略: 总是重启
依赖: shared-api
```

#### 方案B：使用命令行（更高效）

在宝塔面板的终端中执行：

```bash
cd /www/telegram-bot

# 构建所有镜像
docker build -t projects-shared-api:latest -f shared_api/Dockerfile shared_api/
docker build -t projects-group-bot:latest -f group_bot/Dockerfile group_bot/
docker build -t projects-miniapp-bot:latest -f miniapp_bot/Dockerfile miniapp_bot/
docker build -t projects-user-bot:latest -f user_bot/Dockerfile user_bot/

# 启动所有容器
docker-compose up -d
```

### 第3步：配置 .env 文件

在宝塔面板文件管理器中创建 `/www/telegram-bot/.env`：

```
# Bot Tokens（必须填写你的token）
GROUP_BOT_TOKEN=your_group_bot_token
MINIAPP_BOT_TOKEN=your_miniapp_bot_token
USER_BOT_TOKEN=your_user_bot_token

# API配置
API_BOT_TOKEN=api_token_secure_key
SHARED_API_URL=http://localhost:5000/api

# 数据库
MONGO_URI=mongodb://telegram_bot_mongodb:27017
MONGO_DB=telegram_bot_db
REDIS_URL=redis://telegram_bot_redis:6379/0

# Mini App配置
MINIAPP_URL=https://your-miniapp.example.com
MINIAPP_SECRET=your-miniapp-secret-key
MINIAPP_WEBHOOK_URL=http://localhost:8000/webhook/mini-app-event

# JWT配置
JWT_SECRET=your-jwt-secret-key-here
JWT_EXPIRATION_HOURS=24

# 其他配置
LOG_LEVEL=INFO
API_DEBUG=False
BOT_USERNAME=your_group_bot_username
```

### 第4步：验证部署

#### 在宝塔面板中查看容器

1. 打开宝塔面板 → Docker 模块
2. 应该看到6个容器都处于 **运行中** 状态：
   - telegram_bot_mongodb ✅
   - telegram_bot_redis ✅
   - telegram_bot_shared_api ✅
   - telegram_bot_group_bot ✅
   - telegram_bot_miniapp_bot ✅
   - telegram_bot_user_bot ✅

#### 测试API

在宝塔面板终端执行：
```bash
# 测试API健康检查
curl http://localhost:5000/health

# 应该返回：
# {"code":200,"message":"API is running","timestamp":"..."}
```

#### 查看日志

在宝塔面板中：
1. 点击每个容器
2. 查看 **日志** 标签，确认无错误

---

## 🔍 常见问题排查

### 问题1：容器无法启动
- 检查镜像是否成功构建
- 查看宝塔Docker日志：`docker logs <container_name>`
- 确保所有环境变量都已正确设置

### 问题2：容器之间无法通信
- 确保所有容器都在同一Docker网络中
- 在容器内使用 `docker network inspect projects_bot_network` 查看

### 问题3：文件权限问题
- 确保 `/www/telegram-bot` 目录权限为 755
- 文件权限为 644

### 问题4：端口已被占用
- 检查是否有其他服务占用 5000、6379、27017、8000 端口
- 在宝塔面板中修改端口映射

---

## 📞 宝塔面板 Docker 快速命令

在宝塔面板终端执行：

```bash
# 查看所有容器
docker ps -a

# 查看容器日志
docker logs -f telegram_bot_shared_api

# 进入容器
docker exec -it telegram_bot_shared_api /bin/bash

# 停止所有容器
docker-compose stop

# 启动所有容器
docker-compose start

# 重新构建并启动
docker-compose up -d --build

# 删除所有容器（谨慎！）
docker-compose down
```

---

## ✅ 部署完成检查清单

- [ ] 所有6个容器在宝塔面板中显示为 "运行中"
- [ ] API 健康检查成功 (`curl http://localhost:5000/health`)
- [ ] MongoDB 容器可以访问
- [ ] Redis 容器可以访问
- [ ] 三个Bot容器无错误日志
- [ ] 已将宝塔面板密码记录在安全地方
- [ ] 已在防火墙中开放必要的端口
- [ ] 已备份 .env 文件（包含敏感信息）

---

## 🔐 安全建议

### 立即执行

1. **更改root密码**
   ```bash
   passwd root
   ```

2. **更改宝塔面板密码**
   - 在宝塔面板 → 设置 → 修改密码

3. **配置防火墙**
   - 在宝塔面板 → 安全 → 防火墙规则
   - 开放端口：22, 8888, 5000, 8000
   - 其他端口（MongoDB、Redis）设为仅内部访问

4. **备份敏感信息**
   - 安全保存 .env 文件
   - 记录所有Bot Token

### 长期维护

- 定期更新Docker镜像
- 定期检查容器日志
- 定期备份数据库（MongoDB）
- 使用SSH密钥替代密码认证
