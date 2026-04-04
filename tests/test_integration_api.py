import os
import pytest
import httpx
from stirlingpdf_assistant.api.client import StirlingPDFClient
from stirlingpdf_assistant.api.tools import (
    CompressPDFTool, 
    OCRPDFTool, 
    MergePDFsTool, 
    AddPasswordTool, 
    ScannerEffectTool
)

# Minimal valid PDF for testing
MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources <<>> >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000056 00000 n \n0000000111 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF\n"

@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("STIRLING_PDF_URL") or not os.getenv("STIRLING_PDF_API_KEY"),
    reason="STIRLING_PDF_URL or STIRLING_PDF_API_KEY not set for live integration test"
)
async def test_stirling_api_live_integration():
    """
    Live integration test against a Stirling PDF instance.
    This replaces the old scripts/api_validate.py utility.
    """
    url = os.getenv("STIRLING_PDF_URL")
    api_key = os.getenv("STIRLING_PDF_API_KEY")
    
    client = StirlingPDFClient(url, api_key)
    
    # 1. Test Connectivity & Auth
    async with httpx.AsyncClient() as hclient:
        try:
            # We use /api/v1/info/status as a lightweight health check
            resp = await hclient.get(f"{url.rstrip('/')}/api/v1/info/status", headers={"X-API-KEY": api_key})
            assert resp.status_code == 200, f"Connectivity check failed with status {resp.status_code}: {resp.text}"
        except httpx.RequestError as e:
            pytest.fail(f"Could not connect to Stirling PDF at {url}: {e}")

    # 2. Test Compression
    tool_compress = CompressPDFTool()
    res = await client.execute(tool_compress, file_content=MINIMAL_PDF, optimize_level=1)
    assert len(res) > 0, "Compression returned empty result"

    # 3. Test OCR
    tool_ocr = OCRPDFTool()
    res = await client.execute(tool_ocr, file_content=MINIMAL_PDF, languages=["eng"])
    assert len(res) > 0, "OCR returned empty result"

    # 4. Test Merge
    tool_merge = MergePDFsTool()
    res = await client.execute(tool_merge, file_contents=[MINIMAL_PDF, MINIMAL_PDF])
    assert len(res) > 0, "Merge returned empty result"

    # 5. Test Password Protection
    tool_pw = AddPasswordTool()
    res = await client.execute(tool_pw, file_content=MINIMAL_PDF, password="test-integration")
    assert len(res) > 0, "Password protection returned empty result"
    
    # 6. Test Scanner Effect
    tool_scanner = ScannerEffectTool()
    res = await client.execute(tool_scanner, file_content=MINIMAL_PDF)
    assert len(res) > 0, "Scanner effect returned empty result"
