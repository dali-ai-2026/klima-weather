import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import math

# ========== 页面配置 ==========
st.set_page_config(
    page_title="气候运势",
    page_icon="🌍",
    layout="wide"
)

# ========== 高德API配置 ==========
AMAP_KEY = "8432df6237d4926456b946918b1607f6"

# ========== 天气函数（支持全国任意城市）==========
def get_weather(city_name):
    """调用高德API获取实时天气（支持全国任意城市）"""
    if not city_name or city_name.strip() == "":
        return None, "请输入城市名称"
    
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": AMAP_KEY,
        "city": city_name,
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
                "wind": w["winddirection"],
                "humidity": w.get("humidity", "未知")
            }, None
        else:
            return None, "未找到该城市，请输入正确的城市名称"
    except Exception as e:
        return None, f"网络错误: {str(e)}"

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

# ========== 页面标题 ==========
st.title("🌍 气候运势")
st.caption("每日日汉双语 · 气候日语学习")

# ========== 侧边栏 ==========
with st.sidebar:
    # ========== 1. 天气区域 ==========
    st.header("☁️ 天気")
    
    city_name = st.text_input("都市名", value="南京", placeholder="例：北京、上海、南京、民权")
    st.caption("💡 全国すべての都市に対応")
    
    weather, error = get_weather(city_name)
    
    if weather:
        temp = int(weather['temperature'])
        humidity = int(weather['humidity'])
        
        # 体感温度计算
        e = (humidity / 100) * 6.105 * math.exp((17.27 * temp) / (237.7 + temp))
        feels_like = round(temp + 0.33 * e - 0.70 * 2.0 - 4.00, 1)
        
        st.metric("🌡️ 気温", f"{temp}°C")
        st.write(f"**💧 湿度**：{humidity}%")
        st.write(f"**🌡️ 体感温度**：{feels_like}°C")
        
        # 热中症リスク指数
        def get_heat_risk(feels_like):
            if feels_like >= 35:
                return "危険", "🔴", "厳重警戒レベル。屋外での活動は避けてください。"
            elif feels_like >= 32:
                return "高", "🟠", "警戒レベル。こまめな水分補給と休憩が必要です。"
            elif feels_like >= 28:
                return "中", "🟡", "注意レベル。運動時は特に気をつけましょう。"
            elif feels_like >= 25:
                return "やや高", "🟢", "軽度の注意が必要です。"
            else:
                return "低", "🔵", "通常レベル。特に問題はありません。"
        
        risk_level, risk_icon, risk_advice = get_heat_risk(feels_like)
        st.write(f"**{risk_icon} 熱中症リスク**：{risk_level}")
        st.caption(risk_advice)
        
        # 行动感建议
        random.seed(int(datetime.now().strftime("%Y%m%d")))
        
        if feels_like >= 35:
            action_options = [
                "🍧 冷たいかき氷が食べたい気分ですね。おうちで作ってみませんか？",
                "🥤 スポーツドリンクで水分と塩分を一緒に補給しましょう。",
                "🏠 エアコンの効いた部屋で、ゆっくり映画を観るのもいいですね。",
                "🧊 保冷剤をタオルで包んで首に巻くと、涼しく過ごせますよ。"
            ]
        elif feels_like >= 32:
            action_options = [
                "🍦 アイスクリームで一息。今日の小さなご褒美にいかがですか？",
                "💦 濡れタオルで顔や腕を拭くと、すっきりします。",
                "🌿 うちわや扇風機で風を送るだけでも、体感温度が下がります。",
                "🥤 こまめな水分補給を忘れずに。麦茶や経口補水液がおすすめです。"
            ]
        elif feels_like >= 28:
            action_options = [
                "🍉 冷たい果物でビタミン補給。スイカやメロンはいかがですか？",
                "🚶 朝晩の涼しい時間帯に軽い散歩を。",
                "💧 加湿器や濡れタオルで湿度を上げると、体感温度が下がります。",
                "📖 日陰のベンチで読書も気持ちいい季節です。"
            ]
        elif feels_like >= 25:
            action_options = [
                "🌸 窓を開けて風を通すだけで、気持ちいいですよ。",
                "🚲 自転車でちょっとしたお出かけはいかがですか？",
                "🧺 洗濯物がよく乾く絶好の陽気です。",
                "🍙 お弁当を持って、公園でピクニックも楽しいですよ。"
            ]
        elif feels_like >= 18:
            action_options = [
                "🚶 散歩にぴったりの気温です。一歩出かけてみませんか？",
                "📸 写真撮影にぴったりの光と影。散歩がてらどうぞ。",
                "🍵 室温の水やお茶で水分補給を。",
                "📖 読書やカフェでのんびり過ごすのもいいですね。"
            ]
        elif feels_like >= 10:
            action_options = [
                "🍁 紅葉や落ち葉を楽しむ散歩はいかがですか？",
                "☕ 温かい飲み物で一息。ほっとする時間を。",
                "🧥 薄手のコートやカーディガンがあると便利です。",
                "🎵 音楽を聴きながらのんびり過ごす休日もいいですね。"
            ]
        elif feels_like >= 5:
            action_options = [
                "🧣 マフラーや手袋で防寒対策をしっかりと。",
                "☕ 温かいココアや紅茶で体を温めましょう。",
                "📚 おうちで読書や映画鑑賞。ゆったり過ごすのもいいですね。",
                "🍲 鍋料理や温かいスープで体の中からポカポカ。"
            ]
        else:
            action_options = [
                "🛁 温かいお風呂で体を芯から温めましょう。",
                "🧤 手袋や耳あてで冷え対策を。",
                "🔥 ストーブやこたつで暖を取るのも冬の楽しみです。",
                "📺 おうちでゆっくり過ごす週末も悪くないですね。"
            ]
        
        action_advice = random.choice(action_options)
        st.write(f"💡 {action_advice}")
        
        # 数据来源
        st.caption(f"📍 {weather['city']}")
        st.caption("📌 データ元：高德地图")
        
    else:
        st.error(error or "天気情報を取得できませんでした")
    
    st.divider()
    
    # ========== 2. 运势区域 ==========
    st.header("📅 今日の運勢")
    
    # 农历和节气
    solar_term = None
    try:
        from lunar_python import Solar
        today = datetime.now()
        solar = Solar.fromYmd(today.year, today.month, today.day)
        lunar = solar.getLunar()
        lunar_date = f"{lunar.getMonth()}月{lunar.getDay()}日"
        solar_term = lunar.getSolarTerm()
        st.caption(f"📖 旧暦：{lunar_date}")
        if solar_term:
            st.caption(f"🍃 節気：{solar_term}")
    except:
        pass
    
    # 运势等级
    random.seed(int(datetime.now().strftime("%Y%m%d")))
    fortune_levels = ["大吉", "中吉", "小吉", "吉"]
    fortune = random.choice(fortune_levels)
    st.metric("運勢", fortune)
    
    # 幸运色
    color_pool = ["🔴 赤", "🟠 オレンジ", "🟡 黄", "🟢 緑", "🔵 青", "🟣 紫", "💗 ピンク"]
    num_colors = random.choice([1, 2])
    lucky_colors = " / ".join(random.sample(color_pool, num_colors))
    st.write(f"**ラッキーカラー**：{lucky_colors}")
    
    # 今日「宜」
    weather_condition = None
    if weather:
        desc = weather['weather']
        if '晴' in desc:
            weather_condition = '晴'
        elif '雨' in desc:
            weather_condition = '雨'
        elif '高温' in desc or '热' in desc:
            weather_condition = '高温'
        elif '雪' in desc:
            weather_condition = '雪'
        elif '风' in desc:
            weather_condition = '风'
    
    def get_daily_yi(weather_cond, solar_term_val, fortune_level):
        weather_yi = {
            "晴": "外で日光浴をする",
            "雨": "雨音を聞きながら読書",
            "高温": "水分補給をする",
            "雪": "雪見酒を楽しむ",
            "风": "凧揚げをする",
        }
        
        term_yi = {
            "芒种": "希望を蒔く",
            "夏至": "早寝早起き",
            "小满": "足ることを知る",
            "立春": "新しい始まり",
            "春分": "心身のバランス",
            "秋分": "感謝の気持ち",
            "冬至": "自分を温める",
        }
        
        fortune_yi = {
            "大吉": "新しいことに挑戦",
            "中吉": "人と交流する",
            "小吉": "小さな目標を達成",
            "吉": "良い気分を保つ",
        }
        
        creative_pool = [
            "深呼吸をする", "水を一杯飲む", "机の上を整理する", "笑顔を忘れない", "散歩をする",
            "小さな出来事を記録する", "不要な通知をオフにする", "ストレッチをする", "知識をシェアする", "早く寝る",
            "一ページ読む", "新しい言葉を学ぶ", "マインドフルネス", "友達に挨拶する", "好きな歌を聴く",
            "窓を開けて換気する", "ちゃんと朝ごはんを食べる", "空を見上げる", "自分を褒める", "背筋を伸ばす",
            "温かいお茶を飲む", "今日の小さな目標を書く", "植物に水をやる", "写真を見返す", "雨の音を聴く",
        ]
        
        yi_list = []
        
        if weather_cond:
            for key, value in weather_yi.items():
                if key in weather_cond:
                    yi_list.append(value)
                    break
        
        if solar_term_val and solar_term_val in term_yi:
            yi_list.append(term_yi[solar_term_val])
        
        if fortune_level and fortune_level in fortune_yi:
            yi_list.append(fortune_yi[fortune_level])
        
        final_count = random.randint(1, 3)
        
        if len(yi_list) >= final_count:
            result = random.sample(yi_list, final_count)
        else:
            result = yi_list.copy()
            needed = final_count - len(result)
            if needed > 0:
                result.extend(random.sample(creative_pool, needed))
        
        result = list(dict.fromkeys(result))
        return result
    
    yi_list = get_daily_yi(weather_condition, solar_term, fortune)
    
    # 显示「宜」
    st.markdown("**✨ 宜：**")
    for yi_item in yi_list:
        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{yi_item}")
    
    st.divider()

