import pytest
import json
from stirlingpdf_assistant.api.tools import (
    CompressPDFTool, 
    OCRPDFTool, 
    MergePDFsTool, 
    AddPasswordTool,
    ScannerEffectTool,
    SplitPDFTool,
    URLToPDFTool,
    AutoRedactTool,
    MarkdownToPDFTool
)

def test_tool_schemas_are_valid():
    """Verify that each tool provides a valid JSON Schema."""
    tools = [
        CompressPDFTool(), OCRPDFTool(), MergePDFsTool(), AddPasswordTool(),
        ScannerEffectTool(), SplitPDFTool(), URLToPDFTool(), AutoRedactTool(),
        MarkdownToPDFTool()
    ]
    for tool in tools:
        schema = tool.input_schema
        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        # Verify it can be serialized to JSON (standard check for MCP compatibility)
        json_str = json.dumps(schema)
        assert len(json_str) > 0

def test_compress_payload():
    tool = CompressPDFTool()
    content = b"fake pdf"
    files, data = tool.prepare_payload(file_content=content, filename="test.pdf", optimize_level=2)
    
    assert files[0][0] == "fileInput"
    assert files[0][1][0] == "test.pdf"
    assert files[0][1][1] == content
    assert data["optimizeLevel"] == "2"

def test_ocr_payload():
    tool = OCRPDFTool()
    content = b"fake pdf"
    files, data = tool.prepare_payload(file_content=content, languages=["spa"], ocr_type="force-ocr")
    
    assert data["languages"] == ["spa"]
    assert data["ocrType"] == "force-ocr"
    assert data["ocrRenderType"] == "hocr" # Default

def test_merge_payload():
    tool = MergePDFsTool()
    contents = [b"pdf1", b"pdf2"]
    files, data = tool.prepare_payload(file_contents=contents)
    
    assert len(files) == 2
    assert files[0][0] == "fileInput"
    assert files[1][0] == "fileInput"
    assert files[0][1][1] == contents[0]
    assert files[1][1][1] == contents[1]

def test_password_payload():
    tool = AddPasswordTool()
    content = b"pdf"
    files, data = tool.prepare_payload(file_content=content, password="secret")
    
    assert data["password"] == "secret"
    assert data["keyLength"] == "128"

def test_split_payload():
    tool = SplitPDFTool()
    content = b"fake pdf"
    files, data = tool.prepare_payload(file_content=content, page_numbers="1-5")
    
    assert files[0][1][1] == content
    assert data["pageNumbers"] == "1-5"

def test_url_payload():
    tool = URLToPDFTool()
    files, data = tool.prepare_payload(url="https://google.com", zoom=1.5)
    
    assert len(files) == 0
    assert data["url"] == "https://google.com"
    assert data["zoom"] == "1.5"

def test_redact_payload():
    tool = AutoRedactTool()
    content = b"fake pdf"
    files, data = tool.prepare_payload(file_content=content, keywords="secret,admin", case_sensitive=True)
    
    assert files[0][1][1] == content
    assert data["listOfTextToRedact"] == "secret,admin"
    assert data["caseSensitive"] == "true"

def test_markdown_payload():
    tool = MarkdownToPDFTool()
    content = b"fake md"
    files, data = tool.prepare_payload(file_content=content, filename="test.md")
    
    assert files[0][0] == "fileInput"
    assert files[0][1][0] == "test.md"
    assert files[0][1][1] == content
    assert files[0][1][2] == "text/markdown"
    assert len(data) == 0
