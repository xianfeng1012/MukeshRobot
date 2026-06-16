# 🚀 宝塔面板 Docker 部署 - 快速启动

> **目标:** 在宝塔面板的Docker管理界面中部署3个Telegram机器人（GroupBot、MiniAppBot、UserBot）

---

## 📋 准备工作（本地）

### 步骤1：收集所有部署文件

确保您有以下文件准备好上传到服务器（推荐压缩后上传）：

```
telegram-bot/
├── docker-compose.yml              ✅ (已有)
├── .env.example                    ✅ (已有)
├── .env                           (需要创建)
├── shared_api/
│   ├── Dockerfile                 ✅ (已有)
│   ├── app.py                     ✅ (已有)
│   ├── config.py                  ✅ (已有)
│   ├── models.py                  ✅ (已有)
│   └── requirements.txt            ✅ (已有)
├── group_bot/
│   ├── Dockerfile                 ✅ (已有)
│   ├── main.py                    ✅ (已有)
│   ├── handlers.py                ✅ (已有)
│   ├── config.py                  ✅ (已有)
│   └── requirements.txt            ✅ (已有)
├── miniapp_bot/
│   ├── Dockerfile                 ✅ (已有)
│   ├── main.py                    ✅ (已有)
│   ├── handlers.py                ✅ (已有)
│   ├── utils.py                   ✅ (已有)
│   ├── config.py                  ✅ (已有)
│   └── requirements.txt            ✅ (已有)
└── user_bot/
    ├── Dockerfile                 ✅ (已有)
    ├── main.py                    ✅ (已有)
    ├── handlers.py                ✅ (已有)
    ├── config.py                  ✅ (已有)
    └── requirements.txt            ✅ (已有)
```

### 步骤2：生成 .env 文件

创建 `.env` 文件（包含您的Bot Token）：

```bash
# 在本地项目根目录创建 .env
cat > .env << 'EOF'
# Bot Tokens（必须填写你的实际token）
GROUP_BOT_TOKEN=YOUR_GROUP_BOT_TOKEN_HERE
MINIAPP_BOT_TOKEN=YOUR_MINIAPP_BOT_TOKEN_HERE
USER_BOT_TOKEN=YOUR_USER_BOT_TOKEN_HERE

# API配置
API_BOT_TOKEN=secure_api_token_123456
SHARED_API_URL=http://shared-api:5000/api

# 数据库配置
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=telegram_bot_db
REDIS_URL=redis://redis:6379/0

# Mini App配置
MINIAPP_URL=https://your-miniapp.example.com
MINIAPP_SECRET=your-miniapp-secret-key
MINIAPP_WEBHOOK_URL=http://miniapp-bot:8000/webhook/mini-app-event

# JWT配置
JWT_SECRET=your-jwt-secret-key-change-this
JWT_EXPIRATION_HOURS=24

# 其他配置
LOG_LEVEL=INFO
API_DEBUG=False
BOT_USERNAME=your_group_bot_username
EOF
```

> ⚠️ **重要:** 用你实际的Bot Token替换 `YOUR_*_BOT_TOKEN_HERE`

---

## 🖥️ 服务器部分（宝塔面板）

### 步骤3：登录宝塔面板

1. 打开浏览器，访问: `http://144.34.180.250:8888`
2. 输入用户名和密码登录
3. 记住这个密码！（后续会用到）

### 步骤4：创建部署目录

在宝塔面板中：

1. **打开文件管理器**
   - 左侧菜单 → 文件 → 文件管理器
   - 点击 `/www` 目录

2. **创建新目录**
   - 右键 → 新建文件夹
   - 文件夹名: `telegram-bot`
   - 记住完整路径: `/www/telegram-bot`

### 步骤5：上传部署文件到服务器

**方案A：通过宝塔面板文件管理器上传（推荐新手）**

1. 在宝塔面板中进入 `/www/telegram-bot` 目录
2. **上传 .env 文件**
   - 点击"上传"按钮
   - 选择本地的 `.env` 文件
   - 等待上传完成

3. **上传 docker-compose.yml**
   - 点击"上传"按钮
   - 选择本地的 `docker-compose.yml`
   - 等待上传完成

4. **上传所有项目文件夹**
   - 逐个上传:
     - `shared_api/` 目录
     - `group_bot/` 目录  
     - `miniapp_bot/` 目录
     - `user_bot/` 目录
   - 宝塔面板会自动处理目录结构

**方案B：通过宝塔终端上传（更高效）**

如果您有SSH密钥，可以在宝塔终端执行：