# ========== 新闻模块 ==========
# ========== 新闻模块 ==========
st.subheader("📰 今日の気象ニュース")

# 通用优先级函数（与 fetch_news.py 保持一致）
def get_priority(title):
    """计算新闻优先级分数（越高越靠前）"""
    if any(word in title for word in ["榴莲", "荔枝", "西瓜", "杨梅", "水果", "芒果"]):
        return 100
    if any(word in title for word in ["小满", "芒种", "夏至", "端午", "节气", "儿童节"]):
        return 80
    if any(word in title for word in ["为什么", "揭秘", "原来", "竟然", "科普"]):
        return 60
    if any(word in title for word in ["高温", "降温", "出行", "旅游", "穿衣"]):
        return 40
    if any(word in title for word in ["预警", "暴雨", "山洪", "地质灾害", "渍涝", "台风"]):
        return 10
    return 0

# 加载新闻（从 news_data.json 读取）
def load_news():
    """从 news_data.json 读取国内和国际新闻"""
    try:
        with open("news_data.json", "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            china_news = data.get("china_news", [])
            world_news = data.get("world_news", [])
            return china_news, world_news
    except Exception as e:
        print(f"加载新闻失败: {e}")
        return [], []

# 加载数据
china_news, world_news = load_news()

# 两栏布局
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🇨🇳 国内气象")
    if china_news:
        first = china_news[0]
        st.markdown(f"**[{first['title'][:60]}]({first['url']})**")
        st.caption(f"来源：{first.get('source', '中国天气网')} · {first.get('date', '')}")
        if len(china_news) > 1:
            with st.expander(f"📖 もっと見る（{len(china_news)-1}件）"):
                for news in china_news[1:]:
                    if news.get('title', '').strip():
                        st.markdown(f"• [{news['title'][:50]}]({news['url']})")
    else:
        st.info("暂无国内气象新闻")

with col2:
    st.markdown("#### 🌍 国际气候")
    if world_news:
        first = world_news[0]
        st.markdown(f"**[{first['title'][:60]}]({first['url']})**")
        st.caption(f"来源：{first.get('source', '新华网英文')} · {first.get('date', '')}")
        if len(world_news) > 1:
            with st.expander(f"📖 もっと見る（{len(world_news)-1}件）"):
                for news in world_news[1:]:
                    if news.get('title', '').strip():
                        st.markdown(f"• [{news['title'][:50]}]({news['url']})")
    else:
        st.info("暂无国际气候新闻")

st.divider()
# ========== 硬核词模块 ==========
# ========== 硬核词模块（简化版 - 无收藏功能）==========
st.subheader("📖 今日のキーワード")

import csv
import random
import json
import os
import uuid
from datetime import datetime

# ========== 当前文件所在目录 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== 用户ID持久化 ==========
USER_ID_FILE = os.path.join(BASE_DIR, "user_id.txt")

if os.path.exists(USER_ID_FILE):
    with open(USER_ID_FILE, "r") as f:
        user_id = f.read().strip()
else:
    user_id = str(uuid.uuid4())[:8]
    with open(USER_ID_FILE, "w") as f:
        f.write(user_id)

if "user_id" not in st.session_state:
    st.session_state.user_id = user_id

# ========== 学习进度持久化 ==========
PROGRESS_FILE = os.path.join(BASE_DIR, "progress_all.json")

def load_all_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_all_progress(all_progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_progress, f, ensure_ascii=False, indent=2)

def get_user_progress():
    all_prog = load_all_progress()
    return all_prog.get(st.session_state.user_id, {})

def set_user_progress(progress):
    all_prog = load_all_progress()
    all_prog[st.session_state.user_id] = progress
    save_all_progress(all_prog)

# ========== 加载CSV ==========
def load_keywords_from_csv():
    keywords = []
    try:
        csv_path = os.path.join(BASE_DIR, "keywords.csv")
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                keywords.append({
                    "ja": row.get("ja", ""),
                    "ja_kana": row.get("ja_kana", ""),
                    "zh": row.get("zh", ""),
                    "desc_ja": row.get("desc_ja", ""),
                    "desc_zh": row.get("desc_zh", ""),
                    "example_ja": row.get("example_ja", ""),
                    "example_zh": row.get("example_zh", ""),
                    "detail_ja": row.get("detail_ja", ""),
                    "detail_zh": row.get("detail_zh", ""),
                    "source": row.get("source", ""),
                    "tags": row.get("tags", ""),
                    "type": row.get("type", "")
                })
    except Exception as e:
        print(f"加载失败: {e}")
        return []
    return keywords

# ========== 初始化 ==========
if "keyword_pool" not in st.session_state:
    st.session_state.keyword_pool = load_keywords_from_csv()
    st.session_state.achievements = {"bronze": False, "silver": False, "gold": False, "master": False}
    st.session_state.session_viewed = {}

if "viewed_history" not in st.session_state:
    st.session_state.viewed_history = get_user_progress()

# ========== 模式选择 ==========
mode_options = {"all": "全部", "term": "📘 术语", "proverb": "🍃 谚语"}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "all"

col_mode, col_next = st.columns([4, 1])

with col_mode:
    current_mode = st.radio(
        "显示模式",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x],
        horizontal=True,
        label_visibility="collapsed"
    )

