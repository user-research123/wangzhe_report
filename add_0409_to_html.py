#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单直接地添加4月9日到index_with_tabs.html
"""

import json
import re

# 文件路径
HTML_FILE = "index_with_tabs.html"
COMPETITOR_DATA_FILE = "data/competitor_data.json"
USER_FEEDBACK_FILE = "data/user_feedback.json"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_date_for_button(date_str):
    match = re.match(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{int(month)}月{int(day)}日"
    return date_str

def format_date_for_id(date_str):
    match = re.match(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{int(month):02d}-{int(day):02d}"
    return date_str

# 加载数据
print("加载数据...")
competitor_data = load_json(COMPETITOR_DATA_FILE)
user_feedback_data = load_json(USER_FEEDBACK_FILE)

# 获取4月9日的数据
competitor_0409 = next((item for item in competitor_data if item['date'] == "2026年04月09日"), None)
feedback_0409 = next((item for item in user_feedback_data if item['date'] == "2026 年 4 月 9 日"), None)

if not competitor_0409 or not feedback_0409:
    print("❌ 未找到4月9日数据")
    exit(1)

print("✅ 找到4月9日数据")

# 读取HTML
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

date_id = "04-09"
button_text = "4月9日"

# 生成竞品动态HTML
competitor_html_parts = []
for comp in competitor_0409['competitors']:
    competitor_html_parts.append(f'''
                <div class="competitor-card">
                    <div class="competitor-name">{comp['name']}</div>
                    {comp['content']}
                </div>''')
competitor_content = '\n'.join(competitor_html_parts)

# 生成用户反馈HTML
feedback_html_parts = []
for channel in feedback_0409['channels']:
    feedback_html_parts.append(f'''
                <div class="competitor-card">
                    <span class="channel-tag">渠道：{channel['name']}</span>
                    {channel['content']}
                </div>''')
feedback_content = '\n'.join(feedback_html_parts)

# 1. 添加竞品动态按钮
print("添加竞品动态按钮...")
old_competitor_tabs = '                <div class="date-tabs" id="competitor-date-tabs">\n                                        <button class="date-tab active"'
new_competitor_tabs = f'''                <div class="date-tabs" id="competitor-date-tabs">
                                        <button class="date-tab active" onclick="showCompetitorDate('{date_id}')">{button_text}</button>
                                        <button class="date-tab"'''

html = html.replace(old_competitor_tabs, new_competitor_tabs, 1)

# 2. 添加用户反馈按钮
print("添加用户反馈按钮...")
old_feedback_tabs = '                <div class="date-tabs" id="user-feedback-date-tabs">\n                                        <button class="date-tab active"'
new_feedback_tabs = f'''                <div class="date-tabs" id="user-feedback-date-tabs">
                                        <button class="date-tab active" onclick="showUserFeedbackDate('{date_id}')">{button_text}</button>
                                        <button class="date-tab"'''

html = html.replace(old_feedback_tabs, new_feedback_tabs, 1)

# 3. 添加竞品动态内容区块
print("添加竞品动态内容区块...")
# 在 <!-- 4月8日内容 --> 之前插入4月9日内容
insert_marker = '<!-- 4月8日内容 -->'
new_competitor_block = f'''                <!-- 4月9日内容 -->
                <div id="competitor-{date_id}" class="date-content" style="display: block;">
                    {competitor_content}
                </div>

                {insert_marker}'''

html = html.replace(insert_marker, new_competitor_block, 1)

# 4. 添加用户反馈内容区块
print("添加用户反馈内容区块...")
# 查找用户反馈内容的开始位置
feedback_content_marker = '<div id="user-feedback-content">'
if feedback_content_marker in html:
    insert_pos = html.find(feedback_content_marker) + len(feedback_content_marker)
    new_feedback_block = f'''
                <div id="user-feedback-{date_id}" class="date-content" style="display: block;">
                    {feedback_content}
                </div>'''
    html = html[:insert_pos] + new_feedback_block + html[insert_pos:]

# 保存
with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ HTML更新完成!")
