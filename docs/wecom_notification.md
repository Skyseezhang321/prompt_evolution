# 企业微信通知

本仓库的消息通知统一走 `scripts/wecom_notify.py`。后续新增任何脚本、实验任务、定时任务或 CI 流程时，都应调用这个入口发送企业微信机器人提醒，避免在多个位置直接拼 webhook 请求。

## 配置

复制 `.env.example` 为本地 `.env`，然后填入企业微信机器人 webhook：

```dotenv
WECOM_BOT_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
WECOM_NOTIFY_ENABLED=true
```

`.env` 已在 `.gitignore` 中忽略，不应提交真实 webhook。需要临时关闭通知时，把 `WECOM_NOTIFY_ENABLED` 设为 `false`、`0` 或 `off`。

## 命令行发送

```bash
python scripts/wecom_notify.py "### Prompt Evolution 通知通道测试"
```

也可以从文件读取消息内容：

```bash
python scripts/wecom_notify.py --file notification.md
```

检查 payload 但不真实发送：

```bash
python scripts/wecom_notify.py --dry-run "测试消息"
```

## Python 调用

```python
from scripts.wecom_notify import load_dotenv, send_wecom_notification

load_dotenv()

send_wecom_notification("### 实验完成\n- run_id: 20260608-001")
```

企业微信机器人异常、网络异常或 webhook 未配置时会抛出 `NotificationError`。调用方如果有自己的重试或降级策略，应捕获这个异常并记录失败原因。
