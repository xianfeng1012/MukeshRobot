# MukeshRobot 全面汉化设计文档

**日期：** 2026-06-15  
**状态：** 已批准，待实施

---

## 背景

MukeshRobot 是一个功能丰富的 Telegram 群组管理 + AI 机器人，基于 Python 编写，包含 120+ 个功能模块，约 23,000 行代码。所有用户可见字符串均为英文，需全面汉化。

---

## 目标

将项目中所有用户可见的英文字符串替换为中文，保留原有逻辑、结构和命令名不变。

---

## 汉化范围

### 纳入汉化
1. **`__mod_name__`** — 每个模块底部的模块名称（显示在帮助菜单）
2. **`__help__`** — 每个模块底部的帮助文档文本
3. **内联回复消息** — 函数体内所有 `reply_text()`、`send_message()`、`edit_text()` 等面向用户的字符串

### 排除在外
- 命令名（`/ban`、`/kick` 等，Telegram 不支持中文命令）
- 变量名、函数名、类名
- Telegram API 错误消息（如 `"User not found"`，由 API 返回）
- 开发者日志（`LOGGER.info()` 等）
- f-string 中的变量占位符（如 `{user.first_name}`）
- HTML/Markdown 格式标签（`<b>`、`<code>`、`*`、`_` 等）

---

## 方案：原地批量替换

直接在每个 `.py` 文件中替换字符串内容，不改变文件结构，不引入新的抽象层。

**每个模块处理步骤：**
1. 读取文件
2. 翻译 `__mod_name__`
3. 翻译 `__help__` 块
4. 翻译所有面向用户的内联字符串
5. 写回文件

---

## 风格规范

- **保留装饰符号**：`»`、`❍`、`*`、`_`、`**`、`—` 等原有符号标记保持不动
- **保留 Markdown/HTML 格式**：格式标签只翻译内容，不改变结构
- **语气忠实原文**：保留机器人的个性化语气，不做正式化处理
  - `"ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ."` → `"我怀疑那不是个用户。"`
  - `"ʏᴇᴘ, ɪ ʜᴀᴠᴇ ᴜɴʙᴀɴɴᴇᴅ ʏᴏᴜ."` → `"好的，我已经解封你了。"`

---

## 统一术语表

### 身份/权限
| 英文 | 中文 |
|------|------|
| Admin | 管理员 |
| Owner | 群主 |
| Bot | 机器人 |
| User | 用户 |
| Member | 成员 |
| Dragon (sudo) | 超级管理员 |
| Dev | 开发者 |
| Support | 支持人员 |

### 操作
| 英文 | 中文 |
|------|------|
| Ban / Banned | 封禁 / 已封禁 |
| Kick / Kicked | 踢出 / 已踢出 |
| Mute / Muted | 禁言 / 已禁言 |
| Warn / Warning | 警告 |
| Unban | 解封 |
| Unmute | 解除禁言 |
| Flood | 刷屏 |
| Blacklist | 黑名单 |
| Whitelist | 白名单 |
| Filter | 过滤器 |
| Note | 笔记 |
| Federation | 联邦 |
| Pin | 置顶 |
| Lock | 锁定 |
| Report | 举报 |
| Approve | 批准 |
| Rules | 群规 |
| Welcome | 欢迎 |

---

## 执行批次

### 第一批 — 核心群管（10 个模块）
`bans.py`、`admin.py`、`warns.py`、`welcome.py`、`muting.py`、`locks.py`、`flood.py`、`blacklist.py`、`notes.py`、`rules.py`

### 第二批 — 扩展群管（10 个模块）
`approve.py`、`feds.py`、`blacklistusers.py`、`blacklist_stickers.py`、`reporting.py`、`connection.py`、`cleaner.py`、`antiban.py`、`cust_filters.py`、`disable.py`

### 第三批 — 工具功能（~20 个模块）
`userinfo.py`、`users.py`、`translator.py`、`weather.py`、`wiki.py`、`currency_converter.py`、`webss.py`、`ud.py`、`whois.py`、`speed_test.py` 及其他工具模块

### 第四批 — AI + 娱乐 + 其余（~80 个模块）
`chatgpt.py`、`chatbot.py`、`aiimage.py`、`anime.py`、`fun.py`、`couples.py`、`truth_dare.py`、`dicegame.py` 及全部剩余模块

---

## 成功标准

- 所有 `__mod_name__` 值为中文
- 所有 `__help__` 块为中文
- 所有 `reply_text()`、`send_message()`、`edit_text()` 等的字符串参数为中文
- 命令名、变量名、逻辑代码无任何改动
- f-string 占位符和格式标签保持原样
