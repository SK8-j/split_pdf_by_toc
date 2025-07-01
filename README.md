# PDF章节拆分工具使用说明

## 功能描述
这个Python脚本可以根据PDF文件的目录标签将PDF按章节拆分成多个独立的PDF文件。脚本已经优化，只拆分到大章节级别（如第1章、第2章等），不会拆分小节。

## 文件说明
- `pdf_chapter_splitter.py` - 主要的PDF拆分脚本
- `requirements.txt` - 依赖包列表
- `test_chapters.py` - 章节识别测试脚本

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1：直接运行脚本
将PDF文件重命名为 `上交专业课-范里安微观经济学现代观点第9版.pdf` 并放在脚本同目录下，然后运行：
```bash
python pdf_chapter_splitter.py
```

### 方法2：使用函数调用
```python
from pdf_chapter_splitter import split_pdf_chapters

# 拆分PDF
results = split_pdf_chapters('your_pdf_file.pdf')
```

### 方法3：命令行使用
```bash
python pdf_chapter_splitter.py your_pdf_file.pdf
```

### 高级用法
```bash
# 指定章节级别（默认为1，即大章节）
python pdf_chapter_splitter.py your_pdf_file.pdf --level 1

# 不在文件名中包含页码信息
python pdf_chapter_splitter.py your_pdf_file.pdf --no-page-numbers

# 指定页面检测关键词（当PDF没有目录时使用）
python pdf_chapter_splitter.py your_pdf_file.pdf --keywords "第" "章" "Chapter"
```

## 输出结果
- 拆分后的PDF文件将保存在原文件名 + "_chapters" 的文件夹中
- 文件命名格式：`序号_章节标题_页码范围.pdf`
- 例如：`01_1 市场_p31-42.pdf`

## 章节识别逻辑
1. 优先使用PDF内嵌目录：自动识别PDF的目录结构
2. 智能筛选大章节：只提取以数字开头的章节标题（如"1 市场"、"2 预算约束"）
3. 排除子章节：自动过滤小数点编号的子章节（如1.1、2.3等）
4. 备用识别方法：当PDF没有目录时，通过页面内容检测章节

## 测试章节识别
在拆分之前，可以先运行测试脚本查看能识别到哪些章节：
```bash
python test_chapters.py
```

## 注意事项
1. 确保PDF文件有完整的目录信息，否则可能无法正确识别章节
2. 脚本会自动创建输出目录，如果目录已存在会覆盖其中的文件
3. 文件名中的特殊字符会被自动清理，确保文件系统兼容性
4. 建议在拆分大文件前先用测试脚本验证章节识别效果

## 成功案例
本脚本已成功拆分《范里安微观经济学现代观点第9版》PDF文件，将591页的PDF按38个大章节拆分成38个独立的PDF文件，每个文件包含完整的章节内容。

## 技术实现
- 使用PyMuPDF (fitz)库处理PDF文件
- 支持中文文件名和路径
- 自动处理页码转换（PDF内部索引vs显示页码）
- 智能错误处理和进度显示
