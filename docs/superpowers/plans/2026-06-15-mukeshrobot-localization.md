# MukeshRobot 全面汉化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 MukeshRobot 所有用户可见的英文字符串替换为中文，保留命令名、变量名、逻辑代码和格式标记不变。

**Architecture:** 原地批量替换策略——直接修改每个 `.py` 文件中的字符串，不引入新的抽象层。每个模块独立处理：先读文件，翻译 `__mod_name__`、`__help__` 和所有 `reply_text()`/`send_message()`/`edit_text()` 等面向用户的字符串，再写回。

**Tech Stack:** Python、Edit 工具、git

---

## 翻译规范（所有任务通用）

**保留不变：**
- 命令名：`/ban`、`/kick` 等
- 变量名、函数名
- f-string 中的占位符：`{user.first_name}`、`{chat.title}` 等
- HTML/Markdown 标签：`<b>`、`<code>`、`*`、`_` 等
- Telegram API 返回的错误消息：`"User not found"`、`"Chat_not_modified"` 等
- `LOGGER.` 开头的日志调用

**风格规则：**
- 保留装饰符号：`»`、`❍`、`‣`、`•`、`❕`、`☠`、`🥀`、`💫` 等
- 忠实原文语气，保留个性化口吻

**术语表：**
| 英文 | 中文 |
|------|------|
| Admin/Admins | 管理员 |
| Owner | 群主 |
| Bot | 机器人 |
| User | 用户 |
| Member | 成员 |
| Dragon (sudo) | 超级管理员 |
| Dev | 开发者 |
| Ban/Banned | 封禁/已封禁 |
| Kick/Kicked | 踢出/已踢出 |
| Mute/Muted | 禁言/已禁言 |
| Warn/Warning | 警告 |
| Unban | 解封 |
| Unmute | 解除禁言 |
| Flood | 刷屏 |
| Blacklist | 黑名单 |
| Filter | 过滤器 |
| Note | 笔记 |
| Federation | 联邦 |
| Pin/Pinned | 置顶/已置顶 |
| Lock/Unlock | 锁定/解锁 |
| Report | 举报 |
| Approve | 批准 |
| Rules | 群规 |
| Welcome/Goodbye | 欢迎/再见 |
| Promote/Demote | 晋升/降级 |
| Permissions | 权限 |
| Sticker | 贴纸 |
| Description | 简介 |

---

## 第一批：核心群管模块

### Task 1：汉化 bans.py

**Files:**
- Modify: `MukeshRobot/modules/bans.py`

- [ ] **Step 1: 修改 bans.py 中的所有用户可见字符串**

编辑 `MukeshRobot/modules/bans.py`，完整替换如下（只改字符串内容，不改逻辑）：

