# 双向机器人（商用客服转发 Bot）设计

日期：2026-06-17
状态：已确认，待实现

## 1. 目标
新增第 4 个独立 Telegram 机器人 `dual_bot`，作为客服中转：客户私聊机器人 → 转发到内部客服群；客服在群里回复 → 原样回传客户。客户不知道客服身份，也看不到群。

## 2. 架构定位
- 独立服务，加入现有 `projects/docker-compose.yml`。
- 复用 MongoDB（存会话映射）。**不依赖** shared_api、不依赖 yanyulou。
- python-telegram-bot v20.3，与其他三个 bot 保持一致。

```
客户私聊 DualBot ──► 客服群
        ▲                 │
        └── 客服 reply 那条消息 ◄┘
```

## 3. 核心数据流
- **客户 → 群**：客户私聊机器人发任意消息 → 机器人在客服群先发一行身份头
  `👤 张三 (@zhangsan / id:123456)`，紧接着用 `copy_message` 把客户原消息复制进群
  （文本/图片/语音/视频/文件/贴纸/位置全支持）。
- **群 → 客户**：客服**长按客户那条消息选「回复」**再发内容 → 机器人识别 reply 的目标
  消息，从映射表查到对应客户，用 `copy_message` 把客服内容回传客户。
- **非 reply 的群内消息** → 忽略（视为客服内部讨论）。

## 4. 会话映射（关键）
MongoDB 集合 `dual_relay`，文档结构：
```
{ chat_msg_id: <客服群里那条被复制消息的 message_id>, customer_id: <客户 telegram id>, ts: <时间> }
```
- 转发客户消息时写入映射（key = copy 到群里后返回的 message_id）。
- 客服 reply 时用 `reply_to_message.message_id` 查 `customer_id`。
- 存 Mongo 而非内存 → 机器人重启后历史会话仍可回复。

## 5. 身份标识
最简一行头（昵称 + @用户名 + id），随每条客户消息前置发送。这是 `copy_message` 丢失发送者身份后的必需补偿，不是可选富信息卡。

## 6. 配置 / 前置条件
- 新建机器人，BotFather 拿 `DUAL_BOT_TOKEN`；**必须 `/setprivacy → Disable`**，否则收不到客服群回复。
- 客服群：把机器人拉进群，提供 `SUPPORT_GROUP_ID`（提供 `/id` 命令辅助获取）。
- 环境变量：`DUAL_BOT_TOKEN`、`SUPPORT_GROUP_ID`、`MONGODB_URL`（复用现有）。

## 7. 组件
- `dual_bot/config.py`：读取 token / 群 ID / Mongo URL。
- `dual_bot/db.py`：`dual_relay` 集合读写（save_map / find_customer）。
- `dual_bot/handlers.py`：
  - `on_customer_message`：私聊入站 → 发身份头 + copy 到群 + 存映射。
  - `on_group_reply`：客服群内、且是 reply → 查客户 → copy 回传。
  - `cmd_id`：在群里回 `/id` 返回当前 chat id（部署辅助）。
- `dual_bot/main.py`：注册 handler、启动 polling。
- `dual_bot/Dockerfile` + `requirements.txt`（`python-telegram-bot==20.3`，**不需要 job-queue**）。
- `docker-compose.yml` 增加 `dual-bot` 服务。

## 8. 错误处理
- copy 失败（客户拉黑机器人 / 群权限不足）→ 记日志，不崩溃。
- reply 的目标消息在映射表查不到 → 群内静默忽略（可能是客服自己聊天或老消息已过期）。

## 9. 本期不做（YAGNI）
欢迎语、拉黑/解黑、富信息卡、多客服分配、工单统计、自动回复。

## 10. 验证标准
- 客户私聊机器人发文字/图片 → 客服群出现身份头 + 内容。
- 客服 reply 该消息发文字/图片 → 客户私聊收到。
- 重启机器人后，对旧的群消息 reply 仍能正确回传。
- 客服在群里不 reply 直接发言 → 客户收不到。
