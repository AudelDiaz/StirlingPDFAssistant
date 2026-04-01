import abc
from typing import Any, Dict, List, Optional, Tuple

class BaseTool(abc.ABC):
    """
    Abstract base class for all Stirling PDF tools.
    Designed for alignment with the Model Context Protocol (MCP).
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The machine-readable name of the tool."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """A detailed description of what the tool does."""
        pass

    @property
    @abc.abstractmethod
    def endpoint(self) -> str:
        """The API endpoint for this tool."""
        pass

    @property
    @abc.abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema defining the tool's input parameters."""
        pass

    @abc.abstractmethod
    def prepare_payload(self, **kwargs) -> Tuple[List[tuple], Dict[str, Any]]:
        """
        Processes raw arguments into a (files, data) tuple for multipart/form-data.
        
        Returns:
            Tuple[List[tuple], Dict[str, Any]]: (files, form_data)
        """
        pass


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
            "file_content": {"type": "string", "format": "binary", "description": "The PDF file binary content."},
            "filename": {"type": "string", "default": "document.pdf", "description": "Name of the file."},
            "optimize_level": {
                "type": "integer", 
                "default": 1, 
                "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9], 
                "description": "The optimization level (1=low, 9=extreme)."
            },
            "expected_output_size": {"type": "string", "default": "25KB", "description": "Target output size (optional)."}
        },
        "required": ["file_content"]
    }

    def prepare_payload(self, file_content: bytes, filename: str = "document.pdf", optimize_level: int = 1, expected_output_size: str = "") -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "optimizeLevel": str(optimize_level),
            "expectedOutputSize": expected_output_size
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
            "file_content": {"type": "string", "format": "binary", "description": "The PDF file binary content."},
            "filename": {"type": "string", "default": "document.pdf"},
            "languages": {
                "type": "array", 
                "items": {"type": "string"}, 
                "default": ["eng"],
                "description": "List of ISO 639-2 languages (e.g., ['eng', 'spa'])."
            },
            "ocr_type": {
                "type": "string", 
                "default": "skip-text", 
                "enum": ["skip-text", "force-ocr", "Normal"],
                "description": "How to handle existing text layers."
            },
            "ocr_render_type": {
                "type": "string", 
                "default": "hocr", 
                "enum": ["hocr", "sandwich"],
                "description": "The OCR rendering engine (hocr or sandwich)."
            }
        },
        "required": ["file_content"]
    }

    def prepare_payload(self, file_content: bytes, filename: str = "document.pdf", languages: List[str] = None, ocr_type: str = "skip-text", ocr_render_type: str = "hocr") -> Tuple[List[tuple], Dict[str, Any]]:
        if languages is None:
            languages = ["eng"]
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "languages": languages,
            "ocrType": ocr_type,
            "ocrRenderType": ocr_render_type
        }
        return files, data


class MergePDFsTool(BaseTool):
    """
    Tool for merging multiple PDFs into one.
    Based on /api/v1/general/merge-pdfs
    """
    name = "merge_pdfs"
    description = "Merges a list of PDF files into a single document in the provided order."
    endpoint = "/api/v1/general/merge-pdfs"

    input_schema = {
        "type": "object",
        "properties": {
            "file_contents": {"type": "array", "items": {"type": "string", "format": "binary"}},
            "filenames": {"type": "array", "items": {"type": "string"}, "description": "Optional list of filenames for the merged files."},
            "sort_type": {
                "type": "string",
                "default": "orderProvided",
                "enum": ["orderProvided", "byFileName", "byDateModified", "byDateCreated", "byPDFTitle"]
            }
        },
        "required": ["file_contents"]
    }

    def prepare_payload(self, file_contents: List[bytes], filenames: Optional[List[str]] = None, sort_type: str = "orderProvided") -> Tuple[List[tuple], Dict[str, Any]]:
        files = []
        for i, content in enumerate(file_contents):
            fname = filenames[i] if filenames and i < len(filenames) else f"document_{i}.pdf"
            files.append(("fileInput", (fname, content, "application/pdf")))
        return files, {"sortType": sort_type}


