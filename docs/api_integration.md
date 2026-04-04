# API Integration & Tooling

The integration with Stirling PDF is designed to be extensible and follows patterns seen in the **Model Context Protocol (MCP)**.

## The Tool Pattern

Every PDF operation is encapsulated in a "Tool" class inheriting from `BaseTool`. This approach provides several benefits:
- **Consistency**: All tools share a similar structure for input validation and payload preparation.
- **Extensibility**: Adding a new Stirling PDF feature only requires creating a new Tool class.
- **AI-Readiness**: The `input_schema` property (JSON Schema) allows an LLM to understand what parameters a tool requires.

### BaseTool Interface
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

## Supported Operations

Currently, the following tools are implemented:

| Tool Class | Stirling Endpoint | Purpose |
| :--- | :--- | :--- |
| `CompressPDFTool` | `/api/v1/misc/compress-pdf` | Reduce file size. |
| `OCRPDFTool` | `/api/v1/misc/ocr-pdf` | Make PDFs searchable. |
| `MergePDFsTool` | `/api/v1/general/merge-pdfs` | Combine multiple PDFs. |
| `AddPasswordTool` | `/api/v1/security/add-password` | Encrypt PDF with a password. |
| `ImagesToPDFTool` | `/api/v1/convert/img/pdf` | Convert images to PDF. |
| `PdfToWordTool` | `/api/v1/convert/pdf/word` | Convert PDF to .docx. |
| `ScannerEffectTool` | `/api/v1/misc/scanner-effect` | Apply "scanned" look. |

## Client Execution

The `StirlingPDFClient` acts as the executor for these tools:

```python
# Example execution
result_bytes = await client.execute(
    ocr_tool, 
    file_content=raw_bytes, 
    languages=['eng', 'spa']
)
```

The client handles:
- URL construction.
- Authentication (`X-API-Key`).
- Multipart payload generation (via the Tool's `prepare_payload`).
- Error handling and response parsing.
