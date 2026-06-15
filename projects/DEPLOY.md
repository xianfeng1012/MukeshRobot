# 部署和本地执行指南

## 🚀 快速部署（推荐）

### 第1步：配置环境变量

```bash
cd projects
cp .env.example .env
```

编辑 `.env` 文件，填入你的三个Bot Token：

```bash
# .env 文件内容示例
GROUP_BOT_TOKEN=123456789:ABCDEFGHIJKLmnopqrstuvwxyz...
MINIAPP_BOT_TOKEN=987654321:XYZabcdefghijklmnopqrstuvwx...
USER_BOT_TOKEN=456789123:mnopqrstuvwxyzABCDEFGHIJKL...
API_BOT_TOKEN=api_token_here
SHARED_API_URL=http://localhost:5000/api
MINIAPP_URL=https://your-miniapp.example.com
MINIAPP_SECRET=your-secret-key
JWT_SECRET=your-jwt-secret
```

### 第2步：启动所有服务

```bash
# 在projects目录中执行
docker-compose up -d
```

### 第3步：验证服务运行

```bash
# 检查所有容器
docker-compose ps

# 应该看到5个容器都是 "Up" 状态：
# - telegram_bot_mongodb
# - telegram_bot_redis
# - telegram_bot_shared_api
# - telegram_bot_group_bot
# - telegram_bot_miniapp_bot
# - telegram_bot_user_bot
```

### 第4步：验证API可用

```bash
# 测试API健康检查
curl http://localhost:5000/health

# 应该返回：
# {"code":200,"message":"API is running","timestamp":"2024-06-16T..."}
```

## 📋 查看日志

```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务的日志
docker-compose logs -f shared-api
docker-compose logs -f group-bot
docker-compose logs -f miniapp-bot
docker-compose logs -f user-bot

# 查看最后100行
docker-compose logs --tail=100 shared-api
```

## 💻 本地开发（不使用Docker）

如果你想在本地直接运行（用于开发调试），按以下步骤：

### 1. 安装依赖

```bash
# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装所有依赖
pip install -r shared_api/requirements.txt
pip install -r group_bot/requirements.txt
pip install -r miniapp_bot/requirements.txt
pip install -r user_bot/requirements.txt
```

### 2. 启动MongoDB和Redis

```bash
# 使用Docker启动数据库（保持后台运行）
docker-compose up -d mongodb redis

# 或者本地安装MongoDB和Redis
```

### 3. 启动各个Bot（在不同的终端）

**终端1 - 启动API服务器：**
```bash
cd shared_api
python app.py
# 输出: 启动API服务器: 0.0.0.0:5000
```

**终端2 - 启动GroupBot：**
```bash
cd group_bot
python main.py
# 输出: GroupBot 启动中...
```

**终端3 - 启动MiniAppBot：**
```bash
cd miniapp_bot
python main.py
# 输出: MiniAppBot 启动中...
```

**终端4 - 启动UserBot：**
```bash
cd user_bot
python main.py
# 输出: UserBot 启动中...
```

## 🧪 测试Bot功能

### 测试GroupBot

1. 将GroupBot添加到你的群组
2. 邀请新用户进群
3. 新用户应该看到验证提示
4. 点击"我是真人"按钮进行验证

### 测试MiniAppBot

```bash
# 在Telegram中向bot发送
/play         # 打开小程序
/points       # 查看积分
/leaderboard  # 排行榜
/checkin      # 每日签到
```

### 测试UserBot

```bash
# 在Telegram中向bot发送
/profile      # 个人档案
/activity     # 活动记录
/stats        # 统计数据
```

### 测试API

```bash
# 创建用户
curl -X POST http://localhost:5000/api/users \
  -H "X-Bot-Token: api_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 12345,
    "username": "testuser",
    "first_name": "Test"
  }'

# 获取用户信息
curl -X GET http://localhost:5000/api/users/12345 \
  -H "X-Bot-Token: api_token_here"

# 增加积分
curl -X POST http://localhost:5000/api/users/12345/add-points \
  -H "X-Bot-Token: api_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "points": 100,
    "reason": "test_task"
  }'
```

## 🛑 停止服务

```bash
# 停止所有服务（保留数据）
docker-compose stop

# 停止并删除容器（保留数据）
docker-compose down

# 删除所有服务和数据（谨慎！）
docker-compose down -v
```

## 🔄 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart group-bot
```

## 📊 监控和调试

### 查看数据库

```bash
# 进入MongoDB容器
docker-compose exec mongodb mongosh

# 在MongoDB中
use telegram_bot_db
db.users.find().pretty()
db.activity_logs.find().limit(5).pretty()
```

### 查看Redis缓存

```bash
# 进入Redis容器
docker-compose exec redis redis-cli

# 在Redis中
KEYS *
GET user:12345:points
```

## 🚨 常见问题

### Bot无法启动

**检查Token是否正确：**
```bash
echo $GROUP_BOT_TOKEN
echo $MINIAPP_BOT_TOKEN
echo $USER_BOT_TOKEN
```

**查看日志：**
```bash
docker-compose logs group-bot
```

### API连接失败

**检查API是否运行：**
```bash
curl http://localhost:5000/health
```

**检查Network：**
```bash
docker network ls
docker network inspect projects_bot_network
```

### 数据库连接失败

**检查MongoDB：**
```bash
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

**检查Redis：**
```bash
docker-compose exec redis redis-cli ping
```

## 📝 生产部署

对于生产环境，建议：

1. **使用环境变量管理敏感信息**
   ```bash
   export GROUP_BOT_TOKEN="..."
   export MINIAPP_BOT_TOKEN="..."
   # 等等
   ```

2. **使用生产级数据库**
   - MongoDB Atlas (云托管)
   - 或自建高可用MongoDB集群

3. **使用负载均衡**
   - 多实例部署
   - 使用Nginx或HAProxy进行负载均衡

4. **启用SSL/TLS**
   - 在docker-compose中配置HTTPS
   - 使用Let's Encrypt获取免费证书

5. **监控和告警**
   - 使用Prometheus + Grafana监控
   - 设置日志聚合（ELK或Loki）

## 📞 获取帮助

遇到问题？

1. 检查日志：`docker-compose logs -f`
2. 查看README.md
3. 检查.env文件配置
4. 确保所有依赖已安装
