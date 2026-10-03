# Stock Recommendation Agent 📈🤖

An AI-powered stock analysis and portfolio management system built with Claude AI, yfinance, ChromaDB, and Python.

## Features

- 🤖 **AI-Powered Recommendations**: Get buy/sell/hold recommendations using Claude AI
- 📊 **Real-Time Stock Data**: Fetch current prices, fundamentals, and historical data
- 💼 **Portfolio Management**: Track your holdings with automatic gain/loss calculations
- 🔍 **Semantic Search**: Find relevant holdings using natural language (RAG with ChromaDB - Python 3.11-3.13)
- 📈 **Comprehensive Analysis**: Valuation, growth, risk, and diversification metrics
- 🎯 **Sector Analysis**: Track sector exposure and concentration risks
- 🎨 **Beautiful CLI**: Rich terminal interface with colors and formatting

## Architecture

```
User CLI → Agent Orchestrator (Claude API) → Tools:
                                              ├─ Stock Data (yfinance)
                                              ├─ RAG Engine (ChromaDB)
                                              ├─ Portfolio Manager (JSON)
                                              └─ Analysis Engine (metrics)
```

## Installation

### Prerequisites

- **Python 3.11 - 3.13** (RAG features require ChromaDB compatibility; Python 3.14+ not yet supported)
- Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))

### Setup

1. **Navigate to the project directory:**
   ```bash
   cd path/to/StockAgent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key:**
   - Copy `.env.example` to `.env` (or create `.env` from scratch)
   - Add your Anthropic API key from [console.anthropic.com](https://console.anthropic.com):
     ```
     ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
     ```
   - **⚠️ Never commit `.env` to git** (it's in .gitignore)

5. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

### Main Menu Options

1. **💬 Chat with Agent** - Interactive AI assistant for stock analysis
2. **📊 View Portfolio Summary** - Display all positions with current values
3. **➕ Add Position** - Add stocks to your portfolio
4. **➖ Remove Position** - Remove stocks from portfolio
5. **🔄 Refresh Embeddings** - Update RAG embeddings after portfolio changes
6. **ℹ️ About** - View system information

### Example Queries

When chatting with the agent, try:

- **Stock Analysis:**
  - "Should I buy NVDA?"
  - "Analyze Apple stock"
  - "What's the outlook for Tesla?"

- **Portfolio Insights:**
  - "How diversified is my portfolio?"
  - "What's my tech sector exposure?"
  - "Show me my high-growth stocks"

- **Comparisons:**
  - "Compare AAPL and MSFT"
  - "Which is better, AMD or INTC?"

- **Context-Aware:**
  - "Find stocks similar to my AAPL position"
  - "Do I have too much tech exposure?"

## Project Structure

```
StockAgent/
├── main.py                      # CLI entry point
├── config.py                    # Configuration constants
├── requirements.txt             # Python dependencies
├── .env                        # API keys (not in git)
│
├── agent/                      # Agent orchestration
│   ├── orchestrator.py         # Main agent loop with Claude API
│   ├── tool_definitions.py     # Tool schemas (14 tools)
│   └── tool_executor.py        # Routes tool calls
│
├── tools/                      # Tool implementations
│   ├── stock_data.py           # yfinance wrappers
│   ├── portfolio_tools.py      # Portfolio CRUD
│   ├── rag_tools.py            # RAG/semantic search
│   └── analysis_tools.py       # Analysis functions
│
├── rag/                        # RAG system
│   ├── embedder.py             # ChromaDB embedding
│   ├── retriever.py            # Semantic search
│   └── portfolio_processor.py  # Convert positions to documents
│
├── portfolio/                  # Portfolio management
│   ├── models.py               # Pydantic data models
│   └── manager.py              # JSON CRUD operations
│
├── analysis/                   # Analysis engines
│   ├── stock_analyzer.py       # Valuation, growth, risk
│   ├── portfolio_analyzer.py   # Diversification metrics
│   └── recommendation_engine.py # Buy/sell/hold logic
│
├── utils/                      # Utilities
│   ├── logger.py               # Logging setup
│   └── validators.py           # Input validation
│
└── data/                       # Data storage
    ├── portfolio.json          # User holdings
    └── chroma_db/              # Vector embeddings
