#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能更新用户需求追踪板块
自动从 user_feedback.json 读取数据，生成带日期切换的 HTML，并确保最新日期默认 active
"""

import json
import re
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
HTML_FILE = PROJECT_ROOT / "index_with_tabs.html"


def parse_chinese_date(date_str):
    """将中文日期字符串转换为可排序的元组 (year, month, day)"""
    import re
    # 支持多种格式：2026 年 04 月 01 日 或 2026 年 3 月 31 日
    match = re.match(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', date_str)
    if match:
        year, month, day = match.groups()
        return (int(year), int(month), int(day))
    return (0, 0, 0)


def format_date_short(date_str):
    """将完整日期转换为短格式（用于 ID）"""
    # 输入：2026 年 4 月 6 日 -> 输出：04-06
    match = re.match(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{month.zfill(2)}-{day.zfill(2)}"
    return date_str


def format_date_display(date_str):
    """将完整日期转换为显示格式（M 月 D 日）"""
    # 输入：2026 年 4 月 6 日 -> 输出：4 月 6 日
    match = re.match(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{int(month)}月{int(day)}日"
    return date_str


def load_feedback_data():
    """加载用户需求追踪数据"""
    filepath = DATA_DIR / "user_feedback.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def generate_date_buttons(feedback_data, latest_date_id):
    """生成日期切换按钮 HTML"""
    buttons_html = []
    for item in feedback_data:
        date_full = item.get('date', '')
        date_id = format_date_short(date_full)
        date_display = format_date_display(date_full)
        
        # 只有最新日期有 active 类
        active_class = 'active' if date_id == latest_date_id else ''
        buttons_html.append(
            f'                    <button class="date-tab {active_class}" onclick="showUserFeedbackDate(\'{date_id}\')">{date_display}</button>'
        )
    
    return '\n'.join(buttons_html)


def generate_content_blocks(feedback_data, latest_date_id):
    """生成日期内容块 HTML"""
    blocks_html = []
    for item in feedback_data:
        date_full = item.get('date', '')
        date_id = format_date_short(date_full)
        date_display = format_date_display(date_full)
        channels_html = item.get('channels', [])
        
        # 只有最新日期有 active 类
        active_class = 'active' if date_id == latest_date_id else ''
        
        # 生成渠道内容
        channels_content = ""
        for channel in channels_html:
            channel_name = channel.get('name', '')
            channel_content = channel.get('content', '')
            channels_content += f'''
                            <div class="competitor-card" style="margin-bottom: 20px;">
                                <span class="channel-tag">渠道：{channel_name}</span>
                                {channel_content}
                            </div>'''
        
        # 如果没有渠道内容，显示暂无动态
        if not channels_html:
            channels_content = '''
                            <p style="color: #718096; font-style: italic;">暂无新动态</p>'''
        
        block_html = f'''
                <!-- {date_display}内容 -->
                <div id="user-feedback-{date_id}" class="user-feedback-date-content {active_class}">
                    <div class="timeline">
                        <div class="timeline-item">
                            <div class="timeline-date">{date_display}</div>
                            <div class="timeline-content">
{channels_content}
                            </div>
                        </div>
                    </div>
                </div>'''
        
        blocks_html.append(block_html)
    
    return '\n'.join(blocks_html)


def update_html_file(feedback_data):
    """更新 HTML 文件中的用户需求追踪部分"""
    if not feedback_data:
        print("✗ 没有用户需求追踪数据")
        return False
    
    # 按日期降序排序（最新日期在前）
    sorted_data = sorted(feedback_data, key=lambda x: parse_chinese_date(x.get('date', '')), reverse=True)
    
    # 获取最新日期 ID
    latest_date_id = format_date_short(sorted_data[0].get('date', ''))
    
    # 生成新的按钮和内容 HTML
    buttons_html = generate_date_buttons(sorted_data, latest_date_id)
    contents_html = generate_content_blocks(sorted_data, latest_date_id)
    
    # 组合新的用户需求追踪部分
    new_section_html = f'''            <!-- 用户需求追踪（带日期切换） -->
            <div class="section" id="user-feedback-section">
                <h2 class="section-title">3、用户需求追踪</h2>
                
                <!-- 日期切换按钮 -->
                <div class="date-tabs" id="user-feedback-date-tabs">
{buttons_html}
                </div>

{contents_html}
            </div>

        </div>'''
    
    # 读取当前 HTML 文件
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式找到并替换用户需求追踪部分
    # 匹配从注释开始到 </div></div></div> 结束，后面紧跟 </div> 和 <script>
    old_pattern = r'\s*<!-- 用户需求追踪.*?</div>\s*</div>\s*</div>\s*</div>\s*(?=<script>)'
    match = re.search(old_pattern, content, re.DOTALL)
    
    if match:
        content = content[:match.start()] + '\n' + new_section_html + content[match.end():]
        
        # 写入更新后的内容
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 已成功更新用户需求追踪部分")
        print(f"✓ 最新日期 '{sorted_data[0].get('date', '')}' 已设为默认 active")
        print(f"✓ 共更新 {len(sorted_data)} 个日期的内容")
        return True
    else:
        print("✗ 未找到用户需求追踪部分，请检查 HTML 结构")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("用户需求追踪板块智能更新工具")
    print("=" * 60)
    
    # 加载数据
    feedback_data = load_feedback_data()
    
    if not feedback_data:
        print("✗ user_feedback.json 为空或不存在")
        return
    
    print(f"✓ 已加载 {len(feedback_data)} 条用户需求追踪数据")
    
    # 更新 HTML 文件
    success = update_html_file(feedback_data)
    
    if success:
        print("\n✓ 更新完成！请刷新 GitHub Pages 查看效果")
    else:
        print("\n✗ 更新失败")


if __name__ == "__main__":
    main()