```bash
# 在宝塔面板 → 工具 → SSH终端 中执行
cd /www/telegram-bot

# 从本地下载文件（使用wget或curl）
# 或者直接在宝塔文件管理器中拖拽上传

ls -la  # 验证文件已上传
```

### 步骤6：构建Docker镜像

在宝塔面板中打开 **Docker** 模块（如果没有，需要先安装）：

1. **打开宝塔面板 → 应用商店 → 搜索 Docker**
2. **安装 Docker**（如果未安装）
3. 安装完成后，进入 Docker 模块

### 步骤7：构建镜像

在宝塔 Docker 模块中，打开 **镜像管理**：

**方案A：通过宝塔UI构建（推荐）**

1. 点击 **新建镜像** 或 **本地构建**
2. 指定Dockerfile路径和构建参数
3. 逐个构建：
   - `shared_api` 镜像
   - `group_bot` 镜像
   - `miniapp_bot` 镜像
   - `user_bot` 镜像

**方案B：通过终端快速构建**

在宝塔 Docker 终端中执行：

```bash
cd /www/telegram-bot

# 构建所有镜像
docker build -t projects-shared-api:latest -f shared_api/Dockerfile ./shared_api
docker build -t projects-group-bot:latest -f group_bot/Dockerfile ./group_bot
docker build -t projects-miniapp-bot:latest -f miniapp_bot/Dockerfile ./miniapp_bot
docker build -t projects-user-bot:latest -f user_bot/Dockerfile ./user_bot

# 验证镜像
docker images | grep projects-
```

### 步骤8：启动容器（通过 docker-compose）

**最简单的方式：使用 docker-compose**

在宝塔 Docker 模块中：

1. **找到 "Compose" 或 "Docker Compose" 选项**
2. **导入 docker-compose.yml**
   - 选择上传的 `/www/telegram-bot/docker-compose.yml` 文件
   - 或者复制-粘贴 docker-compose.yml 内容
3. **点击启动**

或者在宝塔终端执行：

```bash
cd /www/telegram-bot

# 启动所有服务
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤9：验证部署成功

#### 在宝塔 Docker 模块中查看容器

1. **打开宝塔面板 → Docker → 容器管理**
2. 应该看到以下容器都处于 **运行中** (Up) 状态：
   ```
   ✅ telegram_bot_mongodb (或简写为 mongodb)
   ✅ telegram_bot_redis (或简写为 redis)
   ✅ telegram_bot_shared_api (或简写为 shared-api)
   ✅ telegram_bot_group_bot (或简写为 group-bot)
   ✅ telegram_bot_miniapp_bot (或简写为 miniapp-bot)
   ✅ telegram_bot_user_bot (或简写为 user-bot)
   ```

#### 测试API健康状态

在宝塔终端执行：

```bash
# 测试shared-api健康检查
curl http://localhost:5000/health

# 应该返回：
# {"code":200,"message":"API is running","timestamp":"2026-06-16T..."}
```

#### 查看容器日志

在宝塔 Docker 模块中：

1. 点击每个容器名称
2. 查看 **日志** 标签
3. 确认没有错误信息
4. 如果有错误，检查环境变量配置

---

## ✅ 部署完成检查清单

**容器状态验证**
- [ ] MongoDB 容器运行中
- [ ] Redis 容器运行中
- [ ] shared-api 容器运行中 (端口 5000)
- [ ] group-bot 容器运行中
- [ ] miniapp-bot 容器运行中 (端口 8000)
- [ ] user-bot 容器运行中

**功能验证**
- [ ] API 健康检查成功: `curl http://localhost:5000/health`
- [ ] MongoDB 数据库可访问
- [ ] Redis 缓存可访问
- [ ] 三个Bot容器日志无错误

**安全验证**
- [ ] .env 文件权限正确 (644)
- [ ] /www/telegram-bot 目录权限正确 (755)
- [ ] 防火墙已配置（见下文）

---

## 🔐 安全配置（必须立即执行）

### 立即更改密码

1. **更改 root 密码**
   ```bash
   # 在宝塔终端执行
   passwd root
   ```

2. **更改宝塔面板管理员密码**
   - 宝塔面板 → 用户中心 → 修改密码
   - 或者: 宝塔面板 → 设置 → 修改密码

3. **配置防火墙规则**
   - 宝塔面板 → 安全 → 防火墙
   - 只开放必要端口：
     ```
     22   (SSH)
     8888 (宝塔面板)
     5000 (API)
     8000 (Mini App webhook)
     ```
   - MongoDB 和 Redis 端口仅限容器内部访问

