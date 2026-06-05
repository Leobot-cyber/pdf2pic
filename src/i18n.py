"""UI translations."""

from __future__ import annotations

from typing import Any

TRANSLATIONS: dict[str, dict[str, str]] = {
  "zh": {
    "app_title": "PDF 转图片工具",
    "header": "PDF 转图片",
    "subtitle": "支持批量转换，输出 PNG / JPEG / BMP / TIFF / WEBP / GIF",
    "files_label": "待转换文件",
    "files_selected": "已选 {count} 个文件",
    "drop_hint": "可将 PDF 文件拖拽到此处",
    "add_files": "添加 PDF 文件",
    "remove_selected": "移除选中",
    "clear_list": "清空列表",
    "output_format": "输出格式",
    "dpi": "分辨率 (DPI)",
    "page_range": "页码范围",
    "page_range_hint": "全部 或 1-5 或 1,3,5",
    "output_dir": "输出目录",
    "browse": "浏览...",
    "language": "语言",
    "ready": "就绪",
    "preparing": "准备转换...",
    "converting": "转换中...",
    "start_convert": "开始转换",
    "open_output": "打开输出目录",
    "dialog_select_pdf": "选择 PDF 文件",
    "dialog_select_output": "选择输出目录",
    "pdf_files": "PDF 文件",
    "all_files": "所有文件",
    "info": "提示",
    "error": "错误",
    "done": "完成",
    "no_new_files": "所选文件已在列表中或不是 PDF 文件。",
    "no_files": "请先添加至少一个 PDF 文件。",
    "no_output_dir": "请选择输出目录。",
    "invalid_dpi": "DPI 必须是 72 到 600 之间的整数。",
    "invalid_page_range": "页码范围无效：{detail}",
    "output_not_exist": "输出目录不存在，请先完成一次转换或选择有效目录。",
    "processing_file": "正在处理文件 {current}/{total}...",
    "processing_page": "{name} - 第 {current}/{total} 页",
    "convert_success": "转换完成！共处理 {files} 个 PDF，生成 {images} 张图片。",
    "convert_failed": "转换失败：{error}",
    "open_output_prompt": "是否打开输出目录？",
    "default_output_dir": "PDF转图片",
  },
  "en": {
    "app_title": "PDF to Image",
    "header": "PDF to Image",
    "subtitle": "Batch convert to PNG / JPEG / BMP / TIFF / WEBP / GIF",
    "files_label": "Files to convert",
    "files_selected": "{count} file(s) selected",
    "drop_hint": "Drag PDF files here",
    "add_files": "Add PDF Files",
    "remove_selected": "Remove Selected",
    "clear_list": "Clear List",
    "output_format": "Output Format",
    "dpi": "Resolution (DPI)",
    "page_range": "Page Range",
    "page_range_hint": "all or 1-5 or 1,3,5",
    "output_dir": "Output Directory",
    "browse": "Browse...",
    "language": "Language",
    "ready": "Ready",
    "preparing": "Preparing...",
    "converting": "Converting...",
    "start_convert": "Start Conversion",
    "open_output": "Open Output Folder",
    "dialog_select_pdf": "Select PDF Files",
    "dialog_select_output": "Select Output Directory",
    "pdf_files": "PDF Files",
    "all_files": "All Files",
    "info": "Info",
    "error": "Error",
    "done": "Done",
    "no_new_files": "Selected files are already in the list or not PDF files.",
    "no_files": "Please add at least one PDF file.",
    "no_output_dir": "Please select an output directory.",
    "invalid_dpi": "DPI must be an integer between 72 and 600.",
    "invalid_page_range": "Invalid page range: {detail}",
    "output_not_exist": "Output directory does not exist. Convert first or choose a valid path.",
    "processing_file": "Processing file {current}/{total}...",
    "processing_page": "{name} - page {current}/{total}",
    "convert_success": "Done! Converted {files} PDF(s), generated {images} image(s).",
    "convert_failed": "Conversion failed: {error}",
    "open_output_prompt": "Open output folder?",
    "default_output_dir": "PDFtoImage",
  },
}

LANGUAGE_LABELS = {"zh": "中文", "en": "English"}


class I18n:
    def __init__(self, lang: str = "zh") -> None:
        self._lang = lang if lang in TRANSLATIONS else "zh"

    @property
    def lang(self) -> str:
        return self._lang

    def set_lang(self, lang: str) -> None:
        if lang in TRANSLATIONS:
            self._lang = lang

    def t(self, key: str, **kwargs: Any) -> str:
        text = TRANSLATIONS[self._lang].get(key, TRANSLATIONS["en"].get(key, key))
        if kwargs:
            return text.format(**kwargs)
        return text