with col_next:
    if st.button("⏩ 下一个", use_container_width=True):
        st.rerun()

def filter_by_mode(pool, mode):
    if mode == "term":
        return [kw for kw in pool if kw.get('type') == 'term']
    elif mode == "proverb":
        return [kw for kw in pool if kw.get('type') == 'proverb']
    return pool

filtered_pool = filter_by_mode(st.session_state.keyword_pool, current_mode)

# ========== 随机抽取关键词 ==========
def get_random_keyword(mode, pool):
    if not pool:
        return None
    
    viewed_ja = st.session_state.viewed_history.get(mode, [])
    available = [kw for kw in pool if kw['ja'] not in viewed_ja]
    
    if not available:
        st.session_state.viewed_history[mode] = []
        set_user_progress(st.session_state.viewed_history)
        available = pool
    
    selected = random.choice(available)
    return selected

today_keyword = get_random_keyword(current_mode, filtered_pool)

if not today_keyword:
    st.warning("暂无内容")
    st.stop()

# ========== 记录查看和永久进度 ==========
view_key = f"viewed_{current_mode}_{today_keyword['ja']}"
if not st.session_state.get(view_key):
    if current_mode not in st.session_state.viewed_history:
        st.session_state.viewed_history[current_mode] = []
    
    viewed_ja = st.session_state.viewed_history.get(current_mode, [])
    
    if today_keyword['ja'] not in viewed_ja:
        st.session_state.viewed_history[current_mode].append(today_keyword['ja'])
        set_user_progress(st.session_state.viewed_history)
    
    st.session_state[view_key] = True
    
    # 里程碑检查
    seen = len(st.session_state.viewed_history.get(current_mode, []))
    total = len(filtered_pool)
    if total > 0 and seen >= 10 and not st.session_state.achievements["bronze"]:
        st.session_state.achievements["bronze"] = True
        st.balloons()
        st.success("🎉 获得【气象初心者】称号！")
    if total > 0 and seen >= 30 and not st.session_state.achievements["silver"]:
        st.session_state.achievements["silver"] = True
        st.balloons()
        st.success("🎉 获得【气象通】称号！")
    if total > 0 and seen >= 50 and not st.session_state.achievements["gold"]:
        st.session_state.achievements["gold"] = True
        st.balloons()
        st.success("🎉 获得【气象大师】称号！")
    if total > 0 and seen >= 100 and not st.session_state.achievements["master"]:
        st.session_state.achievements["master"] = True
        st.balloons()
        st.success("🎉 获得【传说气象博士】称号！")

