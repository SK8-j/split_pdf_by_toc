#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量创建markdown笔记文件
"""

import os

def create_markdown_files():
    """批量创建5到38的markdown文件"""
    
    # 目标文件夹路径
    folder_path = "markdown笔记"
    
    # 确保文件夹存在
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"创建文件夹: {folder_path}")
    
    # 创建5到38的md文件
    for i in range(5, 39):  # 5到38（包含38）
        filename = f"{i}.md"
        filepath = os.path.join(folder_path, filename)
        
        # 如果文件不存在才创建
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# 微观经济学 第{i}章 思维导图\n\n## {i}. 章节标题\n  - **待补充内容**\n\n## 小结\n  - **总结**：待补充\n")
            print(f"✓ 创建文件: {filename}")
        else:
            print(f"- 文件已存在: {filename}")
    
    print(f"\n完成！共处理 {38-5+1} 个文件")

if __name__ == "__main__":
    create_markdown_files()
