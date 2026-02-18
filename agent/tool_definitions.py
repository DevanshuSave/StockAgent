"""
Tool definitions for Anthropic Claude function calling
"""

TOOL_DEFINITIONS = [
    # Stock Data Tools
    {
        "name": "get_current_stock_price",
        "description": "Fetches the current stock price, volume, market cap, and daily change percentage for a given ticker symbol. Use this to get real-time stock data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_stock_fundamentals",
        "description": "Fetches fundamental data for a stock including P/E ratio, EPS, dividend yield, sector, industry, market cap, and growth metrics. Essential for valuation analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_historical_data",
        "description": "Fetches historical price data for a stock over a specified period. Returns dates, prices, returns, and summary statistics. Useful for analyzing trends and momentum.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "period": {
                    "type": "string",
                    "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                    "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_stock_news",
        "description": "Fetches recent news articles about a stock. Provides news titles, publishers, and links.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },

    # Portfolio Tools
    {
        "name": "get_portfolio_summary",
        "description": "Gets a complete summary of the user's portfolio including total value, total gain/loss, and details for each position (shares, current value, gain/loss %). Use this to understand the full portfolio state.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_position_details",
        "description": "Gets detailed information about a specific position in the portfolio including shares owned, purchase price, current value, and gain/loss.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "add_position",
        "description": "Adds a new position to the portfolio or updates an existing one. If the position already exists, this will average the cost basis. Automatically updates embeddings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "shares": {
                    "type": "number",
                    "description": "Number of shares to add (must be positive)"
                },
                "price": {
                    "type": "number",
                    "description": "Purchase price per share"
                },
                "date": {
                    "type": "string",
                    "description": "Purchase date in YYYY-MM-DD format (optional, defaults to today)"
                }
            },
            "required": ["ticker", "shares", "price"]
        }
    },
    {
        "name": "remove_position",
        "description": "Removes shares from a position or the entire position from the portfolio. If shares parameter is omitted or equals/exceeds total shares, removes the entire position. Automatically updates embeddings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "shares": {
                    "type": "number",
                    "description": "Number of shares to remove (optional, omit to remove entire position)"
                }
            },
            "required": ["ticker"]
        }
    },

    # RAG Tools
    {
        "name": "search_portfolio_context",
        "description": "Performs semantic search over the portfolio using natural language queries. Use this to find relevant positions (e.g., 'tech stocks', 'high growth companies', 'dividend stocks'). Returns relevant positions with summaries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query"
                },
                "n_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_sector_exposure",
        "description": "Gets all positions in a specific sector and calculates the portfolio's exposure to that sector as a percentage of total value. Useful for analyzing sector concentration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {
                    "type": "string",
                    "description": "Sector name (e.g., Technology, Healthcare, Financials, Energy, Consumer Cyclical)"
                }
            },
            "required": ["sector"]
        }
    },
    {
        "name": "find_similar_holdings",
        "description": "Finds portfolio positions that are similar to a given ticker based on sector, industry, and company characteristics. Useful for identifying potential overlap or correlation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol to find similar holdings for"
                },
                "n_results": {
                    "type": "integer",
                    "description": "Number of similar positions to return (default 3)"
                }
            },
            "required": ["ticker"]
        }
    },

    # Analysis Tools
    {
        "name": "analyze_stock_valuation",
        "description": "Analyzes a stock's valuation metrics including P/E ratio, profitability, and debt levels. Determines if the stock is overvalued, fairly valued, or undervalued. Use this before making buy recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_portfolio_metrics",
        "description": "Calculates comprehensive portfolio metrics including diversification score (0-100), sector allocation, and concentration risks. Use this to understand portfolio health and balance.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "recommend_action",
        "description": "Generates a buy/sell/hold/pass recommendation for a stock based on comprehensive analysis of valuation, growth, risk, and portfolio context. Returns action, confidence level, and detailed reasoning. This is the primary tool for making investment recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "context": {
                    "type": "object",
                    "description": "Optional context from previous analysis or user query"
                }
            },
            "required": ["ticker"]
        }
    }
]


def get_tool_definitions():
    """Returns the list of tool definitions for Claude API"""
    return TOOL_DEFINITIONS


def get_tool_names():
    """Returns a list of all tool names"""
    return [tool["name"] for tool in TOOL_DEFINITIONS]