# ========== 显示当前词汇 ==========
st.markdown("---")

if today_keyword.get('type') == 'term':
    st.markdown("**📘 专业术语**")
    st.caption("正式定义与出处")
else:
    st.markdown("**🍃 气象谚语**")
    st.caption("例句与使用场景")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**🇯🇵 日语**")
    display = today_keyword['ja']
    if today_keyword.get('ja_kana'):
        display = f"{display}（{today_keyword['ja_kana']}）"
    st.info(f"**{display}**\n\n{today_keyword['desc_ja']}")
with col2:
    st.markdown("**🇨🇳 中文**")
    st.success(f"**{today_keyword['zh']}**\n\n{today_keyword['desc_zh']}")

# ========== 了解更多 ==========
with st.expander("📖 了解更多"):
    if today_keyword.get('type') == 'term':
        st.markdown("**📌 内容**")
        if today_keyword.get('detail_ja') and today_keyword.get('detail_zh'):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**🇯🇵**\n{today_keyword['detail_ja']}")
            with col2:
                st.markdown(f"**🇨🇳**\n{today_keyword['detail_zh']}")
        if today_keyword.get('source'):
            st.caption(f"📚 出处：{today_keyword['source']}")
    else:
        if today_keyword.get('example_ja') and today_keyword.get('example_zh'):
            st.markdown("**📝 例句**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**🇯🇵**\n{today_keyword['example_ja']}")
            with col2:
                st.markdown(f"**🇨🇳**\n{today_keyword['example_zh']}")
        st.caption("📝 使用场景：天气话题、季节问候、自然观察作文")

