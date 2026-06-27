# ⚡ 宝塔面板部署 - 5分钟快速开始

## 🎯 你需要做的（按顺序）

### 1️⃣ 准备本地文件
在您的电脑上执行：

```bash
# 进入项目目录
cd 项目路径

# 创建 .env 文件（用您的实际Token替换）
cat > .env << 'EOF'
GROUP_BOT_TOKEN=你的GROUP_BOT_TOKEN
MINIAPP_BOT_TOKEN=你的MINIAPP_BOT_TOKEN
USER_BOT_TOKEN=你的USER_BOT_TOKEN
API_BOT_TOKEN=api_secret_123
SHARED_API_URL=http://shared-api:5000/api
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=telegram_bot_db
REDIS_URL=redis://redis:6379/0
MINIAPP_URL=https://your-miniapp.example.com
JWT_SECRET=jwt_secret_key_here
LOG_LEVEL=INFO
EOF
```

✅ 检查清单：
- [ ] 已创建 `.env` 文件
- [ ] 已填入真实的 Bot Token
- [ ] 已保存文件

---

### 2️⃣ 登录宝塔面板并上传文件

1. 打开浏览器：`http://144.34.180.250:8888`
2. 输入用户名和密码登录
3. 在左侧菜单 → **文件** → **文件管理器**
4. 导航到 `/www` 目录
5. **创建文件夹** `telegram-bot`
6. **上传以下文件**：
   - `.env` ✅
   - `docker-compose.yml` ✅
   - `shared_api/` 文件夹 ✅
   - `group_bot/` 文件夹 ✅
   - `miniapp_bot/` 文件夹 ✅
   - `user_bot/` 文件夹 ✅

✅ 检查清单：
- [ ] 已在宝塔面板登录
- [ ] 已创建 `/www/telegram-bot` 目录
- [ ] 已上传所有文件和文件夹
- [ ] 文件结构与下面完全一致

```
/www/telegram-bot/
├── docker-compose.yml
├── .env
├── shared_api/
├── group_bot/
├── miniapp_bot/
└── user_bot/
```

---

### 3️⃣ 在宝塔面板中构建Docker镜像

在宝塔面板 **Docker** 模块（可能需要先装）中：

**打开宝塔面板 → Docker → 镜像管理**

或者使用 **终端** 方式（更快）：
1. 宝塔面板 → **工具** → **SSH终端**
2. 执行以下命令：

```bash
# 进入部署目录
cd /www/telegram-bot

# 构建4个镜像（会自动安装依赖，首次较慢）
docker build -t projects-shared-api:latest -f shared_api/Dockerfile ./shared_api
docker build -t projects-group-bot:latest -f group_bot/Dockerfile ./group_bot
docker build -t projects-miniapp-bot:latest -f miniapp_bot/Dockerfile ./miniapp_bot
docker build -t projects-user-bot:latest -f user_bot/Dockerfile ./user_bot

# 验证镜像已创建
docker images | grep projects-
```

✅ 检查清单：
- [ ] 镜像构建完成（无错误）
- [ ] `docker images` 显示4个 `projects-*:latest` 镜像

---

### 4️⃣ 启动所有容器

在同一个 **SSH终端** 中继续执行：

```bash
cd /www/telegram-bot

# 启动所有6个容器（MongoDB、Redis、API、3个Bot）
docker-compose up -d

# 查看运行状态（应该都是 Up）
docker-compose ps
```

✅ 检查清单：
- [ ] 命令执行成功（无错误）
- [ ] `docker-compose ps` 显示6个容器都是 "Up" 状态

---

### 5️⃣ 验证部署成功

#### ✅ 在宝塔 Docker 模块中查看

1. 宝塔面板 → **Docker** → **容器管理**
2. 应该看到6个容器都处于 **运行中** ✅：
   - mongodb
   - redis
   - shared-api
   - group-bot
   - miniapp-bot
   - user-bot

#### ✅ 测试API是否工作

在 **SSH终端** 中执行：

```bash
# 测试API健康检查
curl http://localhost:5000/health

# 应该看到返回（类似这样）：
# {"code":200,"message":"API is running","timestamp":"..."}
```

#### ✅ 查看容器日志

在宝塔 Docker 模块中，点击每个容器查看 **日志**，确认：
- ✅ 无红色错误信息
- ✅ 看到 "已启动" 或 "Running" 的日志

---

## 🎉 完成！

如果以上所有步骤都成功，您的3个机器人已经部署在宝塔服务器上了！

### 现在可以做什么：

1. **测试GroupBot**
   - 创建一个Telegram群组
   - 添加 @YourGroupBot 到群组
   - 看它是否欢迎新成员 ✅

2. **测试MiniAppBot**
   - 直接私聊 @YourMiniAppBot
   - 运行 `/points` 命令 ✅

3. **测试UserBot**
   - 直接私聊 @YourUserBot
   - 运行 `/profile` 命令 ✅

---

## 🆘 遇到问题？

### 问题：容器无法启动

**解决方案**：查看错误日志
```bash
docker-compose logs shared-api    # 查看API日志
docker logs telegram_bot_group_bot  # 查看GroupBot日志
```

### 问题：Bot无响应

**原因**: 可能Token不正确或环境变量未生效

**解决方案**：
```bash
# 重启Bot容器
docker-compose restart group-bot miniapp-bot user-bot
```

### 问题：API无法连接

**解决方案**：
```bash
# 检查MongoDB和Redis是否运行
docker-compose ps

# 查看API日志
docker logs telegram_bot_shared_api
```

---

## 🔐 部署后安全步骤（重要！）

⚠️ **立即执行**（在宝塔 SSH 终端中）：

```bash
# 1. 更改root密码
passwd root

# 2. 查看并记录重要信息
echo "服务器状态检查："
docker ps -a
df -h  # 磁盘空间
```

然后在宝塔面板中：
- 宝塔面板 → 设置 → 修改密码
- 宝塔面板 → 安全 → 防火墙规则

---

## 📞 需要完整的详细指南？

查看以下文件：
- **[BAOTA_DEPLOYMENT.md](./BAOTA_DEPLOYMENT.md)** - 完整部署指南（包含排查和维护）
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - 详细的功能说明
- **[README.md](./README.md)** - 项目概述

---

## ⏱️ 预计耗时

- 准备文件：5分钟
- 上传文件到宝塔：10-20分钟（取决于网速）
- 构建镜像：15-30分钟（首次）
- 启动容器：2分钟
- **总计：30-60分钟**

**祝部署顺利！** 🚀
