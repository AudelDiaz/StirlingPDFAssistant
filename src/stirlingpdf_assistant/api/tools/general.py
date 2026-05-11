from typing import Any, Dict, List, Optional, Tuple
from .base import BaseTool


class CompressPDFTool(BaseTool):
    """
    Tool for compressing PDF documents to reduce file size.
    Based on /api/v1/misc/compress-pdf
    """

    name = "compress_pdf"
    description = "Compresses a PDF file to reduce its size by adjusting image quality and removing redundant data."
    endpoint = "/api/v1/misc/compress-pdf"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {
                "type": "string",
                "format": "binary",
                "description": "The PDF file binary content.",
            },
            "filename": {
                "type": "string",
                "default": "document.pdf",
                "description": "Name of the file.",
            },
            "optimize_level": {
                "type": "integer",
                "default": 1,
                "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                "description": "The optimization level (1=low, 9=extreme).",
            },
            "expected_output_size": {
                "type": "string",
                "default": "25KB",
                "description": "Target output size (optional).",
            },
        },
        "required": ["file_content"],
    }

    def prepare_payload(
        self,
        file_content: bytes,
        filename: str = "document.pdf",
        optimize_level: int = 1,
        expected_output_size: str = "",
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "optimizeLevel": str(optimize_level),
            "expectedOutputSize": expected_output_size,
        }
        return files, data


class OCRPDFTool(BaseTool):
    """
    Tool for performing OCR on PDF documents.
    Based on /api/v1/misc/ocr-pdf
    """

    name = "ocr_pdf"
    description = "Performs Optical Character Recognition (OCR) on a PDF to make it searchable or extract text."
    endpoint = "/api/v1/misc/ocr-pdf"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {
                "type": "string",
                "format": "binary",
                "description": "The PDF file binary content.",
            },
            "filename": {"type": "string", "default": "document.pdf"},
            "languages": {
                "type": "array",
                "items": {"type": "string"},
                "default": ["eng"],
                "description": "List of ISO 639-2 languages (e.g., ['eng', 'spa']).",
            },
            "ocr_type": {
                "type": "string",
                "default": "skip-text",
                "enum": ["skip-text", "force-ocr", "Normal"],
                "description": "How to handle existing text layers.",
            },
            "ocr_render_type": {
                "type": "string",
                "default": "hocr",
                "enum": ["hocr", "sandwich"],
                "description": "The OCR rendering engine (hocr or sandwich).",
            },
        },
        "required": ["file_content"],
    }

    def prepare_payload(
        self,
        file_content: bytes,
        filename: str = "document.pdf",
        languages: List[str] = None,
        ocr_type: str = "skip-text",
        ocr_render_type: str = "hocr",
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        if languages is None:
            languages = ["eng"]
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "languages": languages,
            "ocrType": ocr_type,
            "ocrRenderType": ocr_render_type,
        }
        return files, data


class MergePDFsTool(BaseTool):
    """
    Tool for merging multiple PDFs into one.
    Based on /api/v1/general/merge-pdfs
    """

    name = "merge_pdfs"
    description = (
        "Merges a list of PDF files into a single document in the provided order."
    )
    endpoint = "/api/v1/general/merge-pdfs"

    input_schema = {
        "type": "object",
        "properties": {
            "file_contents": {
                "type": "array",
                "items": {"type": "string", "format": "binary"},
            },
            "filenames": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of filenames for the merged files.",
            },
            "sort_type": {
                "type": "string",
                "default": "orderProvided",
                "enum": [
                    "orderProvided",
                    "byFileName",
                    "byDateModified",
                    "byDateCreated",
                    "byPDFTitle",
                ],
            },
        },
        "required": ["file_contents"],
    }

    def prepare_payload(
        self,
        file_contents: List[bytes],
        filenames: Optional[List[str]] = None,
        sort_type: str = "orderProvided",
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = []
        for i, content in enumerate(file_contents):
            fname = (
                filenames[i]
                if filenames and i < len(filenames)
                else f"document_{i}.pdf"
            )
            files.append(("fileInput", (fname, content, "application/pdf")))
        return files, {"sortType": sort_type}


class ScannerEffectTool(BaseTool):
    """
    Tool for applying a 'scanned' look to a digital PDF.
    Based on /api/v1/misc/scanner-effect
    """

    name = "scanner_effect"
    description = "Applies a 'scanned' look to a PDF (grayscaling, slight rotation, noise). Good for making digital docs looks like official scans."
    endpoint = "/api/v1/misc/scanner-effect"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {"type": "string", "format": "binary"},
            "filename": {"type": "string", "default": "document.pdf"},
            "quality": {
                "type": "string",
                "default": "medium",
                "enum": ["low", "medium", "high"],
                "description": "Compression quality.",
            },
            "resolution": {
                "type": "integer",
                "default": 150,
                "description": "DPI for rendering (lower = smaller file).",
            },
            "colorspace": {
                "type": "string",
                "default": "grayscale",
                "enum": ["grayscale", "color"],
            },
        },
        "required": ["file_content"],
    }

    def prepare_payload(
        self,
        file_content: bytes,
        filename: str = "document.pdf",
        quality: str = "medium",
        resolution: int = 150,
        colorspace: str = "grayscale",
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "quality": quality,
            "resolution": str(resolution),
            "colorspace": colorspace,
            "rotation": "slight",
            "noise": "8.0",
            "advancedEnabled": "false",
        }
        return files, data


class SplitPDFTool(BaseTool):
    """
    Tool for splitting a PDF into separate files or extracting page ranges.
    Based on /api/v1/general/split-pages
    """

    name = "split_pages"
    description = "Splits a PDF or extracts specific pages/ranges (e.g., '1,3,5-10')."
    endpoint = "/api/v1/general/split-pages"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {"type": "string", "format": "binary"},
            "filename": {"type": "string", "default": "document.pdf"},
            "page_numbers": {
                "type": "string",
                "default": "all",
                "description": "Pages to extract, e.g., '1,3,5-10' or 'all'.",
            },
        },
        "required": ["file_content"],
    }

    def prepare_payload(
        self,
        file_content: bytes,
        filename: str = "document.pdf",
        page_numbers: str = "all",
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {"pageNumbers": page_numbers}
        return files, data
