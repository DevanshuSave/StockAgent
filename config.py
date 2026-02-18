"""
Configuration file for Stock Recommendation Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Configuration
# Support both standard API key and custom auth token setups
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")  # Optional custom endpoint

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_PATH = DATA_DIR / "chroma_db"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DB_PATH.mkdir(exist_ok=True)

# Agent settings
# Model name - if empty, will use endpoint's default
AGENT_MODEL = os.getenv("ANTHROPIC_MODEL", "") or None  # None means use default
MAX_AGENT_ITERATIONS = 10

# Stock data settings
DEFAULT_HISTORICAL_PERIOD = "1y"  # 1 year
CACHE_TIMEOUT_SECONDS = 300  # 5 minutes

# RAG settings
CHROMA_COLLECTION_NAME = "portfolio_positions"
RAG_TOP_K_RESULTS = 5
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Analysis thresholds
OVERVALUED_PE_THRESHOLD = 30
HIGH_SECTOR_CONCENTRATION_PCT = 40
MIN_DIVERSIFICATION_STOCKS = 10

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
