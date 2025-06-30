#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的PDF章节拆分示例
"""

from pdf_chapter_splitter import split_pdf_chapters

def main():
    # 设置PDF文件路径
    pdf_file = input("请输入PDF文件路径（或直接回车使用默认文件）: ").strip()
    
    if not pdf_file:
        pdf_file = "上交专业课-范里安微观经济学现代观点第9版.pdf"
    
    try:
        print(f"开始拆分PDF: {pdf_file}")
        
        # 调用拆分函数
        results = split_pdf_chapters(
            pdf_path=pdf_file,
            chapter_level=1,  # 只拆分大章节
            include_page_numbers=True  # 文件名包含页码
        )
        
        if results:
            print(f"\n✓ 拆分成功！共生成 {len(results)} 个章节文件")
            print("生成的文件:")
            for i, (title, path) in enumerate(results.items(), 1):
                print(f"  {i:2d}. {title}")
        else:
            print("✗ 拆分失败，请检查PDF文件是否有目录信息")
            
    except FileNotFoundError:
        print(f"✗ 错误：找不到文件 {pdf_file}")
    except Exception as e:
        print(f"✗ 错误：{e}")

if __name__ == "__main__":
    main()
