import os
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from mangum import Mangum

app = FastAPI(title="Markdown Table Generator API", version="1.0.0")
# === BT Builds Standard Middleware (auto-injected) ===
from fastapi.middleware.cors import CORSMiddleware as _BTCors
app.add_middleware(_BTCors, allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], expose_headers=["X-RateLimit-Limit","X-RateLimit-Remaining","X-RateLimit-Reset"])

@app.middleware("http")
async def _bt_add_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Powered-By"] = "btbuilds"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API Key from environment variable
API_KEY = os.environ.get("API_KEY", "default-secret-key-change-me")


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from X-API-Key header."""
    if x_api_key is None or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


class GenerateTableRequest(BaseModel):
    headers: List[str]
    rows: List[List[str]]


class ConvertTableRequest(BaseModel):
    markdown_table: str


def generate_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Generate a markdown table from headers and rows."""
    if not headers:
        return ""
    
    # Create header row
    header_row = "| " + " | ".join(headers) + " |"
    
    # Create separator row
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    
    # Create data rows
    data_rows = []
    for row in rows:
        # Pad row with empty strings if needed
        padded_row = row + [""] * (len(headers) - len(row)) if len(row) < len(headers) else row[:len(headers)]
        data_rows.append("| " + " | ".join(padded_row) + " |")
    
    # Combine all rows
    table = [header_row, separator_row] + data_rows
    return "\n".join(table)


def convert_markdown_to_html(markdown_table: str) -> str:
    """Convert markdown table to HTML table."""
    if not markdown_table.strip():
        return "<table></table>"
    
    lines = markdown_table.strip().split("\n")
    
    # Filter out separator lines (containing ---)
    data_lines = [line for line in lines if not "---" in line]
    
    if not data_lines:
        return "<table></table>"
    
    html_rows = []
    for i, line in enumerate(data_lines):
        # Parse the line - remove leading/trailing | and split by |
        cells = [cell.strip() for cell in line.split("|") if cell.strip()]
        
        if i == 0:
            # First row is header
            html_row = "<tr>" + "".join([f"<th>{cell}</th>" for cell in cells]) + "</tr>"
        else:
            # Data rows
            html_row = "<tr>" + "".join([f"<td>{cell}</td>" for cell in cells]) + "</tr>"
        
        html_rows.append(html_row)
    
    return "<table>\n" + "\n".join(html_rows) + "\n</table>"


@app.get("/health")
async def health_check():
    """Health check endpoint - no authentication required."""
    return {"status": "healthy", "service": "markdown-table-generator"}


@app.post("/generate")
@limiter.limit("100/minute")
async def generate_table(
    request: GenerateTableRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate a markdown table from headers and rows.
    
    - **headers**: List of column header strings
    - **rows**: List of rows, where each row is a list of cell strings
    """
    if not request.headers and not request.rows:
        raise HTTPException(status_code=400, detail="Either headers or rows must be provided")
    
    # Determine column count from headers or first row
    col_count = len(request.headers) if request.headers else (len(request.rows[0]) if request.rows else 0)
    
    if col_count == 0:
        raise HTTPException(status_code=400, detail="No columns provided")
    
    markdown_table = generate_markdown_table(request.headers, request.rows)
    
    return {
        "markdown_table": markdown_table,
        "success": True
    }


@app.post("/convert")
@limiter.limit("100/minute")
async def convert_table(
    request: ConvertTableRequest,
    api_key: str = Depends(verify_api_key)
):
    """Convert a markdown table to HTML table.
    
    - **markdown_table**: The markdown table text to convert
    """
    if not request.markdown_table.strip():
        raise HTTPException(status_code=400, detail="Markdown table cannot be empty")
    
    html_table = convert_markdown_to_html(request.markdown_table)
    
    return {
        "html_table": html_table,
        "success": True
    }


# For Vercel deployment with mangum
handler = Mangum(app)