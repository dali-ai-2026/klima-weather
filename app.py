import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# ========== 页面配置 ==========
st.set_page_config(
    page_title="气候运势",
    page_icon="🌍",
    layout="wide"
)

# ========== 高德API配置 ==========
AMAP_KEY = "8432df6237d4926456b946918b1607f6"

# ========== 城市编码对照表 ==========
CITY_CODES = {
    "南京": "320100",
    "北京": "110000",
    "上海": "310000",
    "广州": "440100",
    "深圳": "440300",
    "杭州": "330100",
    "苏州": "320500",
    "无锡": "320200",
    "常州": "320400",
    "镇江": "321100"
}

# ========== 天气函数 ==========
def get_weather(city_name):
    city_code = CITY_CODES.get(city_name)
    if not city_code:
        return None, "暂不支持该城市"
    
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": AMAP_KEY,
        "city": city_code,
        "extensions": "base"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data["status"] == "1" and data["count"] != "0":
            w = data["lives"][0]
            return {
                "city": w["city"],
                "weather": w["weather"],
                "temperature": w["temperature"],
                "wind": w["winddirection"]
            }, None
        else:
            return None, "获取天气失败"
    except Exception as e:
        return None, f"网络错误: {str(e)}"

# ========== 运势函数 ==========
def get_fortune():
    random.seed(int(datetime.now().strftime("%Y%m%d")))
    levels = ["大吉", "中吉", "小吉", "吉", "末吉"]
    colors = ["🔴 红色", "🟢 绿色", "🔵 蓝色", "🟡 黄色", "🟣 紫色"]
    return {
        "level": random.choice(levels),
        "color": random.choice(colors)
    }

# ========== 鼓励语池 ==========
ENCOURAGE_POOL = {
    "I人": [
        {"ja": "一人の時間は充電の時間。今日は「CBAM」を調べてみよう。", "zh": "独处不是孤独，是充电。今天查一下CBAM是什么。"},
        {"ja": "静かな場所で、今日の気候ニュースを読んでみよう。", "zh": "在安静的地方，读一读今天的气候新闻。"},
        {"ja": "自分のペースでいい。今日も一歩前に進んだ。", "zh": "按自己的节奏就好。今天又前进了一步。"}
    ],
    "E人": [
        {"ja": "今日覚えた言葉を、誰かに話してみよう。", "zh": "把今天学到的词，讲给一个人听。"},
        {"ja": "友達と「カーボンボーダー」について話してみよう。", "zh": "和朋友聊聊“碳边境税”。"},
        {"ja": "今日のニュースをシェアして、みんなの意見を聞こう。", "zh": "分享今天的新闻，听听大家的看法。"}
    ],
    "F人": [
        {"ja": "今日のキーワードは、あなたにとってどんな意味がある？", "zh": "今天的关键词，对你来说有什么意义？"},
        {"ja": "優しさは力になる。今日も誰かに優しく。", "zh": "温柔就是力量。今天也对一个人温柔。"},
        {"ja": "気候変動は遠い話じゃない。あなたの一歩が未来を変える。", "zh": "气候变化不是遥远的事。你的一步会改变未来。"}
    ]
}

def get_encourage(personality):
    pool = ENCOURAGE_POOL.get(personality, ENCOURAGE_POOL["I人"])
    if "encourage_history" not in st.session_state:
        st.session_state.encourage_history = {}
    if personality not in st.session_state.encourage_history:
        st.session_state.encourage_history[personality] = []
    
    history = st.session_state.encourage_history[personality]
    available = [e for e in pool if e not in history]
    
    if not available:
        st.session_state.encourage_history[personality] = []
        available = pool.copy()
    
    selected = random.choice(available)
    st.session_state.encourage_history[personality].append(selected)
    return selected

