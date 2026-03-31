import logging
import httpx
from typing import Optional, Any, Dict, List, Tuple
from urllib.parse import urljoin
from stirlingpdf_assistant.api.tools import BaseTool

logger = logging.getLogger(__name__)

class StirlingPDFClient:
    """
    Asynchronous client for the Stirling PDF API.
    Designed as a low-level transport for modular Tools.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 60.0):
        """
        Initialize the client.
        
        Args:
            base_url (str): The base URL of your Stirling PDF instance (e.g., http://localhost:8080 or http://host/pdf-editor/).
            api_key (str): Optional API Key (X-API-Key).
            timeout (float): Request timeout in seconds.
        """
        # Ensure base_url ends with a slash for reliable urljoin with relative paths
        self.base_url = base_url if base_url.endswith("/") else f"{base_url}/"
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"X-API-Key": self.api_key} if self.api_key else {}

    async def execute(self, tool: BaseTool, **kwargs) -> bytes:
        """
        Executes a modular Stirling PDF Tool.
        
        Args:
            tool (BaseTool): The tool instance to execute.
            **kwargs: Arguments expected by the tool's prepare_payload method.
            
        Returns:
            bytes: The resulting PDF file content.
            
        Raises:
            Exception: If the API returns an error or processing fails.
        """
        # 1. Prepare Multipart Payload
        files, data = tool.prepare_payload(**kwargs)
        
        # 2. Construct Full URL
        # We lstrip("/") from the tool endpoint and join it to the base_url (which ends in /)
        # urljoin handles this correctly as long as base_url has a trailing slash.
        endpoint = tool.endpoint.lstrip("/")
        url = urljoin(self.base_url, endpoint)
        
        logger.info(f"Executing Tool: {tool.name} at {url}")
        
        # 3. Perform Asynchronous POST Request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    headers=self.headers,
                    files=files,
                    data=data
                )
                
                # Check for success
                if response.status_code == 200:
                    return response.content
                
                # Handle error responses
                error_msg = f"API Error {response.status_code}: {response.text}"
                try:
                    # Attempt to parse Stirling's JSON error response
                    error_json = response.json()
                    if "message" in error_json:
                        error_msg = f"Stirling PDF Error: {error_json['message']}"
                except:
                    pass
                
                logger.error(error_msg)
                raise Exception(error_msg)
                
            except httpx.RequestError as e:
                logger.error(f"HTTP Connection Error: {e}")
                raise Exception(f"Failed to connect to Stirling PDF: {e}")
