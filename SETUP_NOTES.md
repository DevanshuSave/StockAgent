# Stock Agent Setup Notes

## ✅ Current Status

- **Python 3.13** - Installed with venv
- **Virtual Environment** - Using venv for isolated dependencies
- **All dependencies** - Installed successfully
- **ChromaDB + RAG** - Working perfectly
- **Portfolio** - 5 positions loaded and embedded
- **Stock data** - yfinance working (real-time data)

## ⚠️ Pending: Model Configuration

Your REDACTED endpoint `` requires a specific model name.

### Error Received:
```
There are no healthy deployments for this model.
Received Model Group=claude-3-5-sonnet-20241022
```

### What This Means:
- The endpoint uses **LiteLLM proxy**
- It has specific model names configured
- Standard Anthropic model names don't work

### What You Need:
Ask your **REDACTED admin** for:
1. The correct model identifier/name to use
2. List of available models on the endpoint
3. Link to internal API documentation

### Tried Model Names (all failed):
- claude-3-5-sonnet-20241022
- claude-3-5-sonnet
- claude-3-sonnet
- claude-sonnet-3-5
- claude-3-opus
- (empty/default)

### Where to Update:
Once you get the model name, update in `.env`:
```bash
ANTHROPIC_MODEL="your-model-name-here"
```

---

## 🎯 What Works Right Now (Without AI Agent):

Even without the correct model name, you can use these features:

### 1. Stock Data Analysis
```bash
python main.py
```
(After activating venv) Use the interactive agent to analyze any stock.

### 2. Portfolio View
Menu option 2 - View your portfolio with current values

### 3. Portfolio Management
- Add positions (option 3)
- Remove positions (option 4)

### 4. Direct Analysis Tools
All the analysis functions work:
- `tools/stock_data.py` - Real-time prices, fundamentals
- `analysis/stock_analyzer.py` - Valuation, growth, risk
- `analysis/recommendation_engine.py` - Buy/sell/hold logic

---

## 📊 Example: Manual Analysis

```python
# In Python shell:
from tools.stock_data import get_current_stock_price, get_stock_fundamentals
from analysis.recommendation_engine import recommend_action

# Get stock data
price = get_current_stock_price("AAPL")
print(price)

# Get recommendation
rec = recommend_action("AAPL")
print(rec["reasoning"])
```

---

## 🚀 Once Model Name is Configured:

The full AI agent will work with:
- Natural language queries: "Should I buy NVDA?"
- Portfolio analysis: "How diversified am I?"
- Semantic search: "Show me tech stocks"
- Stock comparisons: "Compare AAPL and MSFT"

---

## 📞 Support Contacts:

- **REDACTED Admin** - For model name
- **Internal LLM Team** - For endpoint documentation
- Check: REDACTED internal wiki, Confluence, or Slack channels

---

## 🔍 Diagnostic Scripts Available:

- `tests/test_setup.py` - Verify imports, config, portfolio, validators, ChromaDB
- `tests/test_endpoint.py` - Test model names and endpoint discovery
- `main.py` - Interactive agent (analyze stocks, view portfolio, get recommendations)

## 🐍 Python 3.13 & venv Setup

**Activation:**
```bash
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

**Deactivation:**
```bash
deactivate
```

**After activation, run Python directly:**
```bash
python main.py
pip install -r requirements.txt
```
