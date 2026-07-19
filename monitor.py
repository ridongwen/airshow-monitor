import requests
import os
import sys

URL = "https://www.airshow.com.cn/Category_1278/Index.aspx"
SOLD_OUT = "购票信息尚未公布"
KEYWORDS = ["购票", "立即购买", "门票", "¥", "价格", "元", "在线购票", "预订"]

def check():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        r = requests.get(URL, headers=headers, timeout=30)
        r.encoding = 'utf-8'
        text = r.text
        
        print(f"页面长度: {len(text)} 字符")
        
        # 检查是否仍然显示"尚未公布"
        has_sold_out = SOLD_OUT in text
        
        # 检查是否出现购票关键词
        found_keywords = [k for k in KEYWORDS if k in text]
        
        print(f"包含'尚未公布': {has_sold_out}")
        print(f"检测到关键词: {found_keywords}")
        
        # 如果"尚未公布"消失，或出现购票关键词，认为已开售
        if not has_sold_out or len(found_keywords) > 0:
            msg = f"🎉 珠海航展门票可能已开放！\n\n检测到变化：\n- '尚未公布'文本: {'已消失' if not has_sold_out else '仍存在'}\n- 购票关键词: {found_keywords if found_keywords else '无'}\n\n快去看：{URL}"
            send_alert("航展门票监控提醒 🎫", msg)
            return True
            
        print("✅ 暂未开售，继续监控...")
        return False
        
    except Exception as e:
        print(f"❌ 检查出错: {e}")
        send_alert("监控脚本出错 ⚠️", f"检查航展页面时出错：{e}")
        return False

def send_alert(title, msg):
    sendkey = os.environ.get('SERVERCHAN_KEY')
    if not sendkey:
        print("未配置 SERVERCHAN_KEY，跳过通知")
        return
    
    try:
        r = requests.post(
            f"https://sctapi.ftqq.com/{sendkey}.send",
            data={"title": title, "desp": msg},
            timeout=10
        )
        print(f"通知发送结果: {r.status_code}")
    except Exception as e:
        print(f"通知发送失败: {e}")

if __name__ == "__main__":
    if check():
        print("🎉 检测到售票开放！")
    else:
        print("⏳ 继续等待...")
