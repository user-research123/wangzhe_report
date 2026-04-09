#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Git历史提交中提取4月9日的内容区块
"""

import subprocess
import re

def run_git_command(cmd):
    """执行Git命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/Users/jiewen/.real/users/user-777da3823a68e71779b041c8e7807df0/workspace/wangzhe_report_repo')
    return result.stdout

# 提取39e907b提交中的完整HTML内容
html_content = run_git_command('git show 39e907b:index_with_tabs.html')

# 查找竞品日期按钮区域
date_tabs_match = re.search(r'<div class="date-tabs" id="competitor-date-tabs">(.*?)</div>', html_content, re.DOTALL)
if date_tabs_match:
    print("=== 竞品日期按钮 ===")
    print(date_tabs_match.group(0)[:500])
    print()

# 查找4月9日的内容区块
content_match = re.search(r'(<div id="competitor-04-09".*?)<!-- 4月8日内容 -->', html_content, re.DOTALL)
if content_match:
    print("=== 4月9日竞品内容区块 (前1000字符) ===")
    print(content_match.group(1)[:1000])
    print()
    
    # 保存到文件
    with open('competitor_0409_block.html', 'w', encoding='utf-8') as f:
        f.write(content_match.group(1))
    print("已保存到 competitor_0409_block.html")
else:
    print("未找到4月9日的内容区块")

# 检查用户需求追踪部分
user_feedback_match = re.search(r'(<div id="user-feedback-04-09".*?)<!-- 4月8日内容 -->', html_content, re.DOTALL)
if user_feedback_match:
    print("\n=== 4月9日用户反馈内容区块 (前1000字符) ===")
    print(user_feedback_match.group(1)[:1000])
else:
    print("\n未找到4月9日的用户反馈内容区块")