### 配置 SSH 密钥（推荐）

替换密码认证为密钥认证：

```bash
# 在宝塔终端执行
# 生成SSH密钥对（如果没有）
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

# 禁用密码认证（需要root）
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd
```

---

## 🔄 维护和管理

### 查看实时日志

```bash
# 在宝塔终端查看所有容器日志
cd /www/telegram-bot
docker-compose logs -f

# 查看特定容器日志
docker logs -f telegram_bot_shared_api
```

### 重启容器

```bash
cd /www/telegram-bot

# 重启所有容器
docker-compose restart

# 重启特定容器
docker-compose restart shared-api

# 重启并重新构建镜像
docker-compose up -d --build
```

### 停止容器

```bash
cd /www/telegram-bot

# 停止所有容器（不删除）
docker-compose stop

# 启动所有容器
docker-compose start

# 删除所有容器和网络（谨慎！）
docker-compose down
```

### 数据备份

```bash
# 备份 MongoDB 数据
docker exec telegram_bot_mongodb mongodump --out /backup

# 备份 Redis 数据
docker exec telegram_bot_redis redis-cli BGSAVE
```

---

## 🐛 常见问题排查

### 问题1：容器无法启动

**症状**: 容器显示 "Exited" 或 "Dead"

**解决方案**:
```bash
# 查看错误日志
docker logs telegram_bot_shared_api

# 常见原因:
# 1. 端口被占用 - 修改 docker-compose.yml 中的端口
# 2. 环境变量缺失 - 检查 .env 文件
# 3. Dockerfile 错误 - 重新构建镜像
docker build -t projects-shared-api:latest -f shared_api/Dockerfile ./shared_api
```

### 问题2：容器之间无法通信

**症状**: Bot 连接不到 API，API 连接不到 MongoDB

**解决方案**:
```bash
# 检查Docker网络
docker network ls
docker network inspect projects_bot_network

# 确保容器名称正确（在docker-compose.yml中）
docker ps

# 测试连接
docker exec telegram_bot_group_bot curl http://shared-api:5000/health
```

### 问题3：Bot Token 无效

**症状**: Bot 日志显示 "Invalid token" 或 "Unauthorized"

**解决方案**:
1. 检查 .env 文件中的 Bot Token 是否正确
2. 确保 Token 没有多余空格或特殊字符
3. 重启容器使新配置生效:
   ```bash
   docker-compose restart group-bot miniapp-bot user-bot
   ```

### 问题4：内存或磁盘不足

**症状**: 容器频繁 Killed，或"No space left on device"

**解决方案**:
```bash
# 查看磁盘使用
docker system df

# 清理未使用的镜像和容器
docker system prune -a

# 查看MongoDB数据大小
docker exec telegram_bot_mongodb du -h /data/db
```

### 问题5：宝塔面板无法显示容器

**症状**: 宝塔 Docker 模块中看不到容器

**解决方案**:
1. 确认 Docker 已在宝塔面板中安装
2. 刷新浏览器: Ctrl+F5
3. 重启宝塔面板:
   ```bash
   systemctl restart bt
   ```
4. 检查 Docker 守护进程状态:
   ```bash
   systemctl status docker
   ```

---

## 📞 快速命令参考

```bash
# 进入部署目录
cd /www/telegram-bot

# 查看所有容器状态
docker ps -a

# 查看镜像列表
docker images

# 重新启动所有服务
docker-compose restart

# 查看实时日志
docker-compose logs -f

# 进入容器交互模式
docker exec -it telegram_bot_shared_api /bin/bash

# 停止和删除所有（谨慎！）
docker-compose down -v
```

---

## ✨ 下一步

部署完成后：

1. **通知 Bot 用户**
   - 群主将 @GroupBot 添加到群组
   - 用户使用 /start 命令测试其他机器人

2. **配置 Mini App（如果使用）**
   - 在 MINIAPP_URL 指向的服务器上部署前端
   - 配置 MINIAPP_WEBHOOK_URL 接收事件

3. **监控和维护**
   - 定期检查容器日志
   - 定期备份 MongoDB 数据
   - 定期更新Docker镜像和依赖

4. **扩展功能**
   - 添加更多命令处理器
   - 集成第三方服务
   - 配置更多的安全规则

---

## 📚 相关文档

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 详细部署指南
- [README.md](./README.md) - 项目概述
- [CLAUDE.md](./CLAUDE.md) - 开发指南

**需要帮助?** 查看容器日志: `docker logs <container_name>`
