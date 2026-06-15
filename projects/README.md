# Telegram 三Bot架构项目

一个完整的Telegram三Bot系统，提供群组管理、小程序集成和用户管理功能。

## 🏗️ 项目架构

```
┌─────────────────────────────────────────────┐
│         共享数据层 (Shared API)              │
│  ┌───────────────────────────────────────┐  │
│  │   MongoDB + Redis + Flask API         │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         ↑            ↑            ↑
    ┌────────┐  ┌─────────┐  ┌──────────┐
    │GroupBot │  │MiniApp  │  │ UserBot  │
    │ 群管理   │  │ Bot小程序 │  │ 用户管理 │
    └────────┘  └─────────┘  └──────────┘
```

## 📦 三个Bot的职责

### 1️⃣ GroupBot（群管理机器人）
- ✅ 进群欢迎消息
- ✅ 身份验证（CAPTCHA）
- ✅ 垃圾消息检测和过滤
- ✅ 广告屏蔽
- ✅ 违规警告和禁言
- ✅ 信誉分管理

### 2️⃣ MiniAppBot（小程序管理机器人）
- 💰 积分系统
- 📋 任务管理
- 🏆 排行榜
- 🎮 Mini App集成
- 🎯 成就系统
- 📊 统计数据

### 3️⃣ UserBot（用户管理机器人）
- 👤 个人档案管理
- 📋 活动记录查询
- 📊 统计数据展示
- 🎖️ 成就徽章
- 🔐 隐私设置
- 🏷️ 头衔管理

## 🚀 快速开始

### 前置要求
- Python 3.10+
- Docker & Docker Compose
- 三个Telegram Bot Token

### 1. 克隆项目
```bash
cd projects
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的Bot Token和配置
```

### 3. 启动所有服务
```bash
docker-compose up -d
```

这会启动：
- MongoDB 数据库
- Redis 缓存
- 共享API服务器 (端口 5000)
- GroupBot
- MiniAppBot
- UserBot

### 4. 验证服务运行
```bash
# 检查API健康状态
curl http://localhost:5000/health

# 查看日志
docker-compose logs -f shared-api
docker-compose logs -f group-bot
docker-compose logs -f miniapp-bot
docker-compose logs -f user-bot
```

## 📝 GroupBot 命令

```
/start - 开始
/help - 帮助
/stats - 群组统计
```

进群新成员需要点击验证按钮证明身份，120秒内未验证则被踢出。

## 💰 MiniAppBot 命令

```
/play - 打开小程序
/points - 查看积分和等级
/leaderboard - 查看排行榜
/checkin - 每日签到
/tasks - 任务列表
/stats - 个人统计
```

## 👤 UserBot 命令

```
/profile - 个人档案
/activity - 活动记录
/stats - 统计数据
/achievements - 成就展示
/privacy - 隐私设置
```

## 🔌 API接口

### 用户相关
- `GET /api/users/<user_id>` - 获取用户信息
- `POST /api/users` - 创建/更新用户
- `GET /api/users/<user_id>/points` - 获取积分
- `POST /api/users/<user_id>/add-points` - 增加积分

### 黑名单
- `GET /api/blacklist/check/<user_id>` - 检查是否黑名单
- `POST /api/blacklist/add` - 添加到黑名单

### 活动日志
- `GET /api/users/<user_id>/activity-log` - 获取活动记录

### 排行榜
- `GET /api/leaderboard` - 获取排行榜

### Mini App
- `POST /api/webhook/mini-app-event` - 接收Mini App事件

## 🔐 安全配置

1. **修改JWT_SECRET**
   ```bash
   # 生成新的密钥
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **修改MINIAPP_SECRET**
   ```bash
   # 在你的Mini App服务器中也需要相同的密钥
   ```

3. **修改API_BOT_TOKEN**
   ```bash
   # 用于API认证的Token，确保Bot Token安全
   ```

## 📊 数据库结构

### Collections
- `users` - 用户档案
- `groups` - 群组配置
- `tasks` - 任务列表
- `activity_logs` - 活动日志
- `blacklist` - 黑名单

## 🌐 Mini App集成

Mini App需要以下配置：

### 获取访问令牌
用户在Telegram中点击"打开小程序"会获得一个JWT令牌，格式：
```
https://miniapp.example.com?token=<jwt_token>&user_id=<user_id>
```

### 验证令牌
在Mini App中验证Token：
```python
import jwt
from config import JWT_SECRET, JWT_ALGORITHM

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### 提交任务完成事件
```javascript
fetch('http://miniapp-bot:8000/webhook/mini-app-event', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        event_type: 'task_completed',
        user_id: userId,
        task_id: 'task_123',
        points: 100,
        timestamp: Date.now()
    })
})
```

## 📦 Docker命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启单个服务
docker-compose restart group-bot

# 进入MongoDB容器
docker-compose exec mongodb mongosh
```

## 🔧 本地开发（不使用Docker）

### 安装依赖
```bash
# shared_api
cd shared_api
pip install -r requirements.txt

# group_bot
cd ../group_bot
pip install -r requirements.txt

# miniapp_bot
cd ../miniapp_bot
pip install -r requirements.txt

# user_bot
cd ../user_bot
pip install -r requirements.txt
```

### 启动服务
```bash
# 在不同的终端窗口中启动

# Terminal 1: shared_api
cd shared_api
python app.py

# Terminal 2: group_bot
cd group_bot
python main.py

# Terminal 3: miniapp_bot
cd miniapp_bot
python main.py

# Terminal 4: user_bot
cd user_bot
python main.py
```

## 📝 日志文件

各bot会生成日志文件：
- `shared_api/shared_api.log`
- `group_bot/group_bot.log`
- `miniapp_bot/miniapp_bot.log`
- `user_bot/user_bot.log`

## 🐛 故障排除

### MongoDB连接失败
```bash
# 检查MongoDB状态
docker-compose ps mongodb

# 查看MongoDB日志
docker-compose logs mongodb
```

### Bot无法启动
```bash
# 检查Token是否正确设置
cat .env | grep BOT_TOKEN

# 查看bot日志
docker-compose logs group-bot
```

### API无法连接
```bash
# 检查API是否运行
curl http://localhost:5000/health

# 检查网络
docker network ls
```

## 📚 相关文档

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [MongoDB](https://docs.mongodb.com/)
- [Flask](https://flask.palletsprojects.com/)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
