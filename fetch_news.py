import requests
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os

# ========== 国内新闻（中国天气网）==========
def fetch_china_news():
    """抓取中国天气网新闻"""
    url = "https://news.weather.com.cn/news2019_more.htm?callback=jsonpcallback&_=1780327869686"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://news.weather.com.cn/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        text = response.text
        
        match = re.search(r'jsonpcallback\((.*)\)', text, re.DOTALL)
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            
            today = datetime.now().strftime("%Y-%m-%d")
            news_list = []
            
            for item in data.get('sites', []):
                if item.get('c5') == today:
                    title = item.get('c1', '')
                    try:
                        title = title.encode('latin1').decode('unicode_escape')
                    except:
                        pass
                    
                    news_list.append({
                        "title": title,
                        "url": item.get('c2', ''),
                        "date": item.get('c5', ''),
                        "source": "中国天气网"
                    })
            return news_list
    except Exception as e:
        print(f"国内新闻抓取失败: {e}")
    return []

# ========== 国际新闻（新华网英文）==========
def fetch_world_news():
    """抓取新华网英文新闻（不预筛选，全部返回）"""
    url = "https://english.news.cn/list/latestnews.htm"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://english.news.cn/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        html_content = response.text
        
        news_list = []

        # 匹配新闻条目
        pattern = r'<a href="([^"]+)"[^>]*>([^<]+)</a><span class="time">([^<]+)</span>'
        matches = re.findall(pattern, html_content)

        for href, title, pub_date in matches:
            if len(title.strip()) < 15:
                continue
            
            # 处理链接
            if href.startswith('../'):
                full_url = "https://english.news.cn" + href[2:]
            elif href.startswith('/'):
                full_url = "https://english.news.cn" + href
            else:
                full_url = href

            # 直接写死 source，避免乱码
            news_list.append({
                "title": title.strip(),
                "url": full_url,
                "date": pub_date.strip(),
                "source": "新华网英文"
            })
        
        # 去重
        seen = set()
        unique = []
        for item in news_list:
            if item['title'] not in seen:
                seen.add(item['title'])
                unique.append(item)
        
        print(f"国际新闻抓取（共 {len(unique)} 条）")
        return unique
    except Exception as e:
        print(f"国际新闻抓取失败: {e}")
    return []

# ========== 优先级筛选 ==========
def get_priority(title):
    # 趣味类关键词（高分）
    if any(word in title for word in ["榴莲", "荔枝", "西瓜", "杨梅", "水果", "芒果"]):
        return 100
    if any(word in title for word in ["小满", "芒种", "夏至", "端午", "节气", "儿童节"]):
        return 80
    if any(word in title for word in ["为什么", "揭秘", "原来", "竟然", "科普"]):
        return 60
    if any(word in title for word in ["高温", "降温", "出行", "旅游", "穿衣"]):
        return 40
    
    # 灾害预警类（保底分）
    if any(word in title for word in ["预警", "暴雨", "山洪", "地质灾害", "渍涝", "台风"]):
        return 10
    
    return 0

def filter_news_top3(news_list):
    """筛选新闻：优先显示符合条件的（priority>=40），总数固定3条"""
    if not news_list:
        return []
    
    for news in news_list:
        news["priority"] = get_priority(news["title"])
    
    # 分类
    matched = [n for n in news_list if n["priority"] >= 40]
    others = [n for n in news_list if n["priority"] < 40]
    
    matched.sort(key=lambda x: x["priority"], reverse=True)
    others.sort(key=lambda x: x["priority"], reverse=True)
    
    result = []
    
    if matched:
        result.extend(matched[:3])
        if len(result) < 3:
            result.extend(others[:3 - len(result)])
    else:
        # 没有符合条件的，直接取前3条
        result = others[:3]
    
    return result[:3]

# ========== 加载缓存（前几天的新闻）==========
def load_cached_news():
    """读取之前保存的新闻数据作为缓存"""
    try:
        with open("news_data.json", "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data.get("china_news", []), data.get("world_news", [])
    except:
        return [], []

# ========== 主函数 ==========
def main():
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("开始抓取新闻...")
    
    # ========== 国内新闻 ==========
    china_news_raw = fetch_china_news()
    
    if china_news_raw:
        china_news = filter_news_top3(china_news_raw)
        print(f"国内新闻（当天）: {len(china_news_raw)} 条总，筛选后 {len(china_news)} 条")
    else:
        cached_china, _ = load_cached_news()
        if cached_china:
            china_news = cached_china[:3]
            print(f"国内新闻（使用缓存，前{len(china_news)}条）")
        else:
            china_news = []
            print("国内新闻: 无数据")
    
    for news in china_news:
        print(f"  - {news['title'][:50]}")
    
    # ========== 国际新闻 ==========
    world_news_raw = fetch_world_news()
    
    if world_news_raw:
        world_news = filter_news_top3(world_news_raw)
        print(f"国际新闻（当天）: {len(world_news_raw)} 条总，筛选后 {len(world_news)} 条")
    else:
        _, cached_world = load_cached_news()
        if cached_world:
            world_news = cached_world[:3]
            print(f"国际新闻（使用缓存，前{len(world_news)}条）")
        else:
            world_news = []
            print("国际新闻: 无数据")
    
    for news in world_news:
        print(f"  - {news['title'][:50]}")
    
    # 保存到文件（使用 utf-8-sig 避免乱码）
    output = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "china_news": china_news,
        "world_news": world_news
    }
    
    with open("news_data.json", "w", encoding="utf-8-sig") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("新闻保存完成")

if __name__ == "__main__":
    main()
