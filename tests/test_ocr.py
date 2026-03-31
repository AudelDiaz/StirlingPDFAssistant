import pytest
from unittest.mock import AsyncMock, patch
from stirlingpdf_assistant.api.client import StirlingPDFClient
from stirlingpdf_assistant.api.tools import CompressPDFTool, OCRPDFTool

# Minimal valid PDF
MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources <<>> >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000056 00000 n \n0000000111 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF\n"

@pytest.mark.asyncio
async def test_stirling_compress_mocked():
    """Test PDF compression using the new Tool architecture with a mocked API response."""
    client = StirlingPDFClient("http://fake-server:8080", "fake-key")
    tool = CompressPDFTool()

    # Mock the httpx post call
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        # Simulate a successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = b"compressed-pdf-data"
        
        result = await client.execute(tool, file_content=MINIMAL_PDF, filename="test.pdf")
        
        assert result == b"compressed-pdf-data"
        mock_post.assert_called_once()
        # Verify the endpoint used
        args, kwargs = mock_post.call_args
        assert "/api/v1/misc/compress-pdf" in args[0]

@pytest.mark.asyncio
async def test_stirling_ocr_mocked():
    """Test PDF OCR using the new Tool architecture with a mocked API response."""
    client = StirlingPDFClient("http://fake-server:8080", "fake-key")
    tool = OCRPDFTool()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = b"ocr-pdf-data"
        
        result = await client.execute(tool, file_content=MINIMAL_PDF, languages=["spa"])
        
        assert result == b"ocr-pdf-data"
        mock_post.assert_called_once()
        # Verify data passed
        args, kwargs = mock_post.call_args
        assert kwargs["data"]["languages"] == ["spa"]
