# Markdown Table Generator API

A FastAPI service for generating and converting markdown tables. Perfect for developers who need to create tables for documentation, READMEs, and reports.

## Features

- Generate markdown tables from structured data
- Convert markdown tables to HTML tables
- API key authentication for secure access
- Rate limiting (100 requests per minute per API key)
- Ready for Vercel deployment

## Installation

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Environment Variables

- `API_KEY` - Your secret API key for authentication (defaults to `default-secret-key-change-me`)

## API Endpoints

### GET /health

Health check endpoint - no authentication required.

**cURL Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "markdown-table-generator"
}
```

---

### POST /generate

Generate a markdown table from headers and rows. Requires API key authentication via `X-API-Key` header.

**Request Body:**
```json
{
  "headers": ["Column 1", "Column 2", "Column 3"],
  "rows": [
    ["Row 1 Cell 1", "Row 1 Cell 2", "Row 1 Cell 3"],
    ["Row 2 Cell 1", "Row 2 Cell 2", "Row 2 Cell 3"]
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: default-secret-key-change-me" \
  -d '{
    "headers": ["Name", "Age", "City"],
    "rows": [
      ["Alice", "30", "New York"],
      ["Bob", "25", "Los Angeles"],
      ["Charlie", "35", "Chicago"]
    ]
  }'
```

**Response:**
```json
{
  "markdown_table": "| Name | Age | City |\n| --- | --- | --- |\n| Alice | 30 | New York |\n| Bob | 25 | Los Angeles |\n| Charlie | 35 | Chicago |",
  "success": true
}
```

**Rendered Markdown Table:**
```
| Name | Age | City |
| --- | --- | --- |
| Alice | 30 | New York |
| Bob | 25 | Los Angeles |
| Charlie | 35 | Chicago |
```

---

### POST /convert

Convert a markdown table to an HTML table. Requires API key authentication via `X-API-Key` header.

**Request Body:**
```json
{
  "markdown_table": "| Name | Age |\n| --- | --- |\n| Alice | 30 |"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: default-secret-key-change-me" \
  -d '{
    "markdown_table": "| Name | Age | City |\n| --- | --- | --- |\n| Alice | 30 | New York |\n| Bob | 25 | Los Angeles |"
  }'
```

**Response:**
```json
{
  "html_table": "<table>\n<tr><th>Name</th><th>Age</th><th>City</th></tr>\n<tr><td>Alice</td><td>30</td><td>New York</td></tr>\n<tr><td>Bob</td><td>25</td><td>Los Angeles</td></tr>\n</table>",
  "success": true
}
```

---

## Error Responses

### Missing or Invalid API Key (401)
```json
{
  "detail": "Invalid or missing API key"
}
```

### No Data Provided (400)
```json
{
  "detail": "Either headers or rows must be provided"
}
```

### Empty Markdown Table (400)
```json
{
  "detail": "Markdown table cannot be empty"
}
```

## Rate Limiting

All authenticated endpoints are limited to **100 requests per minute per IP address**. When the limit is exceeded, you'll receive a 429 status code.

## Deployment to Vercel

1. Set the `API_KEY` environment variable in your Vercel project settings
2. Deploy using Vercel CLI or connect to your Git repository:

```bash
vercel --prod
```

The `vercel.json` is pre-configured for Python deployment.

## Postman
[![Run in Postman](https://run.pstmn.io/button.svg)](https://raw.githubusercontent.com/BT-Builds/markdown-table-generator/main/postman_collection.json)