```python
# 第 51 行
"ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ."
# 改为：
"我怀疑那不是个用户。"

# 第 58 行
"ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴘᴇʀsᴏɴ."
# 改为：
"好像找不到这个人。"

# 第 61 行
"ᴏʜ ʏᴇᴀʜ, ʙᴀɴ ᴍʏsᴇʟғ, ɴᴏᴏʙ!"
# 改为：
"哦对，封禁我自己，菜鸟！"

# 第 66 行
"ᴛʀʏɪɴɢ ᴛᴏ ᴘᴜᴛ ᴍᴇ ᴀɢᴀɪɴsᴛ ᴀ ɢᴏᴅ ʟᴇᴠᴇʟ ᴅɪsᴀsᴛᴇʀ ʜᴜʜ?"
# 改为：
"想让我对付神级灾害？"

# 第 68 行
"ɪ ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴀɢᴀɪɴsᴛ ᴏᴜʀ ᴏᴡɴ."
# 改为：
"我不能对自己人动手。"

# 第 71 行
"ғɪɢʜᴛɪɴɢ ᴛʜɪs ᴅʀᴀɢᴏɴ ʜᴇʀᴇ ᴡɪʟʟ ᴘᴜᴛ ᴄɪᴠɪʟɪᴀɴ ʟɪᴠᴇs ᴀᴛ ʀɪsᴋ."
# 改为：
"在这里与这条龙战斗会危及平民生命。"

# 第 75 行
"ʙʀɪɴɢ ᴀɴ ᴏʀᴅᴇʀ ғʀᴏᴍ ʜᴇʀᴏᴇs ᴀssᴏᴄɪᴀᴛɪᴏɴ ᴛᴏ ғɪɢʜᴛ ᴀ ᴅᴇᴍᴏɴ ᴅɪsᴀsᴛᴇʀ."
# 改为：
"请先拿到英雄协会的命令再来对付恶魔级灾害。"

# 第 79 行
"ʙʀɪɴɢ ᴀɴ ᴏʀᴅᴇʀ ғʀᴏᴍ ʜᴇʀᴏᴇs ᴀssᴏᴄɪᴀᴛɪᴏɴ ᴛᴏ ғɪɢʜᴛ ᴀ ᴛɪɢᴇʀ ᴅɪsᴀsᴛᴇʀ."
# 改为：
"请先拿到英雄协会的命令再来对付虎级灾害。"

# 第 82-84 行（两处）
"ᴡᴏʟғ ᴀʙɪʟɪᴛɪᴇs ᴍᴀᴋᴇ ᴛʜᴇᴍ ʙᴀɴ ɪᴍᴍᴜɴᴇ!"
# 改为：
"狼级能力使他们免疫封禁！"

# 第 94 行（f-string 内标签）
f"#{'S' if silent else ''}ʙᴀɴɴᴇᴅ\n"
# 改为：
f"#{'静默' if silent else ''}已封禁\n"

# 第 95 行（f-string 内标签）
f"<b>ʙᴀɴɴᴇᴅ ʙʏ:</b> ..."
# 改为：
f"<b>封禁者:</b> ..."

# 第 96 行
f"<b>ᴜsᴇʀ:</b> ..."
# 改为：
f"<b>用户:</b> ..."

# 第 99 行
log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)
# 改为：
log += "\n<b>原因:</b> {}".format(reason)

# 第 112-114 行（ban 事件回复）
f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"
f"<code> </code><b>•  ʙᴀɴɴᴇᴅ ʙʏ:</b> ..."
f"<code> </code><b>•  ᴜsᴇʀ:</b> ..."
# 改为：
f"<code>❕</code><b>封禁事件</b>\n"
f"<code> </code><b>•  封禁者:</b> ..."
f"<code> </code><b>•  用户:</b> ..."

# 第 117 行
reply += f"\n<code> </code><b>•  ʀᴇᴀsᴏɴ:</b> \n{html.escape(reason)}"
# 改为：
reply += f"\n<code> </code><b>•  原因:</b> \n{html.escape(reason)}"

# 第 126 行
message.reply_text("ʙᴀɴɴᴇᴅ !", quote=False)
# 改为：
message.reply_text("已封禁！", quote=False)

# 第 137 行
message.reply_text("ᴜʜᴍ ...ᴛʜᴀᴛ ᴅɪᴅɴ'ᴛ ᴡᴏʀᴋ ..")
# 改为：
message.reply_text("呃……好像没成功……")

# 第 157 行（temp_ban）
"ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ."  →  "我怀疑那不是个用户。"

# 第 165 行
"ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ."  →  "好像找不到这个用户。"

# 第 168 行
"ɪ'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ʙᴀɴ ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?"  →  "我才不会封禁自己，你疯了吗？"

# 第 172 行
"ɪ ᴅᴏɴ'ᴛ ғᴇᴇʟ ʟɪᴋᴇ ɪᴛ."  →  "我不想这么做。"

# 第 176 行
"ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴀ ᴛɪᴍᴇ ᴛᴏ ʙᴀɴ ᴛʜɪs ᴜsᴇʀ ғᴏʀ!"  →  "你还没有指定封禁这个用户多长时间！"

# 第 190 行（f-string 内标签）
"ᴛᴇᴍᴩ ʙᴀɴ\n"  →  "临时封禁\n"
f"<b>ʙᴀɴɴᴇᴅ ʙʏ:</b> ..."  →  f"<b>封禁者:</b> ..."
f"<b>ᴜsᴇʀ:</b> ..."  →  f"<b>用户:</b> ..."
f"<b>ᴛɪᴍᴇ:</b> {time_val}"  →  f"<b>时长:</b> {time_val}"
"\n<b>ʀᴇᴀsᴏɴ:</b> {}"  →  "\n<b>原因:</b> {}"

# 第 203-204 行
f"ʙᴀɴɴᴇᴅ! ᴜsᴇʀ {mention_html(...)} ɪs ɴᴏᴡ ʙᴀɴɴᴇᴅ ғᴏʀ {time_val}."
# 改为：
f"已封禁！用户 {mention_html(...)} 现已被封禁 {time_val}。"

# 第 213 行
f"ʙᴀɴɴᴇᴅ! ᴜsᴇʀ ᴡɪʟʟ ʙᴇ  ʙᴀɴɴᴇᴅ ғᴏʀ  {time_val}."  →  f"已封禁！该用户将被封禁 {time_val}。"

# 第 225 行
"ᴡᴇʟʟ ᴅᴀᴍɴ, ɪ ᴄᴀɴ'ᴛ ʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ."  →  "妈呀，我封禁不了这个用户。"

# kick 函数各处
"ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ."  →  "我怀疑那不是个用户。"
"ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ."  →  "好像找不到这个用户。"
"ʏᴇᴀʜʜʜ ɪ'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴅᴏ ᴛʜᴀᴛ."  →  "是的我才不要那样做。"
"I really wish I could kick this user...."  →  "我真希望能踢掉这个用户……"
f"One Kicked! {mention_html(...)}."  →  f"踢出一人！{mention_html(...)}。"
f"ᴋɪᴄᴋᴇᴅ\n"  →  "已踢出\n"
f"<b>ᴋɪᴄᴋᴇᴅ ʙʏ:</b> ..."  →  f"<b>踢出者:</b> ..."
f"<b>ᴜsᴇʀ:</b> ..."  →  f"<b>用户:</b> ..."
f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"  →  f"\n<b>原因:</b> {reason}"
"ᴡᴇʟʟ ᴅᴀᴍɴ, ɪ ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ᴛʜᴀᴛ ᴜsᴇʀ."  →  "妈呀，我踢不了这个用户。"

# kickme 函数
"ɪ ᴡɪsʜ ɪ ᴄᴏᴜʟᴅ... ʙᴜᴛ ʏᴏᴜ'ʀᴇ ᴀɴ ᴀᴅᴍɪɴ."  →  "我希望可以……但你是管理员。"
"*ᴋɪᴄᴋs ʏᴏᴜ ᴏᴜᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴘ*"  →  "*把你踢出了群组*"
"ʜᴜʜ? ɪ ᴄᴀɴ'ᴛ :/"  →  "啊？我做不到:/"

# unban 函数
"ɪ ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ."  →  "我怀疑那不是个用户。"
"ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ."  →  "好像找不到这个用户。"
"ʜᴏᴡ ᴡᴏᴜʟᴅ ɪ ᴜɴʙᴀɴ ᴍʏsᴇʟғ ɪғ ɪ ᴡᴀsɴ'ᴛ ʜᴇʀᴇ...?"  →  "如果我不在这里，我怎么解封自己……？"
"ɪsɴ'ᴛ ᴛʜɪs ᴘᴇʀsᴏɴ ᴀʟʀᴇᴀᴅʏ ʜᴇʀᴇ??"  →  "这个人不是已经在群里了吗？"
"Yep, this user can join!"  →  "好的，这个用户可以加入了！"
f"ᴜɴʙᴀɴɴᴇᴅ\n"  →  "已解封\n"
f"<b>ᴜɴʙᴀɴɴᴇᴅ ʙʏ:</b> ..."  →  f"<b>解封者:</b> ..."
f"<b>ᴜsᴇʀ:</b> ..."  →  f"<b>用户:</b> ..."
f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"  →  f"\n<b>原因:</b> {reason}"

# selfunban 函数
"ɢɪᴠᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ."  →  "请提供有效的聊天 ID。"
"ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ."  →  "好像找不到这个用户。"
"ᴀʀᴇɴ'ᴛ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ??"  →  "你不是已经在这个聊天里了吗？"
"ʏᴇᴘ, ɪ ʜᴀᴠᴇ ᴜɴʙᴀɴɴᴇᴅ ʏᴏᴜ."  →  "好的，我已经解封你了。"

# __help__ 块（第 397-406 行）
__help__ = """
 ❍ /kickme *:* 踢出发出该命令的用户

*仅管理员:*
 ❍ /ban <用户名>*:* 封禁一个用户。（通过用户名或回复）
 ❍ /sban  <用户名>*:* 静默封禁一个用户。删除命令、被回复的消息，且不回复。（通过用户名或回复）
 ❍ /tban  <用户名> x(m/h/d)*:* 封禁用户 `x` 时长。（通过用户名或回复）。`m` = `分钟`，`h` = `小时`，`d` = `天`。
 ❍ /unban  <用户名>*:* 解封一个用户。（通过用户名或回复）
 ❍ /kick <用户名>*:* 将用户踢出群组。（通过用户名或回复）
"""

# __mod_name__（第 424 行）
__mod_name__ = "封禁"
```

