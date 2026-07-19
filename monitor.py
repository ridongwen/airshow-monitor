import requests
import os
import sys
import datetime

URL = "https://www.airshow.com.cn/Category_1278/Index.aspx"
SOLD_OUT = "购票信息尚未公布"
KEYWORDS = ["购票", "立即购买", "门票", "¥", "价格", "元", "在线购票", "预订", "售票"]

# 用于标记是否已发送过开售通知
NOTIFIED_OPEN = False
# 记录今天是否已发送过日报
TODAY_REPORTED = None

def send_alert(title, msg):
    sendkey = os.environ.get('SERVERCHAN_KEY')
    if not sendkey:
        print("⚠️ 未配置 SERVERCHAN_KEY，跳过通知")
        return False

    try:
        r = requests.post(
            f"https://sctapi.ftqq.com/{sendkey}.send",
            data={"title": title, "desp": msg},
            timeout=10
        )
        result = r.json()
        if result.get('code') == 0:
            print(f"✅ 通知发送成功: {title}")
            return True
        else:
            print(f"❌ 通知发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 通知发送异常: {e}")
        return False

def check():
    global NOTIFIED_OPEN, TODAY_REPORTED

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    # 强制使用北京时间
    import pytz
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now(beijing_tz)
    beijing_time = now.strftime("%Y-%m-%d %H:%M:%S")
    today_str = now.strftime("%Y-%m-%d")

    try:
        r = requests.get(URL, headers=headers, timeout=30)
        r.encoding = 'utf-8'
        text = r.text

        print(f"[{beijing_time}] 页面长度: {len(text)} 字符")

        has_sold_out = SOLD_OUT in text
        found_keywords = [k for k in KEYWORDS if k in text]

        print(f"  包含'尚未公布': {has_sold_out}")
        print(f"  检测到关键词: {found_keywords}")

        # ========== 1. 开售检测（最高优先级）==========
        is_open = (not has_sold_out) or (len(found_keywords) > 0)

        if is_open and not NOTIFIED_OPEN:
            msg = f"""🎉 **珠海航展门票可能已开放！**

⏰ 检测时间: {beijing_time}

📊 检测结果:
• "尚未公布"文本: {'✅ 仍存在' if has_sold_out else '❌ 已消失！'}
• 购票关键词: {', '.join(found_keywords) if found_keywords else '无'}

🔗 立即查看: {URL}

⚠️ 请尽快前往官网购票，热门日期可能很快售罄！"""

            send_alert("🎫 航展门票监控提醒", msg)
            NOTIFIED_OPEN = True
            print("🎉 检测到售票开放！已发送通知")
            return True

        # ========== 2. 每日日报（北京时间早8点，每天只发一次）==========
        if now.hour == 8 and TODAY_REPORTED != today_str:
            status_msg = f"""📋 **航展监控日报** ({now.strftime('%m月%d日')})

⏰ 检测时间: {beijing_time}

📊 页面状态:
• 页面大小: {len(text)} 字符
• 访问状态: ✅ 正常
• "尚未公布": {'✅ 仍在' if has_sold_out else '❌ 已消失'}
• 购票关键词: {', '.join(found_keywords) if found_keywords else '无'}

📌 当前状态: {'⏳ 等待开售中' if has_sold_out else '⚠️ 页面有变化，请关注'}

🤖 脚本运行正常，继续监控中..."""

            send_alert("📋 航展监控日报", status_msg)
            TODAY_REPORTED = today_str  # 标记今天已发送
            print("📋 已发送每日日报")

        if not is_open:
            print("✅ 暂未开售，继续监控...")

        return is_open

    except Exception as e:
        error_msg = f"""⚠️ **航展监控脚本出错！**

⏰ 出错时间: {beijing_time}

❌ 错误信息:
```
{str(e)}
```

🔗 监控页面: {URL}

⚠️ 请检查：
1. 目标网站是否可访问
2. 网络连接是否正常
3. 脚本是否需要更新"""

        send_alert("🚨 航展监控异常告警", error_msg)
        print(f"❌ 脚本出错，已发送告警: {e}")
        return False

if __name__ == "__main__":
    check()
