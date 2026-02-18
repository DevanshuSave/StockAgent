# Stock Agent Setup Notes

## Setup

1. Create and activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set your environment variables
4. Run: `python main.py`

## Configuration

Set these as system environment variables or in `.env`:

```bash
ANTHROPIC_API_KEY=       # or ANTHROPIC_AUTH_TOKEN
ANTHROPIC_BASE_URL=      # optional custom endpoint
ANTHROPIC_MODEL=         # optional model override
```

## Features

- **Interactive Agent** — Natural language stock analysis and recommendations
- **Portfolio Management** — Add/remove positions, view summary with live prices
- **Stock Analysis** — Valuation, growth, risk metrics via yfinance
- **RAG Search** — Semantic search over portfolio using ChromaDB

## Usage

```bash
python main.py
```

Menu options:
1. Chat with Agent (stock analysis and recommendations)
2. View Portfolio Summary
3. Add Position
4. Remove Position
5. Refresh Portfolio Embeddings

## Manual Analysis

```python
from tools.stock_data import get_current_stock_price, get_stock_fundamentals
from analysis.recommendation_engine import recommend_action

price = get_current_stock_price("AAPL")
rec = recommend_action("AAPL")
print(rec["reasoning"])
```

## Diagnostic Scripts

- `python -m tests.test_setup` — Verify imports, config, portfolio, validators, ChromaDB
- `python -m tests.test_endpoint` — Test model names and endpoint discovery

## Virtual Environment

```bash
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac
deactivate                  # exit
```
