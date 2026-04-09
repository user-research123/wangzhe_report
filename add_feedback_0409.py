#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加用户反馈的4月9日内容到index_with_tabs.html
"""

import json
import re

HTML_FILE = "index_with_tabs.html"
USER_FEEDBACK_FILE = "data/user_feedback.json"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载数据
feedback_data = load_json(USER_FEEDBACK_FILE)
feedback_0409 = next((item for item in feedback_data if item['date'] == "2026 年 4 月 9 日"), None)

if not feedback_0409:
    print("❌ 未找到4月9日用户反馈数据")
    exit(1)

print("✅ 找到4月9日用户反馈数据")

# 读取HTML
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# 生成用户反馈HTML
feedback_html_parts = []
for channel in feedback_0409['channels']:
    feedback_html_parts.append(f'''
                            <div class="competitor-card" style="margin-bottom: 20px;">
                                <span class="channel-tag">渠道：{channel['name']}</span>
                                {channel['content']}
                            </div>''')
feedback_content = '\n'.join(feedback_html_parts)

# 在用户反馈的 <!-- 4月8日内容 --> 之前插入4月9日内容
insert_marker = '                <!-- 4月8日内容 -->\n                                <!-- 4 月 8 日内容 -->\n                <div id="user-feedback-04-08"'

new_block = f'''                <!-- 4月9日内容 -->
                <div id="user-feedback-04-09" class="user-feedback-date-content active">
                    <div class="timeline">
                        <div class="timeline-item">
                            <div class="timeline-date">4月9日</div>
                            <div class="timeline-content">
{feedback_content}
                            </div>
                        </div>
                    </div>
                </div>

                {insert_marker.split(chr(10))[0]}'''

html = html.replace(insert_marker, new_block, 1)

# 保存
with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ 用户反馈4月9日内容已添加!")