- [ ] **Step 2: 提交更改**

```bash
git add MukeshRobot/modules/bans.py
git commit -m "i18n: 汉化 bans.py"
```

---

### Task 2：汉化 admin.py

**Files:**
- Modify: `MukeshRobot/modules/admin.py`

- [ ] **Step 1: 修改 admin.py 中的所有用户可见字符串**

替换规则（逐行读文件，按如下映射替换）：

```
"» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ ʙᴀʙʏ !"
→ "» 你没有权限更改群组信息！"

"» ʀᴇᴩʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɢʀᴏᴜᴩ sᴛɪᴄᴋᴇʀ ᴩᴀᴄᴋ !"
→ "» 请回复一个贴纸以将其设置为群组贴纸包！"

f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɢʀᴏᴜᴩ sᴛɪᴄᴋᴇʀs ɪɴ {chat.title}!"
→ f"» 已成功设置 {chat.title} 的群组贴纸！"

"» ʏᴏᴜʀ ɢʀᴏᴜᴩ ɴᴇᴇᴅs ᴍɪɴɪᴍᴜᴍ 100 ᴍᴇᴍʙᴇʀs ғᴏʀ sᴇᴛᴛɪɴɢ ᴀ sᴛɪᴄᴋᴇʀ ᴩᴀᴄᴋ ᴀs ɢʀᴏᴜᴩ sᴛɪᴄᴋᴇʀ ᴩᴀᴄᴋ !"
→ "» 你的群组需要至少 100 名成员才能设置群组贴纸包！"

f"ᴇʀʀᴏʀ ! {excp.message}."  →  f"错误！{excp.message}。"
f"ᴇʀʀᴏʀ ! {excp.message}"  →  f"错误！{excp.message}"

"» ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ ᴩʜᴏᴛᴏs ᴀs ɢʀᴏᴜᴩ ᴩғᴩ !"  →  "» 你只能将图片设置为群组头像！"
"» ᴄʜᴀɴɢɪɴɢ ɢʀᴏᴜᴩ's ᴩʀᴏғɪʟᴇ ᴩɪᴄ..."  →  "» 正在更换群组头像……"
"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɢʀᴏᴜᴩ ᴩʀᴏғɪʟᴇ ᴩɪᴄ !"  →  "» 已成功设置群组头像！"
"» ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴩʜᴏᴛᴏ ᴏʀ ғɪʟᴇ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɢʀᴏᴜᴩ ᴩʀᴏғɪʟᴇ ᴩɪᴄ !"  →  "» 请回复一张图片或文件以将其设置为群组头像！"
"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ɢʀᴏᴜᴩ's ᴅᴇғᴀᴜʟᴛ ᴩʀᴏғɪʟᴇ ᴩɪᴄ !"  →  "» 已成功删除群组头像！"
"» ᴡᴛғ, ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴛ ᴀɴ ᴇᴍᴩᴛʏ ᴅᴇsᴄʀɪᴩᴛɪᴏɴ !"  →  "» 什么？你想设置一个空简介！"
"» ᴅᴇsᴄʀɪᴩᴛɪᴏɴ ᴍᴜsᴛ ʙᴇ ʟᴇss ᴛʜᴀɴ 255 ᴡᴏʀᴅs ᴏʀ ᴄʜᴀʀᴀᴄᴛᴇʀs !"  →  "» 简介不能超过 255 个字符！"
f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴩᴅᴀᴛᴇᴅ ᴄʜᴀᴛ ᴅᴇsᴄʀɪᴩᴛɪᴏɴ ɪɴ {chat.title}!"  →  f"» 已成功更新 {chat.title} 的聊天简介！"
"» ᴇɴᴛᴇʀ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ !"  →  "» 请输入新的聊天标题！"
f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ <b>{title}</b> ᴀs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ !"  →  f"» 已成功将 <b>{title}</b> 设置为新的聊天标题！"
"» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴀᴅᴅ ɴᴇᴡ ᴀᴅᴍɪɴs ʙᴀʙʏ !"  →  "» 你没有权限添加新管理员！"
"» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ's ᴛʜᴀᴛ ᴜsᴇʀ, ɴᴇᴠᴇʀ sᴇᴇɴ ʜɪᴍ ɪɴ ᴀɴʏ ᴏғ ᴛʜᴇ ᴄʜᴀᴛs ᴡʜᴇʀᴇ ɪ ᴀᴍ ᴩʀᴇsᴇɴᴛ !"  →  "» 我不知道那个用户是谁，在我所在的群里从没见过他！"
"» ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍᴇ ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ ʜᴇʀᴇ !"  →  "» 在我看来那个用户已经是管理员了！"
"» ɪ ᴄᴀɴ'ᴛ ᴩʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ, ᴍʏ ᴏᴡɴᴇʀ ᴅɪᴅɴ'ᴛ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ᴅᴏ sᴏ."  →  "» 我不能晋升自己，我的主人没叫我这么做。"
"» ᴀs ɪ ᴄᴀɴ sᴇᴇ ᴛʜᴀᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ᴩʀᴇsᴇɴᴛ ʜᴇʀᴇ."  →  "» 我看这个用户不在这里。"
"» sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ, ᴍᴀʏʙᴇ sᴏᴍᴇᴏɴᴇ ᴩʀᴏᴍᴏᴛᴇᴅ ᴛʜᴀᴛ ᴜsᴇʀ ʙᴇғᴏʀᴇ ᴍᴇ."  →  "» 出了点问题，也许有人在我之前已经晋升了那个用户。"
f"<b>» ᴩʀᴏᴍᴏᴛɪɴɢ ᴀ ᴜsᴇʀ ɪɴ</b> {chat.title}\n\nᴩʀᴏᴍᴏᴛᴇᴅ : ...\nᴩʀᴏᴍᴏᴛᴇʀ : ..."
→ f"<b>» 在</b> {chat.title} <b>晋升用户</b>\n\n晋升者: ...\n操作者: ..."
f"#ᴩʀᴏᴍᴏᴛᴇᴅ\n"  →  "#已晋升\n"
f"<b>ᴩʀᴏᴍᴏᴛᴇʀ :</b> ..."  →  f"<b>操作者:</b> ..."
f"<b>ᴜsᴇʀ :</b> ..."  →  f"<b>用户:</b> ..."
# lowpromote 同上模式
f"<b>» ʟᴏᴡ ᴩʀᴏᴍᴏᴛɪɴɢ ᴀ ᴜsᴇʀ ɪɴ </b>{chat.title}..."  →  f"<b>» 在 {chat.title} 低权限晋升用户</b>..."
f"#ʟᴏᴡᴩʀᴏᴍᴏᴛᴇᴅ\n"  →  "#低权限晋升\n"
# fullpromote
f"» ғᴜʟʟᴩʀᴏᴍᴏᴛɪɴɢ ᴀ ᴜsᴇʀ ɪɴ <b>{chat.title}</b>..."  →  f"» 在 <b>{chat.title}</b> 完全晋升用户..."
f"#ғᴜʟʟᴩʀᴏᴍᴏᴛᴇᴅ\n"  →  "#完全晋升\n"
# demote
"» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴀɴᴅ ɪ ᴅᴏɴ'ᴛ ᴡᴀɴᴛ ᴛᴏ ᴩᴜᴛ ᴍʏsᴇʟғ ɪɴ ᴅᴀɴɢᴇʀ."  →  "» 那个用户是群主，我不想让自己陷入危险。"
"» ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍᴇ ᴛʜᴀᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ʜᴇʀᴇ !"  →  "» 在我看来那个用户在这里不是管理员！"
"» ɪ ᴄᴀɴ'ᴛ ᴅᴇᴍᴏᴛᴇ ᴍʏsᴇʟғ, ʙᴜᴛ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ɪ ᴄᴀɴ ʟᴇᴀᴠᴇ."  →  "» 我不能降级自己，但如果你想，我可以退群。"
f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇᴍᴏᴛᴇᴅ ᴀ ᴀᴅᴍɪɴ ɪɴ <b>{chat.title}</b>..."  →  f"» 已成功降级 <b>{chat.title}</b> 中的管理员..."
"ᴅᴇᴍᴏᴛᴇᴅ :"  →  "被降级:"
"ᴅᴇᴍᴏᴛᴇʀ :"  →  "操作者:"
f"#ᴅᴇᴍᴏᴛᴇᴅ\n"  →  "#已降级\n"
"» ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴇᴍᴏᴛᴇ ᴍᴀʏʙᴇ ɪ'ᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ᴏʀ ᴍᴀʏʙᴇ sᴏᴍᴇᴏɴᴇ ᴇʟsᴇ ᴩʀᴏᴍᴏᴛᴇᴅ ᴛʜᴀᴛ ᴜsᴇʀ !"  →  "» 降级失败，也许我不是管理员，或者是别人晋升了那个用户！"
"» sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇғʀᴇsʜᴇᴅ ᴀᴅᴍɪɴ ᴄᴀᴄʜᴇ !"  →  "» 已成功刷新管理员缓存！"
# set_title
"» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴀɴᴅ ɪ ᴅᴏɴ'ᴛ ᴡᴀɴᴛ ᴛᴏ ᴩᴜᴛ ᴍʏsᴇʟғ ɪɴ ᴅᴀɴɢᴇʀ."  →  "» 那个用户是群主，我不想让自己陷入危险。"
"» ɪ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ ᴀᴅᴍɪɴs !"  →  "» 我只能给管理员设置头衔！"
"» ɪ ᴄᴀɴ'ᴛ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ ᴍʏsᴇʟғ, ᴍʏ ᴏᴡɴᴇʀ ᴅɪᴅɴ'ᴛ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ᴅᴏ sᴏ."  →  "» 我不能给自己设置头衔，我的主人没叫我这么做。"
"» ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜᴀᴛ sᴇᴛᴛɪɴɢ ʙʟᴀɴᴋ ᴛɪᴛʟᴇ ᴡɪʟʟ ᴄʜᴀɴɢᴇ sᴏᴍᴇᴛʜɪɴɢ ?"  →  "» 你觉得设置空头衔会有什么用吗？"
"» ᴛʜᴇ ᴛɪᴛʟᴇ ʟᴇɴɢᴛʜ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ 16 ᴡᴏʀᴅs ᴏʀ ᴄʜᴀʀᴀᴄᴛᴇʀs sᴏ ᴛʀᴜɴᴄᴀᴛɪɴɢ ɪᴛ ᴛᴏ 16 ᴡᴏʀᴅs."  →  "» 头衔超过 16 个字符，将自动截断。"
"» ᴍᴀʏʙᴇ ᴛʜᴀᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ᴩʀᴏᴍᴏᴛᴇᴅ ʙʏ ᴍᴇ ᴏʀ ᴍᴀʏʙᴇ ʏᴏᴜ sᴇɴᴛ sᴏᴍᴇᴛʜɪɴɢ ᴛʜᴀᴛ ᴄᴀɴ'ᴛ ʙᴇ sᴇᴛ ᴀs ᴛɪᴛʟᴇ."  →  "» 可能那个用户不是由我晋升的，或者你发送了不能用作头衔的内容。"
f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ <code>...</code> ᴛᴏ <code>...</code>!"  →  f"» 已成功将 <code>...</code> 的头衔设置为 <code>...</code>！"
# pin/unpin
"» ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴩɪɴ ɪᴛ !"  →  "» 请回复一条消息以置顶！"
f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴩɪɴɴᴇᴅ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ.\nᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ᴍᴇssᴀɢᴇ."  →  f"» 已成功置顶该消息。\n点击下方按钮查看消息。"
InlineKeyboardButton("ᴍᴇssᴀɢᴇ", ...)  →  InlineKeyboardButton("查看消息", ...)
"ᴩɪɴɴᴇᴅ-ᴀ-ᴍᴇssᴀɢᴇ\n"  →  "已置顶消息\n"
f"<b>ᴩɪɴɴᴇᴅ ʙʏ :</b> ..."  →  f"<b>置顶者:</b> ..."
"» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴩɪɴ/ᴜɴᴩɪɴ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ !"  →  "» 你没有权限在此聊天中置顶/取消置顶消息！"
f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴᴩɪɴɴᴇᴅ <a href=...> ᴛʜɪs ᴩɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ</a>."  →  f"» 已成功取消置顶 <a href=...>此消息</a>。"
"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴᴩɪɴɴᴇᴅ ᴛʜᴇ ʟᴀsᴛ ᴩɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ."  →  "» 已成功取消最后一条置顶消息。"
"» ɪ ᴄᴀɴ'ᴛ ᴜɴᴩɪɴ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ, ᴍᴀʏʙᴇ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ɪs ᴛᴏᴏ ᴏʟᴅ ᴏʀ ᴍᴀʏʙᴇ sᴏᴍᴇᴏɴᴇ ᴀʟʀᴇᴀᴅʏ ᴜɴᴩɪɴɴᴇᴅ ɪᴛ."  →  "» 我无法取消那条消息的置顶，也许消息太旧了，或者已被他人取消置顶。"
"ᴜɴᴩɪɴɴᴇᴅ-ᴀ-ᴍᴇssᴀɢᴇ\n"  →  "已取消置顶消息\n"
f"<b>ᴜɴᴩɪɴɴᴇᴅ ʙʏ :</b> ..."  →  f"<b>操作者:</b> ..."
f"ᴩɪɴɴᴇᴅ ᴏɴ {html.escape(chat.title)}."  →  f"置顶于 {html.escape(chat.title)}。"
InlineKeyboardButton(text="ᴍᴇssᴀɢᴇ", ...)  →  InlineKeyboardButton(text="查看消息", ...)
f"» ᴛʜᴇʀᴇ's ɴᴏ ᴩɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ <b>{html.escape(chat.title)}!</b>"  →  f"» <b>{html.escape(chat.title)}</b> 中没有置顶消息！"
# invite
"» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴀᴄᴄᴇss ɪɴᴠɪᴛᴇ ʟɪɴᴋs !"  →  "» 我没有权限访问邀请链接！"
"» ɪ ᴄᴀɴ ᴏɴʟʏ ɢɪᴠᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋs ғᴏʀ ɢʀᴏᴜᴩs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs !"  →  "» 我只能提供群组和频道的邀请链接！"
# adminlist
"» ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ɪɴ ɢʀᴏᴜᴩ's ɴᴏᴛ ɪɴ ᴩᴍ."  →  "» 此命令只能在群组中使用，不能在私聊中使用。"
"» ғᴇᴛᴄʜɪɴɢ ᴀᴅᴍɪɴs ʟɪsᴛ..."  →  "» 正在获取管理员列表……"
"ᴀᴅᴍɪɴs ɪɴ <b>{}</b>:"  →  "<b>{}</b> 的管理员列表:"
"☠ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ"  →  "☠ 已注销账号"
"🥀 ᴏᴡɴᴇʀ :"  →  "🥀 群主:"
"💫 ᴀᴅᴍɪɴs :"  →  "💫 管理员:"
# __help__
__help__ = """
*用户命令*:
» /admins*:* 查看群内管理员列表
» /pinned*:* 获取当前置顶消息

*以下命令仅限管理员:*
» /pin*:* 静默置顶所回复的消息 - 加上 `'loud'` 或 `'notify'` 可通知用户
» /unpin*:* 取消当前置顶消息
» /invitelink*:* 获取邀请链接
» /promote*:* 晋升所回复的用户
» /lowpromote*:* 以半权限晋升所回复的用户
» /fullpromote*:* 以全权限晋升所回复的用户
» /demote*:* 降级所回复的用户
» /title <头衔>*:* 为机器人晋升的管理员设置自定义头衔
» /admincache*:* 强制刷新管理员列表
» /del*:* 删除所回复的消息
» /purge*:* 删除本消息到所回复消息之间的所有消息
» /purge <整数 X>*:* 如回复某条消息，则删除该消息及其后 X 条消息
» /setgtitle <文本>*:* 设置群组标题
» /setgpic*:* 回复一张图片以设置为群组头像
» /setdesc*:* 设置群组简介
» /setsticker*:* 设置群组贴纸
"""

# __mod_name__
__mod_name__ = "管理员"
```

