#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀世界市场监控日报生成脚本
自动生成HTML报告并准备部署到GitHub Pages
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = PROJECT_ROOT / "index.html"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)


def load_json_data(filename):
    """加载JSON数据文件"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_json_data(filename, data):
    """保存JSON数据文件"""
    filepath = DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_today_str():
    """获取今日日期字符串"""
    return datetime.now().strftime("%Y年%m月%d日")


def generate_timeline_item(date_str, content_html):
    """生成时间线项目HTML"""
    return f'''
                   <div class="timeline-item">
                        <div class="timeline-date">{date_str}</div>
                        <div class="timeline-content">
                            {content_html}
                        </div>
                   </div>'''


def generate_official_events_section(events_data):
    """生成游戏官方事件部分"""
    if not events_data:
        return ""
    
    timeline_items = []
    for event in sorted(events_data, key=lambda x: x.get('date', ''), reverse=True):
        date_str = event.get('date', '')
        content = event.get('content', '')
        timeline_items.append(generate_timeline_item(date_str, f'<p style="margin: 0; color: #4a5568;">{content}</p>'))
    
    # 添加数据来源说明
    source_note = '''
                  <div class="timeline-item">
                        <div class="timeline-content" style="background: transparent; border: none; padding: 0;">
                           <p style="margin: 0; color: #718096; font-size: 0.9em; font-style: italic;">数据来源于《王者荣耀：世界》游戏官方网站</p>
                        </div>
                   </div>'''
    timeline_items.append(source_note)
    
    return '\n'.join(timeline_items)


def generate_competitor_section(competitor_data):
    """生成竞品动态追踪部分"""
    if not competitor_data:
        return ""
    
    timeline_items = []
    for item in sorted(competitor_data, key=lambda x: x.get('date', ''), reverse=True):
        date_str = item.get('date', '')
        competitors_html = item.get('competitors', [])
        
        competitors_content = ""
        for comp in competitors_html:
            competitors_content += f'''
                            <div class="competitor-card" style="margin-bottom: 20px;">
                               <div class="competitor-name">{comp.get('name', '')}</div>
                                {comp.get('content', '')}
                            </div>'''
        
        timeline_items.append(generate_timeline_item(date_str, competitors_content))
    
    return '\n'.join(timeline_items)


def generate_user_feedback_section(feedback_data):
    """生成用户需求追踪部分"""
    if not feedback_data:
        return ""
    
    timeline_items = []
    for item in sorted(feedback_data, key=lambda x: x.get('date', ''), reverse=True):
        date_str = item.get('date', '')
        channels_html = item.get('channels', [])
        
        channels_content = ""
        for channel in channels_html:
            channels_content += f'''
                            <div class="competitor-card" style="margin-bottom: 20px;">
                                <span class="channel-tag">渠道：{channel.get('name', '')}</span>
                                {channel.get('content', '')}
                            </div>'''
        
        timeline_items.append(generate_timeline_item(date_str, channels_content))
    
    return '\n'.join(timeline_items)


def generate_html_report():
    """生成完整的HTML报告"""
    
    # 加载数据
    official_events = load_json_data("official_events.json")
    competitor_data = load_json_data("competitor_data.json")
    user_feedback = load_json_data("user_feedback.json")
    
    # 生成各部分内容
    official_events_html = generate_official_events_section(official_events)
    competitor_html = generate_competitor_section(competitor_data)
    user_feedback_html = generate_user_feedback_section(user_feedback)
    
    # 生成总结（取最新日期的总结）
    summary = ""
    if official_events:
        latest_event = max(official_events, key=lambda x: x.get('date', ''))
        summary = latest_event.get('summary', '')
    
    # HTML模板
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>王者荣耀世界 - 市场监控日报</title>
   <style>
        * {{
            margin:0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .date {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .content {{
            padding:40px 30px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #2d3748;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            font-weight: 600;
        }}

        .subsubsection-title {{
            font-size: 1.3em;
            color: #4a5568;
            margin:20px 0 15px 0;
            font-weight: 600;
        }}

        .summary-box {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 25px;
            border-radius: 8px;
            border-left: 5px solid #667eea;
        }}

        .summary-box p {{
            color: #2d3748;
            font-size: 1.05em;
            line-height: 1.8;
        }}

        .competitor-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .competitor-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .competitor-name {{
            font-size: 1.4em;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .channel-tag {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 15px;
            font-weight: 500;
        }}

        ul {{
            margin-left: 20px;
            margin-top: 10px;
        }}

        li {{
            margin-bottom: 8px;
            color: #4a5568;
        }}

        li ul {{
            margin-top: 5px;
            margin-left: 20px;
        }}

        p {{
            color: #4a5568;
            margin-bottom: 10px;
        }}

        /* 时间线样式 */
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            left: 8px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }}

        .timeline-item {{
            position: relative;
            margin-bottom: 25px;
            padding-left: 25px;
        }}

        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -26px;
            top: 8px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: white;
            border: 3px solid #667eea;
            z-index: 1;
        }}

        .timeline-date {{
            font-size: 1.1em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            padding: 8px15px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 6px;
            display: inline-block;
        }}

        .timeline-content {{
            background: #f8f9fa;
            border-radius: 8px;
            padding:20px;
            border: 1px solid #e2e8f0;
            margin-top: 10px;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .content {{
                padding: 25px 20px;
            }}

            .section-title {{
                font-size: 1.5em;
            }}

            .competitor-card {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>王者荣耀世界 - 市场监控日报</h1>
            <div class="date">最后更新：{get_today_str()}</div>
       </div>

        <div class="content">
            <!-- 总结部分 -->
            <div class="section">
                <h2 class="section-title">总结</h2>
               <div class="summary-box">
                    <p>{summary}</p>
                </div>
           </div>

            <!-- 游戏官方事件/活动 -->
            <div class="section">
               <h2 class="section-title">1、游戏官方事件/活动</h2>
                <div class="timeline">
{official_events_html}
               </div>
            </div>

           <!-- 竞品动态追踪 -->
            <div class="section">
                <h2 class="section-title">2、竞品动态追踪</h2>
               <div class="timeline">
{competitor_html}
                </div>
            </div>

            <!-- 用户需求追踪 -->
           <div class="section">
                <h2 class="section-title">3、用户需求追踪</h2>
               <div class="timeline">
{user_feedback_html}
                </div>
            </div>
       </div>

        <div class="footer">
            <p>© 2026 市场监控报告 | 数据自动更新</p>
        </div>
    </div>
</body>
</html>'''
    
    # 写入HTML文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ 报告已生成：{OUTPUT_FILE}")
    return OUTPUT_FILE


if __name__ == "__main__":
    generate_html_report()
