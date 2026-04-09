#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加4月9日的数据到JSON数据源和HTML报告
"""

import json
import os
from datetime import datetime

# 工作目录 - 使用当前脚本所在目录
import sys
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = WORK_DIR

def format_pxb7_content(data):
    """格式化螃蟹账号数据为HTML"""
    html = f"""<h3 class="subsubsection-title">螃蟹账号《王者荣耀世界》商品数据分析报告</h3>
<p><strong>数据总量:</strong> {data['total_count']} 个商品</p>
<p><strong>分析时间:</strong> {data['analysis_date']}</p>

<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">价格分布分析</h4>
<ul>
<li><strong>价格范围:</strong> ¥{data['price_analysis']['min_price']} - ¥{data['price_analysis']['max_price']:,}</li>
<li><strong>中位数价格:</strong> ¥{data['price_analysis']['median_price']:,}</li>
<li><strong>高价商品(≥¥10,000):</strong> {data['price_analysis']['high_value_count']} 个 ({data['price_analysis']['high_value_percentage']}%)</li>
</ul>

<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">价格区间分布</h4>
<ul>
<li>0-500: {data['price_analysis']['price_ranges']['0-500']} 个 ({data['price_analysis']['price_ranges']['0-500']}%)</li>
<li>500-1000: {data['price_analysis']['price_ranges']['500-1000']} 个 ({data['price_analysis']['price_ranges']['500-1000']}%)</li>
<li>1000-5000: {data['price_analysis']['price_ranges']['1000-5000']} 个 ({data['price_analysis']['price_ranges']['1000-5000']}%)</li>
<li>5000-10000: {data['price_analysis']['price_ranges']['5000-10000']} 个 ({data['price_analysis']['price_ranges']['5000-10000']}%)</li>
<li>10000以上: {data['price_analysis']['price_ranges']['10000以上']} 个 ({data['price_analysis']['price_ranges']['10000以上']}%)</li>
</ul>

<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">平台分布</h4>
<ul>
<li><strong>QQ:</strong> {data['platform_distribution']['QQ']} 个 ({data['platform_distribution']['QQ']}%)</li>
<li><strong>微信:</strong> {data['platform_distribution']['微信']} 个 ({data['platform_distribution']['微信']}%)</li>
</ul>

<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">命名特征</h4>
<ul>
<li><strong>单字ID:</strong> {data['naming_features']['single_char_ids']} 个 ({data['naming_features']['single_char_ids']}%)</li>
<li><strong>双字ID:</strong> {data['naming_features']['double_char_ids']} 个 ({data['naming_features']['double_char_ids']}%)</li>
<li><strong>主要风格:</strong> 霸气/中二类 (8%)、诗意/文学类 (4%)、可爱/萌系 (3%)</li>
</ul>"""
    return html

def format_pzds_content(text_content):
    """格式化盼之平台数据为HTML"""
    # 将文本内容转换为HTML格式
    lines = text_content.strip().split('\n')
    html_parts = []
    
    for line in lines:
        if line.startswith('数据分析数量:'):
            html_parts.append(f'<p>{line}</p>')
        elif line.startswith('一、') or line.startswith('二、'):
            html_parts.append(f'<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">{line}</h4>')
        elif line.startswith('1）') or line.startswith('2）') or line.startswith('3）') or line.startswith('4）'):
            html_parts.append(f'<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">{line}</h4>')
        elif line.startswith('主要风格:'):
            html_parts.append(f'<p><strong>{line}</strong></p>')
        elif ':' in line and ('个' in line or '%' in line):
            html_parts.append(f'<li>{line}</li>')
        else:
            html_parts.append(f'<p>{line}</p>')
    
    html = '\n'.join(html_parts)
    return f'<h3 class="subsubsection-title">盼之网站前100个商品分析报告</h3>\n{html}'

def format_weibo_content(data):
    """格式化微博舆情数据为HTML"""
    date_str = data['date'].replace('-', '年').replace('-', '月') + '日'
    
    # 构建分类分布HTML
    categories_html = ""
    for cat, info in sorted(data['category_distribution'].items(), key=lambda x: x[1]['percentage'], reverse=True):
        categories_html += f'<li>{cat} ({info["percentage"]}%, {info["count"]} 条)</li>\n'
    
    # 构建核心发现HTML
    findings_html = ""
    for finding in data['core_findings']:
        findings_html += f'<li>{finding}</li>\n'
    
    # 构建典型帖子示例HTML
    examples_html = ""
    for cat, posts in data['example_posts'].items():
        if posts:
            posts_str = '", "'.join(posts[:2])
            examples_html += f'<li><strong>{cat}：</strong>"{posts_str}"</li>\n'
    
    html = f"""<h3 class="subsubsection-title">微博舆情分析（前 5 页共 {data['total_posts']} 条帖子）</h3>