- [ ] **Step 2: 提交更改**

```bash
git add MukeshRobot/modules/admin.py
git commit -m "i18n: 汉化 admin.py"
```

---

### Task 3：汉化 warns.py

**Files:**
- Modify: `MukeshRobot/modules/warns.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射：

```
"Tigers cant be warned."  →  "虎级用户不能被警告。"
"Tiger triggered an auto warn filter!\n I can't warn tigers but they should avoid abusing this."
→  "虎级用户触发了自动警告过滤器！\n我不能警告虎级用户，但他们应该避免滥用这一点。"
"Wolf disasters are warn immune."  →  "狼级灾害免疫警告。"
"Wolf Disaster triggered an auto warn filter!\nI can't warn wolves but they should avoid abusing this."
→  "狼级灾害触发了自动警告过滤器！\n我不能警告狼级用户，但他们应该避免滥用这一点。"

# 以及 warns.py 中所有其他 reply_text/send_message 字符串
# 包括警告计数消息、警告限制消息、__help__ 和 __mod_name__

__mod_name__ = "警告"

__help__ = """
*仅管理员:*
 ❍ /warn <用户名>*:* 警告用户。累计到警告上限后将自动处罚。
 ❍ /dwarn <用户名>*:* 警告用户并删除触发警告的消息。
 ❍ /resetwarn <用户名>*:* 重置用户的警告次数。
 ❍ /addwarn <关键词> <回复内容>*:* 设置触发词，命中时自动发出警告。
 ❍ /nowarn <关键词>*:* 停止对某关键词的警告。
 ❍ /warnlimit <数量>*:* 设置警告上限。
 ❍ /strongwarn <开/关>*:* 开启时，超过警告上限将封禁而非踢出。
 ❍ /warns <用户名>*:* 查看某用户的警告次数及原因。
 ❍ /warnlist*:* 列出所有自动警告触发词。
"""
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/warns.py
git commit -m "i18n: 汉化 warns.py"
```

---

### Task 4：汉化 welcome.py

**Files:**
- Modify: `MukeshRobot/modules/welcome.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射（welcome.py 约 1130 行，字符串分散）：