```

## Agent Tools (14 Total)

### Stock Data Tools
1. `get_current_stock_price` - Real-time price, volume, market cap
2. `get_stock_fundamentals` - P/E, EPS, sector, industry, growth metrics
3. `get_historical_data` - Price history and returns
4. `get_stock_news` - Recent news articles

### Portfolio Tools
5. `get_portfolio_summary` - Complete portfolio overview
6. `get_position_details` - Specific position information
7. `add_position` - Add/update holdings
8. `remove_position` - Remove holdings

### RAG Tools
9. `search_portfolio_context` - Semantic search ("tech stocks")
10. `get_sector_exposure` - Sector concentration analysis
11. `find_similar_holdings` - Find similar positions

### Analysis Tools
12. `analyze_stock_valuation` - Valuation metrics and assessment
13. `calculate_portfolio_metrics` - Diversification score, sector allocation
14. `recommend_action` - Buy/sell/hold recommendation with reasoning

## Configuration

Edit `config.py` or `.env` to customize:

- **Agent settings**:
  - Model (default: Claude Haiku 4.5) - set `ANTHROPIC_MODEL` in `.env` to override
  - Max iterations (default: 10)
- **RAG settings**: Collection name, top-K results, embedding model
- **Analysis thresholds**: P/E ratio threshold, sector concentration limits
- **Data paths**: Portfolio file, database location

## Sample Portfolio

The system comes with a sample portfolio in `data/portfolio.json`:

- **AAPL** (Apple) - Technology
- **MSFT** (Microsoft) - Technology
- **JNJ** (Johnson & Johnson) - Healthcare
- **XOM** (ExxonMobil) - Energy
- **JPM** (JPMorgan) - Financials

You can modify this file or use the CLI to manage positions.

## How It Works

### 1. Agent Orchestration
The agent uses Claude's function calling to:
- Understand user intent
- Select and execute relevant tools
- Synthesize results into recommendations

### 2. RAG System (Optional)
Portfolio positions are embedded as rich text documents:
```
Position: AAPL (Apple Inc.)
Sector: Technology | Industry: Consumer Electronics
Holdings: 50 shares @ $150.25 purchased 2024-01-15
Current Value: $9,500 | Gain: +26.5%
Fundamentals: P/E Ratio: 29.5 | Market Cap: $2.9T
```

ChromaDB enables semantic queries like "show me tech stocks" or "high growth companies".

**Note**: RAG features require Python 3.11-3.13. If ChromaDB is unavailable, the system degrades gracefully and continues operating with basic portfolio tools.

### 3. Analysis Engine
The recommendation engine combines:
- **Valuation**: P/E ratio, profitability, debt levels
- **Growth**: Revenue/earnings growth, momentum
- **Risk**: Beta (volatility), financial leverage
- **Portfolio Context**: Sector exposure, diversification, existing positions

### 4. Recommendation Logic
**For BUY decisions:**
- Signal ratio ≥ 0.7 → Strong Buy
- Signal ratio ≥ 0.5 → Cautious Buy
- Otherwise → Pass

**For existing positions:**
- Negative signals ≥ 3 → Sell
- Mixed signals → Hold

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Open `.env` file and add your API key
- Ensure no quotes around the key

### "Could not fetch price data"
- Check internet connection
- Verify ticker symbol is valid (use Yahoo Finance format)
- Some stocks may not be available via yfinance

### "Portfolio collection not found"
- The embeddings are created automatically on first run
- Use option 5 (Refresh Embeddings) to rebuild them

### Import errors
- Ensure you're in the virtual environment
- Run `pip install -r requirements.txt` again

## Limitations

- **Data Source**: yfinance is free but may have delays or missing data for some stocks
- **Analysis**: Recommendations are based on quantitative metrics and don't include qualitative factors
- **Not Financial Advice**: This is an educational tool, not professional investment advice
- **Rate Limits**: Anthropic API has rate limits on the free tier
- **RAG Features**: Semantic search (RAG with ChromaDB) requires Python 3.11-3.13; unavailable on Python 3.14+ (system degrades gracefully)

## Future Enhancements

Potential improvements:
- 📱 Web UI (Streamlit/Flask)
- 🔔 Price alerts and notifications
- 📊 Backtesting engine
- 📈 Options analysis
- 💰 Tax-loss harvesting
- 👥 Multi-user support
- 📱 Mobile app
- 🌐 Multiple data sources
- 📧 Email reports

## Technologies Used

- **[Anthropic Claude](https://www.anthropic.com)** - AI agent
- **[yfinance](https://github.com/ranaroussi/yfinance)** - Stock data
- **[ChromaDB](https://www.trychroma.com)** - Vector database
- **[Pydantic](https://docs.pydantic.dev)** - Data validation
- **[Rich](https://rich.readthedocs.io)** - Terminal UI
- **Python 3.13**

## License

This project is for educational purposes. Not financial advice.

## Contributing

This is a learning project, but suggestions are welcome!

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the code comments
3. Check API documentation for Anthropic/yfinance

---

**Disclaimer**: This tool is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with qualified financial advisors before making investment decisions.

Built with ❤️ using Claude AI
