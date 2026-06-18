# 双向机器人（商用客服转发 Bot · 多号共群版）设计

日期：2026-06-17
状态：已确认，待实现

## 1. 目标
新增第 4 个独立服务 `dual_bot`：**N 个对外机器人**（当前 5 个，后期可加）作为客服入口，
客户私聊任一机器人 → 消息全部汇总到**同一个客服群**统一接待；客服在群里 reply →
自动用客户当初私聊的那个号原样回传。客户不知道客服身份，也看不到群。

## 2. 架构
- 单服务、单进程，内部用 asyncio 并发跑 N 个 PTB Application（每个一个 token），
  共享一个 MongoDB 连接和同一个 `SUPPORT_GROUP_ID`。
- 配置驱动：`DUAL_BOT_TOKENS` 是逗号分隔的 token 列表。加号 = 往列表追加 token + 把新号
  拉进客服群 + 重启服务，代码不改。
- 不依赖 shared_api / yanyulou。python-telegram-bot v20.3。

```
客户A 私聊 Bot1 ┐
客户B 私聊 Bot2 ├──► 同一客服群 ──► 客服 reply ──► 自动用对应号回传原客户
客户C 私聊 Bot5 ┘       (身份头注明来自哪个号)
```

## 3. 多号共群的路由（核心）
- 所有机器人**保持隐私模式开启（默认）**。
- Telegram 规则：隐私模式下机器人在群里**只收到「对它自己发的消息的回复」**。
- 客户消息由「源机器人」copy 进群 → 客服 reply 该消息时，**只有源机器人收到**，其余 N-1 个收不到。
- → 天然路由，零串号、零重复，无需去重逻辑。映射表仍存源 bot id 作兜底。

## 4. 核心数据流
- **客户 → 群**：客户私聊某机器人发任意消息 → 该机器人在客服群先发身份头
  `👤 张三 (@zhangsan / id:123456) ·〔Bot3〕`，紧接着 `copy_message` 把原消息复制进群
  （文本/图片/语音/视频/文件/贴纸/位置全支持）。
- **群 → 客户**：客服 reply 客户那条消息再发内容 → 源机器人收到 → 用
  `reply_to_message.message_id` 查 `customer_id` → `copy_message` 回传客户。
- **非 reply 的群内消息** → 忽略（客服内部讨论）。

## 5. 会话映射
MongoDB 集合 `dual_relay`：
```
{ group_msg_id: <copy 到群后返回的 message_id>, customer_id: <客户 tg id>,
  bot_id: <源机器人 id>, ts: <时间> }
```
群内 message_id 全群唯一，按 group_msg_id 查即可；bot_id 仅作兜底校验。存 Mongo →
重启后旧会话仍可回复。

## 6. 身份标识
最简一行头：昵称 + @用户名 + id + 〔来源号标签〕。来源号标签便于客服区分客户走的哪个门面。

## 7. 配置 / 前置条件
- 已建 5 个机器人（隐私模式默认开启），token 见部署记录。
- 客服群 ID：`-4446604880`，5 个机器人全部拉进群。
- 环境变量：`DUAL_BOT_TOKENS`（逗号分隔）、`SUPPORT_GROUP_ID`、`MONGODB_URL`（复用现有 mongodb:27017）。

## 8. 组件
- `dual_bot/config.py`：解析 token 列表 / 群 ID / Mongo URL。
- `dual_bot/db.py`：pymongo 连接，`dual_relay` 读写（save_map / find_customer）。
- `dual_bot/handlers.py`：
  - `on_customer_message`：私聊入站 → 发身份头 + copy 到群 + 存映射。
  - `on_group_reply`：群内 reply → 查客户 → copy 回传。
  - `cmd_id`：群里回 `/id` 返回当前 chat id（部署辅助）。
- `dual_bot/main.py`：为每个 token 构建 Application，asyncio 并发 start + polling。
- `dual_bot/Dockerfile` + `requirements.txt`（`python-telegram-bot==20.3`、`pymongo`；**不需要 job-queue**）。
- `docker-compose.yml` 增加 `dual-bot` 服务（依赖 mongodb）。

## 9. 错误处理
- copy 失败（客户拉黑机器人 / 群权限不足）→ 记日志，不崩溃。
- reply 目标在映射表查不到 → 静默忽略。
- 单个 Application 异常不应拖垮其它实例。

## 10. 本期不做（YAGNI）
欢迎语、拉黑/解黑、富信息卡、多客服分配、工单统计、自动回复。

## 11. 验证标准
- 客户私聊 Bot1 发文字/图片 → 客服群出现身份头 + 内容，头部标注〔Bot1〕。
- 客服 reply 该消息发文字/图片 → 该客户私聊收到，且是 Bot1 发的。
- 客户私聊 Bot2 → 同群另一条，客服 reply → 由 Bot2 回传，不串到 Bot1 客户。
- 重启服务后对旧群消息 reply 仍正确回传。
- 客服群里不 reply 直接发言 → 无客户收到。