```
# __mod_name__
__mod_name__ = "欢迎"

# __help__ 末尾块
__help__ = """
 ❍ /welcome <开/关>*:* 开启或关闭欢迎消息。
 ❍ /welcome*:* 显示当前欢迎消息设置。
 ❍ /welcome noformat*:* 显示无格式的欢迎消息——便于回收利用。
 ❍ /goodbye*:* 类似 /welcome，但针对离开消息。
 ❍ /setwelcome <欢迎内容>*:* 设置自定义欢迎消息。支持 Markdown、按钮和媒体。
 ❍ /setgoodbye <再见内容>*:* 设置自定义再见消息。支持 Markdown、按钮和媒体。
 ❍ /resetwelcome*:* 恢复默认欢迎消息。
 ❍ /resetgoodbye*:* 恢复默认再见消息。
 ❍ /cleanwelcome <开/关>*:* 有新成员加入时，尝试删除上一条欢迎消息以避免刷屏。
 ❍ /welcomemutehelp*:* 显示欢迎静音的相关信息。
 ❍ /cleanservice <开/关>*:* 删除 Telegram 的加入/离开服务消息。
 ❍ /welcomehelp*:* 查看自定义欢迎/再见消息的更多格式说明。
"""

# 内联消息（逐行扫描 welcome.py 中的所有 reply_text/send_message 调用）
# 示例：
"» ʟᴏᴄᴋᴇᴅ ᴍᴇssᴀɢᴇ..."  →  按实际含义翻译
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/welcome.py
git commit -m "i18n: 汉化 welcome.py"
```

