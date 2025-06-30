#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试章节识别脚本
"""

import os
from pdf_chapter_splitter import PDFChapterSplitter

# 测试PDF文件
pdf_file = "上交专业课-范里安微观经济学现代观点第9版.pdf"

if os.path.exists(pdf_file):
    print("正在分析PDF目录结构...")
    splitter = PDFChapterSplitter(pdf_file)
    
    # 获取目录
    toc = splitter.get_toc()
    print(f"PDF总页数: {splitter.doc.page_count}")
    print(f"目录项目总数: {len(toc)}")
    
    # 显示前20个目录项目，分析结构
    print("\n前20个目录项目:")
    for i, item in enumerate(toc[:20]):
        level, title, page = item
        print(f"  {i+1:2d}. 级别{level}: {title} (页码: {page})")
    
    # 测试章节筛选
    chapters = splitter.filter_chapters(toc)
    
    print(f"\n识别到的大章节数量: {len(chapters)}")
    for i, (title, start, end) in enumerate(chapters, 1):
        print(f"  {i:2d}. {title} (页码: {start+1}-{end+1})")
    
    splitter.close()
else:
    print(f"PDF文件不存在: {pdf_file}")
