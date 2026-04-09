#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀世界官网活动自动爬取与更新脚本
1. 爬取官网“活动”Tab 最新内容
2. 更新 data/official_events.json
3. 更新 index_with_tabs.html 中的“游戏官方事件/活动”板块
4. 自动 Git 推送
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 缺少依赖库，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
    import requests
    from bs4 import BeautifulSoup

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
HTML_FILE = PROJECT_ROOT / "index_with_tabs.html"
EVENTS_JSON = DATA_DIR / "official_events.json"

# 王者荣耀世界官网活动页 URL
OFFICIAL_URL = "https://world.qq.com/web202603/index.html"

def fetch_official_activities():
    """
    从官网爬取最新活动列表
    返回: list of dict [{'date': 'YYYY年MM月DD日', 'title': '...', 'link': '...'}]
    """
    print(f"🕷️  正在爬取官网: {OFFICIAL_URL}")
    activities = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(OFFICIAL_URL, headers=headers, timeout=10)
        # 腾讯官网常用 utf-8 或 gbk，先尝试 utf-8
        response.encoding = 'utf-8'
        if 'charset=gbk' in response.text[:1000].lower():
            response.encoding = 'gbk'
        
        if response.status_code != 200:
            print(f"⚠️  请求失败，状态码: {response.status_code}")
            return activities
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根据浏览器观察，活动列表在 .news-list-container 下
        news_container = soup.select_one('.news-list-container')
        
        if news_container:
            items = news_container.find_all('div', class_='news-item')
            for item in items:
                title_el = item.select_one('.news-item-title')
                time_el = item.select_one('.news-item-time')
                type_el = item.select_one('.news-item-type-bg')
                
                if not title_el or not time_el:
                    continue
                
                title = title_el.get_text(strip=True)
                time_str = time_el.get_text(strip=True) # e.g., "04-09"
                type_str = type_el.get_text(strip=True) if type_el else ""
                
                # 只关注“活动”类型
                if "活动" not in type_str:
                    continue
                
                # 解析日期
                date_str = datetime.now().strftime("%Y年%m月%d日")
                date_match = re.match(r'(\d{2})-(\d{2})', time_str)
                if date_match:
                    month, day = date_match.groups()
                    year = datetime.now().year
                    try:
                        dt = datetime(year, int(month), int(day))
                        date_str = dt.strftime("%Y年%m月%d日")
                    except:
                        pass
                
                # 获取链接 (通常整个 item 或者 title 是链接，或者父级是链接)
                link = OFFICIAL_URL
                parent_a = item.find_parent('a')
                if parent_a:
                    link = parent_a.get('href', OFFICIAL_URL)
                else:
                    a_tag = item.find('a')
                    if a_tag:
                        link = a_tag.get('href', OFFICIAL_URL)
                
                if title:
                    activities.append({
                        'date': date_str,
                        'title': title,
                        'link': link
                    })
                    
                if len(activities) >= 5:
                    break
        else:
            print("⚠️  未找到新闻容器 (.news-list-container)")
                
    except Exception as e:
        print(f"❌ 爬取出错: {e}")
        import traceback
        traceback.print_exc()
        
    return activities


def load_existing_events():
    """加载已有的事件数据"""
    if EVENTS_JSON.exists():
        with open(EVENTS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_events(events):
    """保存事件数据到 JSON"""
    with open(EVENTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存 {len(events)} 条事件到 official_events.json")


def update_html_content(events):
    """
    更新 index_with_tabs.html 中的“游戏官方事件/活动”板块
    """
    if not HTML_FILE.exists():
        print(f"❌ 找不到文件: {HTML_FILE}")
        return False

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 生成新的 HTML 片段
    timeline_items = []
    # 按日期降序排列
    sorted_events = sorted(events, key=lambda x: x['date'], reverse=True)
    
    for event in sorted_events:
        date_display = event['date'].replace('年', ' 年 ').replace('月', ' 月 ').replace('日', ' 日')
        # 简单美化日期显示，如 "2026 年 04 月 09 日" -> "4 月 9 日" (可选，这里保持原样或简单处理)
        try:
            dt = datetime.strptime(event['date'], "%Y年%m月%d日")
            date_display = f"{dt.month} 月 {dt.day} 日"
        except:
            date_display = event['date']

        item_html = f'''
                    <div class="timeline-item">
                        <div class="timeline-date">{date_display}</div>
                        <div class="timeline-content">
                            <p style="margin: 0; color: #4a5568;"><a href="{event['link']}" target="_blank" style="color: #667eea; text-decoration: none;">{event['title']}</a></p>
                        </div>
                    </div>'''
        timeline_items.append(item_html)

    new_section_content = '\n'.join(timeline_items)

    # 正则替换：找到 <!-- 游戏官方事件/活动 --> 后面的 <div class="timeline">...</div>
    # 注意：这个正则比较脆弱，依赖于 HTML 结构的稳定性
    pattern = r'(<!-- 游戏官方事件/活动 -->\s*<div class="section">\s*<h2 class="section-title">1、游戏官方事件/活动</h2>\s*<div class="timeline">)(.*?)(</div>\s*</div>)'
    
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # 替换中间的内容部分
        new_content = content[:match.start(2)] + new_section_content + content[match.end(2):]
        
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✓ 已成功更新 index_with_tabs.html 中的官方活动板块")
        return True
    else:
        print("⚠️  未能在 HTML 中找到匹配的活动板块结构，可能模板已变更。")
        return False


def git_push():
    """执行 Git 推送"""
    print("🚀 开始 Git 推送...")
    try:
        os.chdir(PROJECT_ROOT)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto Update: Official Events ({datetime.now().strftime('%Y-%m-%d')})"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Git 推送成功！")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def main():
    print("=" * 60)
    print("王者荣耀世界官网活动自动更新脚本")
    print("=" * 60)
    
    # 1. 爬取
    new_activities = fetch_official_activities()
    if not new_activities:
        print("⚠️  未获取到新活动，退出。")
        return

    print(f"📰 获取到 {len(new_activities)} 个最新活动")
    
    # 2. 合并数据
    existing_events = load_existing_events()
    
    # 简单去重：基于标题
    existing_titles = {e['title'] for e in existing_events}
    added_count = 0
    for act in new_activities:
        if act['title'] not in existing_titles:
            existing_events.insert(0, act) # 插入到最前面
            existing_titles.add(act['title'])
            added_count += 1
    
    if added_count == 0:
        print("ℹ️  没有新活动需要更新。")
        # 即使没有新活动，也可以重新生成 HTML 以确保格式正确，或者选择退出
        # 这里选择退出，避免无意义的 Git 提交
        return

    print(f"➕ 新增 {added_count} 条活动记录")
    
    # 3. 保存 JSON
    save_events(existing_events)
    
    # 4. 更新 HTML
    update_html_content(existing_events)
    
    # 5. Git 推送
    git_push()

if __name__ == "__main__":
    main()