---

### Task 5：汉化 muting.py

**Files:**
- Modify: `MukeshRobot/modules/muting.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射：

```
"This user is already muted."  →  "该用户已经被禁言了。"
f"Muted for {time_val}!"  →  f"已禁言 {time_val}！"
"Well damn, I can't mute that user."  →  "妈呀，我禁言不了这个用户。"

__mod_name__ = "禁言"

__help__ = """
*仅管理员:*
 ❍ /mute  <用户名>*:* 对用户禁言。也可通过回复使用，对被回复用户禁言。
 ❍ /tmute  <用户名> x(m/h/d)*:* 禁言用户 x 时长。（通过用户名或回复）。`m`=分钟，`h`=小时，`d`=天。
 ❍ /unmute <用户名>*:* 解除用户禁言。也可通过回复使用。
 ❍ /dmute <用户名>*:* 禁言用户并删除触发消息。也可通过回复使用。
"""
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/muting.py
git commit -m "i18n: 汉化 muting.py"
```

---

### Task 6：汉化 locks.py

**Files:**
- Modify: `MukeshRobot/modules/locks.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射：

```
__mod_name__ = "锁定"

__help__ = """
贴纸让你烦恼？或者想阻止人们分享链接？或者图片？你来对地方了！
锁定模块允许你锁定 Telegram 中的某些内容类型；机器人会自动删除它们！

 ❍ /locktypes *:* 列出所有可锁定的类型

*仅管理员:*
 ❍ /lock  <类型>*:* 锁定某类型的内容（不可在私聊中使用）
 ❍ /unlock  <类型>*:* 解锁某类型的内容（不可在私聊中使用）
 ❍ /locks *:* 查看此群的当前锁定列表

锁定功能可用于限制群组用户。
例如：
锁定 urls 后将自动删除所有含链接的消息，锁定 stickers 后将禁止非管理员发送贴纸，等等。
锁定 bots 后将阻止非管理员向群组添加机器人。

*注意:*
 • 解锁权限 *info* 将允许成员（非管理员）更改群组信息，如简介或群名
 • 解锁权限 *pin* 将允许成员（非管理员）在群组中置顶消息
"""
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/locks.py
git commit -m "i18n: 汉化 locks.py"
```