class AddPasswordTool(BaseTool):
    """
    Tool for adding password protection to a PDF.
    Based on /api/v1/security/add-password
    """
    name = "add_password"
    description = "Encrypts a PDF document with a user password."
    endpoint = "/api/v1/security/add-password"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {"type": "string", "format": "binary"},
            "filename": {"type": "string", "default": "document.pdf"},
            "password": {"type": "string", "description": "The password to set."},
            "owner_password": {"type": "string", "description": "Master password for permissions."},
            "key_length": {
                "type": "integer", 
                "default": 128, 
                "enum": [40, 128, 256]
            }
        },
        "required": ["file_content", "password"]
    }

    def prepare_payload(self, file_content: bytes, password: str, filename: str = "document.pdf", owner_password: str = "", key_length: int = 128) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "password": password,
            "ownerPassword": owner_password,
            "keyLength": str(key_length)
        }
        return files, data


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
            "file_contents": {"type": "array", "items": {"type": "string", "format": "binary"}},
            "filenames": {"type": "array", "items": {"type": "string"}},
            "fit_option": {
                "type": "string", 
                "default": "fillPage", 
                "enum": ["fillPage", "fitDocumentToImage", "maintainAspectRatio"],
                "description": "How to fit images onto the PDF pages."
            },
            "color_type": {
                "type": "string", 
                "default": "color", 
                "enum": ["color", "greyscale", "blackwhite"]
            },
            "auto_rotate": {"type": "boolean", "default": True}
        },
        "required": ["file_contents"]
    }

    def prepare_payload(self, file_contents: List[bytes], filenames: Optional[List[str]] = None, fit_option: str = "fillPage", color_type: str = "color", auto_rotate: bool = True) -> Tuple[List[tuple], Dict[str, Any]]:
        files = []
        for i, content in enumerate(file_contents):
            fname = filenames[i] if filenames and i < len(filenames) else f"image_{i}.jpg"
            # Attempt to detect mime type basic (can be improved)
            mime = "image/jpeg"
            if ".png" in fname.lower(): mime = "image/png"
            files.append(("fileInput", (fname, content, mime)))
            
        data = {
            "fitOption": fit_option,
            "colorType": color_type,
            "autoRotate": "true" if auto_rotate else "false"
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
                "enum": ["doc", "docx", "odt"]
            }
        },
        "required": ["file_content"]
    }

    def prepare_payload(self, file_content: bytes, filename: str = "document.pdf", output_format: str = "docx") -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {"outputFormat": output_format}
        return files, data


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
                "description": "Compression quality."
            },
            "resolution": {
                "type": "integer", 
                "default": 150,
                "description": "DPI for rendering (lower = smaller file)."
            },
            "colorspace": {
                "type": "string", 
                "default": "grayscale", 
                "enum": ["grayscale", "color"]
            }
        },
        "required": ["file_content"]
    }

    def prepare_payload(self, file_content: bytes, filename: str = "document.pdf", quality: str = "medium", resolution: int = 150, colorspace: str = "grayscale") -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "quality": quality,
            "resolution": str(resolution),
            "colorspace": colorspace,
            "rotation": "slight",
            "noise": "8.0",
            "advancedEnabled": "false"
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
                "description": "Pages to extract, e.g., '1,3,5-10' or 'all'."
            }
        },
        "required": ["file_content"]
    }

    def prepare_payload(self, file_content: bytes, filename: str = "document.pdf", page_numbers: str = "all") -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {"pageNumbers": page_numbers}
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
            "url": {"type": "string", "description": "The full URL starting with http/https."}
        },
        "required": ["url"]
    }

    def prepare_payload(self, url: str) -> Tuple[List[tuple], Dict[str, Any]]:
        # This tool doesn't take a file input, only fields
        # Note: server expects 'urlInput'
        return [], {"urlInput": url}


class AutoRedactTool(BaseTool):
    """
    Tool for automatically redacting text from a PDF.
    Based on /api/v1/security/auto-redact
    """
    name = "auto_redact"
    description = "Masks specific keywords or sensitive info in a PDF automatically."
    endpoint = "/api/v1/security/auto-redact"

    input_schema = {
        "type": "object",
        "properties": {
            "file_content": {"type": "string", "format": "binary"},
            "filename": {"type": "string", "default": "document.pdf"},
            "keywords": {
                "type": "string", 
                "description": "Comma-separated list of text to redact."
            },
            "use_regex": {"type": "boolean", "default": False},
            "whole_word": {"type": "boolean", "default": False}
        },
        "required": ["file_content", "keywords"]
    }

    def prepare_payload(self, file_content: bytes, keywords: str, filename: str = "document.pdf", use_regex: bool = False, whole_word: bool = False) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "listOfText": keywords,
            "useRegex": "true" if use_regex else "false",
            "wholeWordSearch": "true" if whole_word else "false",
            "redactColor": "#000000",
            "customPadding": "0",
            "convertPDFToImage": "false"
        }
        return files, data
