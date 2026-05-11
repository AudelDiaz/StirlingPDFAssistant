from typing import Any, Dict, List, Optional, Tuple
from .base import BaseTool


class ImagesToPDFTool(BaseTool):
    """
    Tool for converting images into a PDF file.
    Based on /api/v1/convert/images/pdf
    """

    name = "images_to_pdf"
    description = "Converts and combines one or more images into a single PDF document."
    endpoint = "/api/v1/convert/img/pdf"

    input_schema = {
        "type": "object",
        "properties": {
            "file_contents": {
                "type": "array",
                "items": {"type": "string", "format": "binary"},
            },
            "filenames": {"type": "array", "items": {"type": "string"}},
            "fit_option": {
                "type": "string",
                "default": "fillPage",
                "enum": ["fillPage", "fitDocumentToImage", "maintainAspectRatio"],
                "description": "How to fit images onto the PDF pages.",
            },
            "color_type": {
                "type": "string",
                "default": "color",
                "enum": ["color", "greyscale", "blackwhite"],
            },
            "auto_rotate": {"type": "boolean", "default": True},
        },
        "required": ["file_contents"],
    }

    def prepare_payload(
        self,
        file_contents: List[bytes],
        filenames: Optional[List[str]] = None,
        fit_option: str = "fillPage",
        color_type: str = "color",
        auto_rotate: bool = True,
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = []
        for i, content in enumerate(file_contents):
            fname = (
                filenames[i] if filenames and i < len(filenames) else f"image_{i}.jpg"
            )
            # Attempt to detect mime type basic (can be improved)
            mime = "image/jpeg"
            if ".png" in fname.lower():
                mime = "image/png"
            files.append(("fileInput", (fname, content, mime)))

        data = {
            "fitOption": fit_option,
            "colorType": color_type,
            "autoRotate": "true" if auto_rotate else "false",
        }
        return files, data


class PdfToWordTool(BaseTool):
    """
    Tool for converting PDF files to Word documents.
    Based on /api/v1/convert/pdf/word
    """

    name = "pdf_to_word"
    description = "Converts a PDF document into an editable Word file (.docx)."
    endpoint = "/api/v1/convert/pdf/word"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {"type": "string", "format": "binary"},
            "filename": {"type": "string", "default": "document.pdf"},
            "output_format": {
                "type": "string",
                "default": "docx",
                "enum": ["doc", "docx", "odt"],
            },
        },
        "required": ["file_content"],
    }

    def prepare_payload(
        self,
        file_content: bytes,
        filename: str = "document.pdf",
        output_format: str = "docx",
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {"outputFormat": output_format}
        return files, data


class URLToPDFTool(BaseTool):
    """
    Tool for converting a website URL to a PDF document.
    Based on /api/v1/convert/url/pdf
    """

    name = "url_to_pdf"
    description = "Converts a public website URL into a clean PDF document."
    endpoint = "/api/v1/convert/url/pdf"

    input_schema = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The full URL starting with http/https.",
            },
            "zoom": {
                "type": "number",
                "default": 1.0,
                "description": "Zoom level for rendering.",
            },
        },
        "required": ["url"],
    }

    def prepare_payload(
        self, url: str, zoom: float = 1.0
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        # This tool doesn't take a file input, only fields
        return [], {"url": url, "zoom": str(zoom)}


class MarkdownToPDFTool(BaseTool):
    """
    Tool for converting a Markdown file to a PDF document.
    Based on /api/v1/convert/markdown/pdf
    """

    name = "markdown_to_pdf"
    description = "Converts a Markdown file (.md) into a PDF document."
    endpoint = "/api/v1/convert/markdown/pdf"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {"type": "string", "format": "binary"},
            "filename": {"type": "string", "default": "document.md"},
        },
        "required": ["file_content"],
    }

    def prepare_payload(
        self, file_content: bytes, filename: str = "document.md", **kwargs
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        # Using mime type text/markdown, but Stirling handles it natively via endpoint
        files = [("fileInput", (filename, file_content, "text/markdown"))]
        return files, {}


class FileToPDFTool(BaseTool):
    """
    Tool for converting generic office documents and text files to PDF.
    Based on /api/v1/convert/file/pdf (LibreOffice)
    """

    name = "file_to_pdf"
    description = "Converts office documents (.docx, .ppt, .xls, .txt, etc.) into a PDF document."
    endpoint = "/api/v1/convert/file/pdf"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {"type": "string", "format": "binary"},
            "filename": {"type": "string", "default": "document.file"},
        },
        "required": ["file_content"],
    }

    def prepare_payload(
        self, file_content: bytes, filename: str = "document.file", **kwargs
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/octet-stream"))]
        return files, {}