---

### Task 7：汉化 flood.py

**Files:**
- Modify: `MukeshRobot/modules/flood.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射：

```
__mod_name__ = "防刷屏"

# flood.py 中的内联消息（读文件后逐一替换）
# 示例：
"No flood control in this chat."  →  "此群尚未开启防刷屏。"
"Flood control set to {} messages."  →  "防刷屏已设置为 {} 条消息。"

__help__ = """
 ❍ /flood*:* 获取当前防刷屏设置

*仅管理员:*
 ❍ /setflood <数量/关闭>*:* 开启或关闭刷屏控制。设置为 0 或 'off' 表示关闭。
 ❍ /setfloodmode <封禁/踢出/禁言/tban/tmute> <时间值>*:* 设置达到刷屏上限后的处罚方式。
"""
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/flood.py
git commit -m "i18n: 汉化 flood.py"
```

---

### Task 8：汉化 blacklist.py

**Files:**
- Modify: `MukeshRobot/modules/blacklist.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射：

```
__mod_name__ = "黑名单"

__help__ = """
 ❍ /blacklist*:* 查看当前黑名单词语

*仅管理员:*
 ❍ /addblacklist <触发词>*:* 将词语添加到黑名单。每行一个词。
 ❍ /unblacklist <触发词>*:* 从黑名单中移除词语。每行一个词。
 ❍ /blacklistmode <关闭/删除/警告/禁言/踢出/封禁/封禁贴纸>*:* 设置命中黑名单时的处罚方式。默认为删除。
"""
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/blacklist.py
git commit -m "i18n: 汉化 blacklist.py"
```

---

### Task 9：汉化 notes.py

**Files:**
- Modify: `MukeshRobot/modules/notes.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射：

```
__mod_name__ = "笔记"

__help__ = """
 ❍ /get <笔记名>*:* 获取该名称的笔记
 ❍ #<笔记名>*:* 同 /get
 ❍ /notes 或 /saved*:* 列出此群的所有已保存笔记

*仅管理员:*
 ❍ /save <笔记名> <内容>*:* 将内容保存为指定名称的笔记。
可用标准 Markdown 链接语法添加按钮，链接前加 `buttonurl:` 前缀，如：`[链接文本](buttonurl:example.com)`。
 ❍ /save <笔记名>*:* 将被回复的消息保存为笔记
 ❍ /clear <笔记名>*:* 删除该名称的笔记
 ❍ /removeallnotes*:* 删除群内所有笔记
 *注意:* 笔记名不区分大小写，保存前会自动转换为小写。
"""
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/notes.py
git commit -m "i18n: 汉化 notes.py"
```

---

### Task 10：汉化 rules.py

**Files:**
- Modify: `MukeshRobot/modules/rules.py`

- [ ] **Step 1: 读取文件，替换所有用户可见字符串**

关键字符串映射：

```
__mod_name__ = "群规"