# ========== 打卡功能 ==========
def checkin():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open("checkin.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"last_date": "", "continuous": 0, "total": 0}
    
    last_date = data.get("last_date", "")
    if last_date != today:
        if last_date == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
            data["continuous"] += 1
        elif last_date == "":
            data["continuous"] = 1
        else:
            data["continuous"] = 1
        data["total"] = data.get("total", 0) + 1
        data["last_date"] = today
        with open("checkin.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return data

# ========== 加载今日新闻 ==========
def load_today_news():
    try:
        with open("daily_news.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except:
        return {
            "one_sentence": "今日暂无重要气候新闻",
            "summary": "",
            "url": "",
            "source": "生态环境部",
            "date": datetime.now().strftime("%Y-%m-%d")
        }

# ========== 初始化 ==========
if "personality" not in st.session_state:
    st.session_state.personality = "I人"

# ========== 页面标题 ==========
st.title("🌍 气候运势")
st.caption("每日日汉双语 · 气候政治科普")

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("☁️ 天気")
    cities = list(CITY_CODES.keys())
    selected_city = st.selectbox("城市 / 都市", cities, index=0)
    
    weather, error = get_weather(selected_city)
    if weather:
        st.metric("現在の気温", f"{weather['temperature']}°C")
        st.write(f"**天気**：{weather['weather']}")
    else:
        st.error(error or "获取天气失败")
    
    st.divider()
    
    st.header("📅 今日の運勢")
    fortune = get_fortune()
    st.metric("運勢", fortune["level"])
    st.write(f"**ラッキーカラー**：{fortune['color']}")
    
    st.divider()
    
    st.markdown("### 🧘 あなたのタイプ")
    col_i, col_e, col_f = st.columns(3)
    with col_i:
        if st.button("I人", use_container_width=True):
            st.session_state.personality = "I人"
    with col_e:
        if st.button("E人", use_container_width=True):
            st.session_state.personality = "E人"
    with col_f:
        if st.button("F人", use_container_width=True):
            st.session_state.personality = "F人"
    st.caption(f"現在：{st.session_state.personality}")
    
    st.divider()
    
    st.markdown("### ✨ 今日の一言")
    encourage = get_encourage(st.session_state.personality)
    st.info(f"🇯🇵 {encourage['ja']}")
    st.caption(f"🇨🇳 {encourage['zh']}")

# ========== 主页面 ==========
# 新闻模块（带了解更多）
st.subheader("📰 今日の気候ニュース")

news_data = load_today_news()
news_title = news_data.get("one_sentence", "今日暂无重要气候新闻")
news_summary = news_data.get("summary", "")
news_url = news_data.get("url", "")
news_source = news_data.get("source", "生态环境部")
news_date = news_data.get("date", "")

st.info(f"🌍 {news_title}")
st.caption(f"来源：{news_source} · {news_date}")

# 了解更多
with st.expander("📖 もっと見る / 了解更多"):
    if news_summary:
        st.markdown("**📝 詳細 / 详情**")
        st.write(news_summary)
    else:
        st.info("详细内容待补充。正式版本将接入AI大模型生成新闻摘要。")
    
    if news_url and news_url != "":
        st.markdown(f"**🔗 原文 / 原文链接**：[{news_url}]({news_url})")

st.divider()

# 硬核词模块
st.subheader("📖 今日のキーワード")

KEYWORDS = [
    {
        "ja": "CBAM（炭素国境調整メカニズム）",
        "zh": "CBAM（碳边境调节机制）",
        "desc_ja": "EUが2026年から本格導入する制度。輸入品に製造時のCO2排出量に応じた炭素コストを課す。",
        "desc_zh": "欧盟将于2026年全面实施的制度。对进口产品根据其生产过程中的CO2排放量征收碳成本。",
        "detail_ja": "**詳細**：EUは2005年から排出量取引制度を運用。CBAMは無償割当の代替として導入される。",
        "detail_zh": "**详解**：欧盟自2005年起运行碳交易体系。CBAM将替代免费配额。"
    },
    {
        "ja": "カーボンリーケージ",
        "zh": "碳泄漏",
        "desc_ja": "排出規制の厳しい国から緩い国へ生産拠点が移転する現象。",
        "desc_zh": "生产从排放管制严格的国家向宽松国家转移的现象。",
        "detail_ja": "**詳細**：規制の厳しい国では生産コストが上昇するため。",
        "detail_zh": "**详解**：管制严格的国家生产成本上升。"
    }
]

day_index = datetime.now().timetuple().tm_yday % len(KEYWORDS)
today_keyword = KEYWORDS[day_index]

col1, col2 = st.columns(2)
with col1:
    st.markdown("**🇯🇵 日本語**")
    st.info(f"**{today_keyword['ja']}**\n\n{today_keyword['desc_ja']}")
with col2:
    st.markdown("**🇨🇳 中文**")
    st.success(f"**{today_keyword['zh']}**\n\n{today_keyword['desc_zh']}")

with st.expander("📖 もっと見る / 了解更多"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🇯🇵 詳細解説**")
        st.info(today_keyword.get('detail_ja', '详细内容待补充'))
    with col2:
        st.markdown("**🇨🇳 详细解读**")
        st.success(today_keyword.get('detail_zh', '详细内容待补充'))

st.divider()

# 打卡和分享
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📅 学習記録")
    checkin_data = checkin()
    st.metric("🔥 連続", f"{checkin_data['continuous']} 日")
    st.caption(f"📊 累計 {checkin_data['total']} 日")
    if checkin_data.get("last_date") == datetime.now().strftime("%Y-%m-%d"):
        st.success("✅ 今日はもうチェックインしました / 今日已打卡")

with col_right:
    st.subheader("📤 シェア")
    st.caption("今日のカードを生成してシェアしよう")
    st.caption("生成学习卡片，分享给朋友")
    
    if st.button("✨ 生成今日卡片", use_container_width=True):
        st.info("卡片生成功能开发中，正式版本将支持分享朋友圈")

st.divider()
st.caption("💡 每日更新 · 日汉双语 · 气候变化下的国际政治科普")