# ========== 进度 ==========
total = len(filtered_pool)
seen = len(st.session_state.viewed_history.get(current_mode, []))
st.progress(seen / total if total > 0 else 0)
remaining = total - seen
if remaining > 0:
    st.caption(f"📊 进度：{seen}/{total} 语（还剩{remaining}语）")
    if seen < 10:
        st.caption(f"✨ 再学{10 - seen}语获得【气象初心者】")
    elif seen < 30:
        st.caption(f"✨ 再学{30 - seen}语获得【气象通】")
    elif seen < 50:
        st.caption(f"✨ 再学{50 - seen}语获得【气象大师】")
    elif seen < 100:
        st.caption(f"✨ 再学{100 - seen}语获得【传说气象博士】")
else:
    st.caption(f"📊 进度：{seen}/{total} 语 🎉 完成！")

st.divider()
# ========== 打卡和分享 ==========
# ========== 打卡和分享 ==========
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
        with st.spinner("卡片生成中..."):
            try:
                from PIL import Image, ImageDraw, ImageFont
                import io
                import qrcode
                import random
                
                # 获取今日关键词
                if "today_keyword" in locals() or "today_keyword" in dir():
                    keyword_ja = today_keyword.get('ja', '')
                    keyword_zh = today_keyword.get('zh', '')
                else:
                    keyword_ja = "今日のキーワード"
                    keyword_zh = "今日关键词"
                
                # 获取运势和幸运色
                fortune_level = fortune if 'fortune' in dir() else "中吉"
                lucky_color = lucky_colors if 'lucky_colors' in dir() else "🔴 红色"
                
                # 创建图片
                img = Image.new('RGB', (800, 1000), color='white')
                draw = ImageDraw.Draw(img)
                
                # 尝试加载字体
                try:
                    font_title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
                    font_body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
                    font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
                except:
                    font_title = ImageFont.load_default()
                    font_body = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                
                # 标题
                draw.text((50, 40), "🌍 气候运势", fill='black', font=font_title)
                draw.text((50, 100), f"📅 {datetime.now().strftime('%Y年%m月%d日')}", fill='gray', font=font_small)
                
                # 分割线
                draw.line((50, 140, 750, 140), fill='lightgray', width=2)
                
                # 运势和幸运色
                draw.text((50, 180), f"🎴 今日运势：{fortune_level}", fill='#e67e22', font=font_body)
                draw.text((50, 230), f"🎨 幸运色：{lucky_color}", fill='#e67e22', font=font_body)
                
                # 分割线
                draw.line((50, 280, 750, 280), fill='lightgray', width=1)
                
                # 术语（只显示术语名称，不显示解释）
                draw.text((50, 320), "📖 今日のキーワード", fill='black', font=font_body)
                draw.text((50, 380), f"🇯🇵 {keyword_ja[:40]}", fill='#2c3e50', font=font_body)
                draw.text((50, 430), f"🇨🇳 {keyword_zh[:40]}", fill='#2c3e50', font=font_body)
                
                # 分割线
                draw.line((50, 490, 750, 490), fill='lightgray', width=1)
                
                # 打卡信息
                checkin_data = checkin()
                draw.text((50, 530), f"🔥 连续学习 {checkin_data['continuous']} 天", fill='#e67e22', font=font_body)
                draw.text((50, 580), f"📊 累计学习 {checkin_data['total']} 天", fill='#e67e22', font=font_body)
                
                # 底部
                draw.line((50, 660, 750, 660), fill='lightgray', width=1)
                draw.text((50, 700), "气候运势 · 每日气象日语学习", fill='gray', font=font_small)
                draw.text((50, 740), "扫码体验更多", fill='gray', font=font_small)
                
                # 二维码
                try:
                    qr = qrcode.QRCode(box_size=8, border=1)
                    qr.add_data("https://klima-weather.streamlit.app")  # 替换为你的公网链接
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_img = qr_img.resize((120, 120))
                    img.paste(qr_img, (600, 680))
                except:
                    draw.text((600, 700), "[二维码]", fill='gray', font=font_small)
                
                # 保存图片
                img_path = os.path.join(BASE_DIR, "share_card.png")
                img.save(img_path)
                
                st.image(img_path, caption="今日学習カード", use_column_width=True)
                st.success("✅ 卡片已生成！长按图片保存，即可分享到朋友圈")
                
            except Exception as e:
                st.error(f"生成失败: {e}")
                st.info("请确保已安装 Pillow 和 qrcode 库")

st.divider()
st.caption("💡 每日更新 · 日汉双语 · 气候日语学习")