__help__ = """
 ‣ `/rules`*:* 获取此群的群规。
 ‣ `/rules here`*:* 在群内直接发送群规。
*仅管理员:*
 ‣ `/setrules <群规内容>`*:* 设置此群的群规。
 ‣ `/clearrules`*:* 清除此群的群规。
"""
```

- [ ] **Step 2: 提交**

```bash
git add MukeshRobot/modules/rules.py
git commit -m "i18n: 汉化 rules.py"
```

---

### Task 11：提交第一批完成

- [ ] **Step 1: 确认第一批所有模块已完成**

```bash
git log --oneline -10
```

期望看到 10 条 `i18n:` 提交记录。

---

## 第二批：扩展群管模块

### Task 12-21：汉化第二批模块

对以下每个模块，重复"读文件 → 翻译所有用户可见字符串 → 写回 → 提交"流程：

| Task | 文件 | __mod_name__ |
|------|------|--------------|
| 12 | `MukeshRobot/modules/approve.py` | `"批准"` |
| 13 | `MukeshRobot/modules/feds.py` | `"联邦"` |
| 14 | `MukeshRobot/modules/blacklistusers.py` | `"用户黑名单"` |
| 15 | `MukeshRobot/modules/blacklist_stickers.py` | `"贴纸黑名单"` |
| 16 | `MukeshRobot/modules/reporting.py` | `"举报"` |
| 17 | `MukeshRobot/modules/connection.py` | `"远程连接"` |
| 18 | `MukeshRobot/modules/cleaner.py` | `"清理"` |
| 19 | `MukeshRobot/modules/antiban.py` | `"防封号"` |
| 20 | `MukeshRobot/modules/cust_filters.py` | `"自定义过滤器"` |
| 21 | `MukeshRobot/modules/disable.py` | `"禁用命令"` |

**每个模块的步骤：**

- [ ] 读取文件（使用 Read 工具）
- [ ] 翻译所有 `reply_text()`、`send_message()`、`edit_text()` 字符串
- [ ] 翻译 `__help__` 块
- [ ] 修改 `__mod_name__`
- [ ] 写回文件（使用 Edit 工具）
- [ ] 提交：`git commit -m "i18n: 汉化 <文件名>"`

---

## 第三批：工具功能模块

### Task 22-31：汉化第三批模块

对以下每个模块，重复"读 → 翻译 → 写 → 提交"流程：

| Task | 文件 | __mod_name__ |
|------|------|--------------|
| 22 | `userinfo.py` | `"用户信息"` |
| 23 | `users.py` | `"用户"` |
| 24 | `translator.py` | `"翻译"` |
| 25 | `weather.py` | `"天气"` |
| 26 | `wiki.py` | `"维基百科"` |
| 27 | `currency_converter.py` | `"汇率换算"` |
| 28 | `webss.py` | `"网页截图"` |
| 29 | `ud.py` | `"词典"` |
| 30 | `whois.py` | `"WHOIS 查询"` |
| 31 | `speed_test.py` | `"网速测试"` |

以及以下模块（Task 32-41）：

| Task | 文件 | __mod_name__ |
|------|------|--------------|
| 32 | `carbon.py` | `"代码美化"` |
| 33 | `telegraph.py` | `"Telegraph"` |
| 34 | `urlshortner.py` | `"短链接"` |
| 35 | `encode_decode.py` | `"编解码"` |
| 36 | `encrypt.py` | `"加密"` |
| 37 | `country.py` | `"国家信息"` |
| 38 | `rss.py`（如有） | `"RSS 订阅"` |
| 39 | `alive.py` | `"在线状态"` |
| 40 | `backups.py` | `"备份"` |
| 41 | `tagall.py` | `"全体标记"` |

---

## 第四批：AI + 娱乐 + 其余模块

### Task 42-∞：汉化第四批模块

对所有剩余模块，重复"读 → 翻译 → 写 → 提交"流程：

| 文件 | __mod_name__ |
|------|--------------|
| `chatgpt.py` | `"ChatGPT"` |
| `chatbot.py` | `"聊天机器人"` |
| `aiimage.py` | `"AI 图像"` |
| `anime.py` | `"动漫"` |
| `animez.py` | `"动漫搜索"` |
| `fun.py` | `"娱乐"` |
| `couples.py` | `"CP 配对"` |
| `truth_dare.py` | `"真心话大冒险"` |
| `dicegame.py` | `"骰子游戏"` |
| `wallpaper.py` | `"壁纸"` |
| `animation.py` | `"动图"` |
| `snipe.py` | `"狙击"` |
| `karma.py` | `"声望"` |
| `english.py` | `"英语"` |
| `figlet.py` | `"艺术字"` |
| `writetool.py` | `"写字工具"` |
| `zip.py` | `"压缩文件"` |
| `zombies.py` | `"僵尸账号"` |
| `unbanall.py` | `"解封全体"` |
| `nsfw.py` | `"NSFW 检测"` |
| `night_mode.py` | `"夜间模式"` |
| `remote_cmds.py` | `"远程命令"` |
| `disasters.py` | `"超级管理"` |
| `dev.py` | `"开发者"` |
| `eval.py` | `"执行代码"` |
| `debug.py` | `"调试"` |
| `bug.py` | `"反馈问题"` |
| 其余所有模块 | 按实际功能命名 |

---

## 最终任务

### Task 最终：验证与汇总提交

- [ ] **Step 1: 检查是否有遗漏的英文字符串**

```bash
cd MukeshRobot/modules
grep -r "reply_text\|send_message\|edit_text" --include="*.py" -l
```

对每个文件抽查 2-3 条 `reply_text` 调用，确认已为中文。

- [ ] **Step 2: 检查所有 __mod_name__ 已汉化**

```bash
grep -r "__mod_name__" MukeshRobot/modules/ --include="*.py"
```

确认所有值均为中文。

- [ ] **Step 3: 最终汇总提交**

```bash
git log --oneline | grep "i18n:" | wc -l
```

确认提交数量与模块数量匹配。

```bash
git push origin main
```
