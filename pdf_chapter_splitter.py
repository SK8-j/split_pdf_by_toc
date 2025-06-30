#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF章节拆分工具
根据PDF的章节标签将PDF拆分成多个独立的PDF文件
"""

import os
import re
import fitz  # PyMuPDF
from typing import List, Tuple, Dict
import argparse


class PDFChapterSplitter:
    """PDF章节拆分器"""
    
    def __init__(self, pdf_path: str):
        """
        初始化PDF拆分器
        
        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.output_dir = os.path.splitext(pdf_path)[0] + "_chapters"
        
    def get_toc(self) -> List[List]:
        """
        获取PDF的目录结构
        
        Returns:
            目录列表，每个元素包含[级别, 标题, 页码]
        """
        toc = self.doc.get_toc()
        if not toc:
            print("警告：PDF文件没有找到目录信息")
            return []
        return toc
    
    def filter_chapters(self, toc: List[List], chapter_level: int = 1) -> List[Tuple[str, int, int]]:
        """
        筛选指定级别的章节（只提取大章节，如第一章、第二章等）
        
        Args:
            toc: 目录列表
            chapter_level: 章节级别（1为一级章节，2为二级章节等）
            
        Returns:
            章节信息列表，每个元素包含(章节标题, 开始页码, 结束页码)
        """
        chapters = []
        
        # 只筛选一级章节（大章节）
        chapter_items = [item for item in toc if item[0] == 1]
        
        # 进一步筛选，只保留明显的章节标题，包含数字的章节名
        main_chapters = []
        for item in chapter_items:
            title = item[1].strip()
            
            # 匹配以数字开头的章节标题，如"1  市场"、"2  预算约束"等
            if re.match(r'^\d+\s+', title) and len(title.split()) >= 2:
                # 检查不是以小数点开头的子章节（如 1.1, 2.3等）
                first_part = title.split()[0]
                if '.' not in first_part:
                    main_chapters.append(item)
                    
        # 如果没有找到标准数字章节格式，尝试其他章节模式
        if not main_chapters:
            for item in chapter_items:
                title = item[1].strip()
                # 匹配包含"第X章"、"Chapter X"等模式的标题
                if (re.search(r'第\s*[一二三四五六七八九十\d]+\s*章', title) or 
                    re.search(r'Chapter\s*\d+', title, re.IGNORECASE)):
                    main_chapters.append(item)
        
        # 如果还是没有找到，使用所有一级标题，但排除明显的子章节
        if not main_chapters:
            for item in chapter_items:
                title = item[1].strip()
                # 排除明显的子章节（包含小数点的编号）
                if not re.match(r'^\d+\.\d+', title):
                    main_chapters.append(item)
        
        print(f"筛选后的大章节数量: {len(main_chapters)}")
        for item in main_chapters:
            print(f"  - {item[1]} (页码: {item[2]})")
        
        for i, item in enumerate(main_chapters):
            title = item[1]
            start_page = item[2] - 1  # PyMuPDF使用0基索引
            
            # 确定结束页码
            if i + 1 < len(main_chapters):
                end_page = main_chapters[i + 1][2] - 2
            else:
                end_page = self.doc.page_count - 1
                
            chapters.append((title, start_page, end_page))
            
        return chapters
    
    def clean_filename(self, title: str) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            title: 原始标题
            
        Returns:
            清理后的文件名
        """
        # 移除或替换Windows文件名中的非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        clean_title = re.sub(illegal_chars, '_', title)
        # 移除多余的空格和点
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        clean_title = clean_title.replace('..', '.')
        # 限制文件名长度
        if len(clean_title) > 100:
            clean_title = clean_title[:100]
        return clean_title
    
    def extract_chapter(self, start_page: int, end_page: int, output_path: str) -> bool:
        """
        提取指定页面范围的PDF内容
        
        Args:
            start_page: 开始页码
            end_page: 结束页码
            output_path: 输出文件路径
            
        Returns:
            是否成功提取
        """
        try:
            # 创建新的PDF文档
            new_doc = fitz.open()
            
            # 复制指定页面
            for page_num in range(start_page, end_page + 1):
                if page_num < self.doc.page_count:
                    new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
            
            # 保存新文档
            new_doc.save(output_path)
            new_doc.close()
            return True
            
        except Exception as e:
            print(f"提取章节时出错: {e}")
            return False
    
    def split_by_chapters(self, chapter_level: int = 1, include_page_numbers: bool = True) -> Dict[str, str]:
        """
        按章节拆分PDF
        
        Args:
            chapter_level: 章节级别
            include_page_numbers: 是否在文件名中包含页码信息
            
        Returns:
            拆分结果字典，键为章节标题，值为输出文件路径
        """
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 获取目录
        toc = self.get_toc()
        if not toc:
            print("无法获取PDF目录，尝试使用页面检测方法...")
            return self.split_by_page_detection()
        
        # 筛选章节
        chapters = self.filter_chapters(toc, chapter_level)
        if not chapters:
            print(f"没有找到{chapter_level}级章节")
            return {}
        
        results = {}
        print(f"找到 {len(chapters)} 个章节:")
        
        for i, (title, start_page, end_page) in enumerate(chapters, 1):
            print(f"  {i}. {title} (页码: {start_page + 1}-{end_page + 1})")
            
            # 生成文件名
            clean_title = self.clean_filename(title)
            if include_page_numbers:
                filename = f"{i:02d}_{clean_title}_p{start_page + 1}-{end_page + 1}.pdf"
            else:
                filename = f"{i:02d}_{clean_title}.pdf"
            
            output_path = os.path.join(self.output_dir, filename)
            
            # 提取章节
            if self.extract_chapter(start_page, end_page, output_path):
                results[title] = output_path
                print(f"    ✓ 已保存: {filename}")
            else:
                print(f"    ✗ 提取失败: {title}")
        
        return results
    
    def split_by_page_detection(self, keywords: List[str] = None) -> Dict[str, str]:
        """
        通过页面内容检测章节（当PDF没有目录时使用）
        
        Args:
            keywords: 章节关键词列表，如['第', '章', 'Chapter']
            
        Returns:
            拆分结果字典
        """
        if keywords is None:
            keywords = ['第.*章', 'Chapter.*', '章节.*', '第.*节']
        
        chapters = []
        pattern = '|'.join(keywords)
        
        print("正在扫描页面内容检测章节...")
        
        for page_num in range(self.doc.page_count):
            page = self.doc.load_page(page_num)
            text = page.get_text()
            
            # 查找章节标题
            for line in text.split('\n'):
                line = line.strip()
                if re.search(pattern, line, re.IGNORECASE) and len(line) < 100:
                    chapters.append((line, page_num))
                    print(f"  找到章节: {line} (第{page_num + 1}页)")
                    break
        
        if not chapters:
            print("未检测到章节，将整个PDF作为一个文件处理")
            return self.split_whole_pdf()
        
        # 按章节拆分
        results = {}
        os.makedirs(self.output_dir, exist_ok=True)
        
        for i, (title, start_page) in enumerate(chapters):
            end_page = chapters[i + 1][1] - 1 if i + 1 < len(chapters) else self.doc.page_count - 1
            
            clean_title = self.clean_filename(title)
            filename = f"{i + 1:02d}_{clean_title}_p{start_page + 1}-{end_page + 1}.pdf"
            output_path = os.path.join(self.output_dir, filename)
            
            if self.extract_chapter(start_page, end_page, output_path):
                results[title] = output_path
                print(f"    ✓ 已保存: {filename}")
        
        return results
    
    def split_whole_pdf(self) -> Dict[str, str]:
        """
        将整个PDF复制到输出目录
        
        Returns:
            结果字典
        """
        os.makedirs(self.output_dir, exist_ok=True)
        filename = f"complete_{os.path.basename(self.pdf_path)}"
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)
            new_doc.save(output_path)
            new_doc.close()
            return {"完整文档": output_path}
        except Exception as e:
            print(f"复制PDF时出错: {e}")
            return {}
    
    def close(self):
        """关闭PDF文档"""
        if self.doc:
            self.doc.close()


def split_pdf_chapters(pdf_path: str, chapter_level: int = 1, 
                      include_page_numbers: bool = True,
                      detection_keywords: List[str] = None) -> Dict[str, str]:
    """
    快速拆分PDF章节的便捷函数
    
    Args:
        pdf_path: PDF文件路径
        chapter_level: 章节级别（1为一级章节）
        include_page_numbers: 是否在文件名中包含页码
        detection_keywords: 页面检测时的关键词列表
        
    Returns:
        拆分结果字典，键为章节标题，值为输出文件路径
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    splitter = PDFChapterSplitter(pdf_path)
    try:
        print(f"正在处理PDF: {pdf_path}")
        print(f"总页数: {splitter.doc.page_count}")
        
        # 尝试按目录拆分
        results = splitter.split_by_chapters(chapter_level, include_page_numbers)
        
        # 如果目录拆分失败，尝试页面检测
        if not results:
            results = splitter.split_by_page_detection(detection_keywords)
        
        if results:
            print(f"\n✓ 成功拆分 {len(results)} 个章节")
            print(f"输出目录: {splitter.output_dir}")
        else:
            print("✗ 拆分失败")
        
        return results
        
    finally:
        splitter.close()


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="PDF章节拆分工具")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("--level", "-l", type=int, default=1, 
                       help="章节级别 (默认: 1)")
    parser.add_argument("--no-page-numbers", action="store_true",
                       help="不在文件名中包含页码")
    parser.add_argument("--keywords", "-k", nargs="+",
                       help="页面检测关键词")
    
    args = parser.parse_args()
    
    try:
        results = split_pdf_chapters(
            pdf_path=args.pdf_path,
            chapter_level=args.level,
            include_page_numbers=not args.no_page_numbers,
            detection_keywords=args.keywords
        )
        
        if results:
            print("\n拆分完成！输出文件:")
            for title, path in results.items():
                print(f"  {title}: {path}")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 示例用法
    pdf_file = "上交专业课-范里安微观经济学现代观点第9版.pdf"
    
    if os.path.exists(pdf_file):
        print("发现PDF文件，开始拆分...")
        results = split_pdf_chapters(pdf_file)
    else:
        print("使用方法:")
        print("1. 直接调用函数:")
        print("   results = split_pdf_chapters('your_pdf_file.pdf')")
        print("2. 命令行使用:")
        print("   python pdf_chapter_splitter.py your_pdf_file.pdf")
        print("3. 指定章节级别:")
        print("   python pdf_chapter_splitter.py your_pdf_file.pdf --level 2")