#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 index_with_tabs.html，添加4月9日的日期按钮和内容区块
"""

import json
import re
from datetime import datetime

# 文件路径
HTML_FILE = "index_with_tabs.html"
COMPETITOR_DATA_FILE = "data/competitor_data.json"
USER_FEEDBACK_FILE = "data/user_feedback.json"

def load_json(filepath):
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_date_for_button(date_str):
    """将日期字符串转换为按钮显示格式 (如: 4月9日)"""
    # 支持格式: "2026年04月09日" 或 "2026 年 4 月 9 日"
    match = re.match(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{int(month)}月{int(day)}日"
    return date_str

def format_date_for_id(date_str):
    """将日期字符串转换为ID格式 (如: 04-09)"""
    match = re.match(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{int(month):02d}-{int(day):02d}"
    return date_str

def generate_competitor_html(competitors):
    """生成竞品动态的HTML内容"""
    html_parts = []
    for comp in competitors:
        html_parts.append(f'''
                <div class="competitor-card">
                    <div class="competitor-name">{comp['name']}</div>
                    {comp['content']}
                </div>''')
    return '\n'.join(html_parts)

def generate_user_feedback_html(channels):
    """生成用户反馈的HTML内容"""
    html_parts = []
    for channel in channels:
        html_parts.append(f'''
                <div class="competitor-card">
                    <span class="channel-tag">渠道：{channel['name']}</span>
                    {channel['content']}
                </div>''')
    return '\n'.join(html_parts)

def update_html():
    """更新HTML文件"""
    print("正在加载数据...")
    
    # 加载数据
    competitor_data = load_json(COMPETITOR_DATA_FILE)
    user_feedback_data = load_json(USER_FEEDBACK_FILE)
    
    # 获取4月9日的数据
    target_date_competitor = "2026年04月09日"
    target_date_feedback = "2026 年 4 月 9 日"
    
    competitor_0409 = None
    feedback_0409 = None
    
    for item in competitor_data:
        if item['date'] == target_date_competitor:
            competitor_0409 = item
            break
    
    for item in user_feedback_data:
        if item['date'] == target_date_feedback:
            feedback_0409 = item
            break
    
    if not competitor_0409 or not feedback_0409:
        print("❌ 未找到4月9日的数据")
        return
    
    print("✅ 已找到4月9日数据")
    
    # 读取HTML文件
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 生成日期ID和按钮文本
    date_id = format_date_for_id(target_date_competitor)  # "04-09"
    button_text = format_date_for_button(target_date_competitor)  # "4月9日"
    
    print(f"日期ID: {date_id}, 按钮文本: {button_text}")
    
    # 1. 在竞品动态追踪的日期按钮区域添加4月9日按钮
    # 查找竞品日期按钮区域的开始位置
    competitor_tabs_pattern = r'(<div id="competitor-date-tabs"[^>]*>)'
    match = re.search(competitor_tabs_pattern, html_content)
    
    if match:
        insert_pos = match.end()
        # 插入新的日期按钮(设为active),并将其他按钮的active类移除
        new_button = f'\n                                        <button class="date-tab active" onclick="showCompetitorDate(\'{date_id}\')">{button_text}</button>'
        
        # 先移除所有现有的active类
        html_content = html_content.replace('class="date-tab active"', 'class="date-tab"')
        
        # 在开头插入新按钮
        html_content = html_content[:insert_pos] + new_button + html_content[insert_pos:]
        print("✅ 已添加竞品动态追踪的4月9日按钮")
    else:
        print("❌ 未找到竞品动态追踪的日期按钮区域")
        return
    
    # 2. 在用户需求追踪的日期按钮区域添加4月9日按钮
    user_feedback_tabs_pattern = r'(<div id="user-feedback-date-tabs"[^>]*>)'
    match = re.search(user_feedback_tabs_pattern, html_content)
    
    if match:
        insert_pos = match.end()
        new_button = f'\n                                        <button class="date-tab active" onclick="showUserFeedbackDate(\'{date_id}\')">{button_text}</button>'
        
        # 先移除所有现有的active类
        html_content = html_content.replace('class="date-tab active"', 'class="date-tab"')
        
        # 在开头插入新按钮
        html_content = html_content[:insert_pos] + new_button + html_content[insert_pos:]
        print("✅ 已添加用户需求追踪的4月9日按钮")
    else:
        print("❌ 未找到用户需求追踪的日期按钮区域")
        return
    
    # 3. 在竞品动态追踪的内容区域添加4月9日的内容区块
    competitor_content_pattern = r'(<div id="competitor-content"[^>]*>)'
    match = re.search(competitor_content_pattern, html_content)
    
    if match:
        insert_pos = match.end()
        competitor_html = generate_competitor_html(competitor_0409['competitors'])
        new_content = f'''
                <div id="competitor-{date_id}" class="date-content" style="display: block;">
                    {competitor_html}
                </div>'''
        
        # 隐藏所有现有的内容区块
        html_content = re.sub(r'id="competitor-([^"]+)" class="date-content" style="display: block;"', 
                             r'id="competitor-\1" class="date-content" style="display: none;"', 
                             html_content)
        
        # 在开头插入新内容
        html_content = html_content[:insert_pos] + new_content + html_content[insert_pos:]
        print("✅ 已添加竞品动态追踪的4月9日内容区块")
    else:
        print("❌ 未找到竞品动态追踪的内容区域")
        return
    
    # 4. 在用户需求追踪的内容区域添加4月9日的内容区块
    user_feedback_content_pattern = r'(<div id="user-feedback-content"[^>]*>)'
    match = re.search(user_feedback_content_pattern, html_content)
    
    if match:
        insert_pos = match.end()
        feedback_html = generate_user_feedback_html(feedback_0409['channels'])
        new_content = f'''
                <div id="user-feedback-{date_id}" class="date-content" style="display: block;">
                    {feedback_html}
                </div>'''
        
        # 隐藏所有现有的内容区块
        html_content = re.sub(r'id="user-feedback-([^"]+)" class="date-content" style="display: block;"', 
                             r'id="user-feedback-\1" class="date-content" style="display: none;"', 
                             html_content)
        
        # 在开头插入新内容
        html_content = html_content[:insert_pos] + new_content + html_content[insert_pos:]
        print("✅ 已添加用户需求追踪的4月9日内容区块")
    else:
        print("❌ 未找到用户需求追踪的内容区域")
        return
    
    # 保存更新后的HTML文件
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n✅ HTML文件更新完成！")

if __name__ == "__main__":
    print("=" * 60)
    print("开始更新 index_with_tabs.html...")
    print("=" * 60)
    
    update_html()
    
    print("\n" + "=" * 60)
    print("✅ 所有操作完成！")
    print("=" * 60)
