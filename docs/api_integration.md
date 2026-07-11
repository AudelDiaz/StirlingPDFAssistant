# API Integration and Tooling

The bot communicates with Stirling PDF through a set of Tool classes. Each Tool wraps one API endpoint and knows how to build the multipart payload.

## The Tool Pattern

Every operation is a class that inherits from `BaseTool`. This keeps things consistent: each tool has a name, description, endpoint, input schema, and a `prepare_payload` method.

```python
class BaseTool(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str: ...
    
    @property
    @abc.abstractmethod
    def description(self) -> str: ...
    
    @property
    @abc.abstractmethod
    def endpoint(self) -> str: ...
    
    @property
    @abc.abstractmethod
    def input_schema(self) -> Dict[str, Any]: ...
    
    @abc.abstractmethod
    def prepare_payload(self, **kwargs) -> Tuple[List[tuple], Dict[str, Any]]: ...
```

## Tools

| Tool Class | Stirling Endpoint | Purpose |
| :--- | :--- | :--- |
| `CompressPDFTool` | `/api/v1/misc/compress-pdf` | Reduce file size (target size, grayscale, linearize). |
| `OCRPDFTool` | `/api/v1/misc/ocr-pdf` | Make PDFs searchable. |
| `MergePDFsTool` | `/api/v1/general/merge-pdfs` | Combine multiple PDFs. |
| `SplitPDFTool` | `/api/v1/general/split-pages` | Extract specific page ranges. |
| `ScannerEffectTool` | `/api/v1/misc/scanner-effect` | Make digital docs look scanned. |
| `AddPasswordTool` | `/api/v1/security/add-password` | Encrypt PDF with a password. |
| `AutoRedactTool` | `/api/v1/security/auto-redact` | Mask keywords in a PDF. |
| `ImagesToPDFTool` | `/api/v1/convert/img/pdf` | Convert images to PDF. |
| `PdfToWordTool` | `/api/v1/convert/pdf/word` | Convert PDF to .docx. |
| `URLToPDFTool` | `/api/v1/convert/url/pdf` | Convert a web URL to PDF. |
| `MarkdownToPDFTool` | `/api/v1/convert/markdown/pdf` | Convert Markdown to PDF. |
| `FileToPDFTool` | `/api/v1/convert/file/pdf` | Convert Office docs, text to PDF. |

## Client Execution

`StirlingPDFClient` takes a tool instance and keyword arguments, calls `prepare_payload`, and sends the request:

```python
result_bytes = await client.execute(
    ocr_tool, 
    file_content=raw_bytes, 
    languages=['eng', 'spa']
)
```

The client handles:
- URL construction (base URL + endpoint).
- Authentication via `X-API-Key` header.
- Multipart payload assembly.
- Error handling and response parsing.