<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">用户关注点分布</h4>
<ul>
{categories_html}</ul>

<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">核心发现</h4>
<ul>
{findings_html}</ul>

<h4 style="color: #5a67d8; margin: 15px 0 10px 0;">典型帖子示例</h4>
<ul>
{examples_html}</ul>"""
    return html

def add_competitor_data():
    """添加4月9日竞品数据到competitor_data.json"""
    print("正在处理竞品数据...")
    
    # 读取现有数据
    competitor_file = os.path.join(REPORT_DIR, "data", "competitor_data.json")
    with open(competitor_file, 'r', encoding='utf-8') as f:
        competitors = json.load(f)
    
    # 检查是否已有4月9日数据
    existing_dates = [item['date'] for item in competitors]
    target_date = "2026年04月09日"
    
    if target_date in existing_dates:
        print(f"⚠️  {target_date} 已存在，跳过")
        return
    
    # 读取螃蟹数据
    pxb7_file = os.path.join(WORK_DIR, "pxb7_analysis_20260409.json")
    with open(pxb7_file, 'r', encoding='utf-8') as f:
        pxb7_data = json.load(f)
    
    # 读取盼之数据
    pzds_file = os.path.join(WORK_DIR, "pzds_analysis_20260409.txt")
    with open(pzds_file, 'r', encoding='utf-8') as f:
        pzds_text = f.read()
    
    # 构建新的竞品数据条目
    new_entry = {
        "date": target_date,
        "competitors": [
            {
                "name": "竞品一：螃蟹",
                "content": format_pxb7_content(pxb7_data)
            },
            {
                "name": "竞品二：盼之",
                "content": format_pzds_content(pzds_text)
            },
            {
                "name": "竞品三：闲鱼",
                "content": "<p>暂无新动态</p>"
            }
        ]
    }
    
    # 插入到列表开头
    competitors.insert(0, new_entry)
    
    # 保存
    with open(competitor_file, 'w', encoding='utf-8') as f:
        json.dump(competitors, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已添加 {target_date} 竞品数据")

def add_user_feedback_data():
    """添加4月9日用户反馈数据到user_feedback.json"""
    print("正在处理用户反馈数据...")
    
    # 读取现有数据
    feedback_file = os.path.join(REPORT_DIR, "data", "user_feedback.json")
    with open(feedback_file, 'r', encoding='utf-8') as f:
        feedbacks = json.load(f)
    
    # 检查是否已有4月9日数据
    existing_dates = [item['date'] for item in feedbacks]
    target_date = "2026 年 4 月 9 日"
    
    if target_date in existing_dates:
        print(f"⚠️  {target_date} 已存在，跳过")
        return
    
    # 读取微博数据
    weibo_file = os.path.join(WORK_DIR, "weibo_analysis_result.json")
    with open(weibo_file, 'r', encoding='utf-8') as f:
        weibo_data = json.load(f)
    
    # 构建新的用户反馈条目
    new_entry = {
        "date": target_date,
        "channels": [
            {
                "name": "微博",
                "content": format_weibo_content(weibo_data)
            }
        ]
    }
    
    # 插入到列表开头
    feedbacks.insert(0, new_entry)
    
    # 保存
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已添加 {target_date} 用户反馈数据")

if __name__ == "__main__":
    print("=" * 60)
    print("开始添加4月9日数据...")
    print("=" * 60)
    
    add_competitor_data()
    add_user_feedback_data()
    
    print("\n" + "=" * 60)
    print("✅ 所有数据处理完成！")
    print("=" * 60)
