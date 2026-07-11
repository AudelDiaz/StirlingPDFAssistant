from typing import Any, Dict, List, Tuple
from .base import BaseTool


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
            "owner_password": {
                "type": "string",
                "description": "Master password for permissions.",
            },
            "key_length": {"type": "integer", "default": 128, "enum": [40, 128, 256]},
        },
        "required": ["file_content", "password"],
    }

    def prepare_payload(
        self,
        file_content: bytes,
        password: str,
        filename: str = "document.pdf",
        owner_password: str = "",
        key_length: int = 128,
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "password": password,
            "ownerPassword": owner_password,
            "keyLength": str(key_length),
        }
        return files, data


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
                "description": "Comma-separated list of text to redact.",
            },
            "case_sensitive": {"type": "boolean", "default": False},
            "whole_word": {"type": "boolean", "default": False},
        },
        "required": ["file_content", "keywords"],
    }

    def prepare_payload(
        self,
        file_content: bytes,
        keywords: str,
        filename: str = "document.pdf",
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> Tuple[List[tuple], Dict[str, Any]]:
        files = [("fileInput", (filename, file_content, "application/pdf"))]
        data = {
            "listOfTextToRedact": keywords,
            "caseSensitive": "true" if case_sensitive else "false",
            "wholeWord": "true" if whole_word else "false",
        }
        return files, data
