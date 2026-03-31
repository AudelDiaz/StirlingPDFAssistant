import os
import asyncio
import httpx
from dotenv import load_dotenv
from stirlingpdf_assistant.api.client import StirlingPDFClient
from stirlingpdf_assistant.api.tools import (
    CompressPDFTool, 
    OCRPDFTool, 
    MergePDFsTool, 
    AddPasswordTool, 
    ScannerEffectTool
)

async def validate():
    load_dotenv()
    url = os.getenv("STIRLING_PDF_URL")
    api_key = os.getenv("STIRLING_PDF_API_KEY")
    
    if not url or not api_key:
        print("❌ Error: STIRLING_PDF_URL or STIRLING_PDF_API_KEY not found in .env")
        return

    print(f"📡 Testing Stirling PDF at: {url}")
    client = StirlingPDFClient(url, api_key)
    
    # 1. Test Connectivity
    try:
        async with httpx.AsyncClient() as hclient:
            resp = await hclient.get(f"{url.rstrip('/')}/api/v1/info/status", headers={"X-API-KEY": api_key})
            if resp.status_code == 200:
                print("✅ Connectivity: OK")
            else:
                print(f"⚠️ Connectivity check returned {resp.status_code}")
    except Exception as e:
        print(f"❌ Connectivity failed: {e}")

    # Load dummy file
    if not os.path.exists("test_dummy.pdf"):
        print("❌ Error: test_dummy.pdf not found")
        return
        
    with open("test_dummy.pdf", "rb") as f:
        pdf_bytes = f.read()

    # 2. Test Compression
    try:
        print("⏳ Testing CompressPDFTool...", end="", flush=True)
        tool = CompressPDFTool()
        res = await client.execute(tool, file_content=pdf_bytes, optimize_level=5)
        print(f" ✅ Success! ({len(res)} bytes)")
    except Exception as e:
        print(f" ❌ Failed: {e}")

    # 3. Test OCR
    try:
        print("⏳ Testing OCRPDFTool...", end="", flush=True)
        tool = OCRPDFTool()
        res = await client.execute(tool, file_content=pdf_bytes, languages=["eng"])
        print(f" ✅ Success! ({len(res)} bytes)")
    except Exception as e:
        print(f" ❌ Failed: {e}")

    # 4. Test Merge
    try:
        print("⏳ Testing MergePDFsTool...", end="", flush=True)
        tool = MergePDFsTool()
        res = await client.execute(tool, file_contents=[pdf_bytes, pdf_bytes], sort_type="orderProvided")
        print(f" ✅ Success! ({len(res)} bytes)")
    except Exception as e:
        print(f" ❌ Failed: {e}")

    # 5. Test Password
    try:
        print("⏳ Testing AddPasswordTool...", end="", flush=True)
        tool = AddPasswordTool()
        res = await client.execute(tool, file_content=pdf_bytes, password="test", key_length=256)
        print(f" ✅ Success! ({len(res)} bytes)")
    except Exception as e:
        print(f" ❌ Failed: {e}")

    # 6. Test Scanner Effect
    try:
        print("⏳ Testing ScannerEffectTool...", end="", flush=True)
        tool = ScannerEffectTool()
        res = await client.execute(tool, file_content=pdf_bytes, quality="medium", resolution=150, colorspace="grayscale")
        print(f" ✅ Success! ({len(res)} bytes)")
    except Exception as e:
        print(f" ❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(validate())
