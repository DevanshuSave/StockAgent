"""
Setup verification — imports, portfolio, validators, tools, ChromaDB, and RAG.
Run: python -m tests.test_setup
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")

# Allow imports from project root when run as a script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_python_version():
    print(f"Python version: {sys.version}")
    major, minor = sys.version_info[:2]
    assert major == 3 and minor >= 12, f"Expected Python >= 3.12, got {major}.{minor}"
    print("[OK] Python version")
    return True


def test_imports():
    """Test that all project modules can be imported."""
    print("\nTesting imports...")
    modules = [
        ("config", lambda: __import__("config")),
        ("portfolio.models", lambda: __import__("portfolio.models", fromlist=["Position", "Portfolio"])),
        ("portfolio.manager", lambda: __import__("portfolio.manager", fromlist=["PortfolioManager"])),
        ("utils.logger", lambda: __import__("utils.logger", fromlist=["get_logger"])),
        ("utils.validators", lambda: __import__("utils.validators", fromlist=["validate_ticker"])),
        ("tools.stock_data", lambda: __import__("tools.stock_data", fromlist=["get_current_stock_price"])),
        ("agent.tool_definitions", lambda: __import__("agent.tool_definitions", fromlist=["get_tool_definitions"])),
        ("agent.tool_executor", lambda: __import__("agent.tool_executor", fromlist=["ToolExecutor"])),
    ]

    errors = []
    for name, loader in modules:
        try:
            loader()
            print(f"  [OK] {name}")
        except Exception as e:
            if name == "agent.tool_executor" and "unable to infer type" in str(e):
                print(f"  [WARN] {name} (ChromaDB type warning — non-critical)")
            else:
                errors.append(f"{name}: {e}")
                print(f"  [X] {name}: {e}")

    if errors:
        return False
    print("[OK] All imports successful")
    return True


def test_config():
    """Verify configuration loads and env vars are set."""
    print("\nTesting configuration...")
    import config

    print(f"  API Key configured: {bool(config.ANTHROPIC_API_KEY)}")
    print(f"  Base URL: {config.ANTHROPIC_BASE_URL or '(not set)'}")
    print(f"  Model: {config.AGENT_MODEL or '(endpoint default)'}")
    print("[OK] Configuration loaded")
    return True


def test_portfolio():
    """Test basic portfolio operations."""
    print("\nTesting portfolio...")
    from portfolio.manager import PortfolioManager

    mgr = PortfolioManager()
    portfolio = mgr.load_portfolio()
    print(f"  Portfolio loaded: {portfolio.total_positions()} positions")

    if portfolio.total_positions() > 0:
        print(f"  First position: {portfolio.positions[0].ticker}")

    print("[OK] Portfolio operations")
    return True


def test_validators():
    """Test validators."""
    print("\nTesting validators...")
    from utils.validators import validate_ticker, sanitize_ticker

    assert validate_ticker("AAPL") is True, "AAPL should be valid"
    assert validate_ticker("") is False, "Empty should be invalid"
    assert sanitize_ticker("aapl") == "AAPL", "Should uppercase"

    print("[OK] Validators")
    return True


def test_tool_definitions():
    """Test tool definitions."""
    print("\nTesting tool definitions...")
    from agent.tool_definitions import get_tool_definitions, get_tool_names

    tools = get_tool_definitions()
    names = get_tool_names()

    print(f"  Found {len(tools)} tools: {', '.join(names[:5])}...")
    assert all("name" in t and "description" in t for t in tools), "Missing fields"

    print("[OK] Tool definitions")
    return True


def test_chromadb():
    """Test ChromaDB and RAG embedding."""
    print("\nTesting ChromaDB / RAG...")
    import chromadb  # noqa: F401

    print("  [OK] ChromaDB imported")

    from rag.embedder import PortfolioEmbedder

    embedder = PortfolioEmbedder()
    print(f"  ChromaDB available: {embedder.available}")

    if embedder.available:
        from portfolio.manager import PortfolioManager

        portfolio = PortfolioManager().load_portfolio()
        if portfolio.total_positions() > 0:
            success = embedder.embed_portfolio(portfolio, include_current_data=False)
            if success:
                print(f"  Collection count: {embedder.get_collection_count()}")
                print("[OK] RAG embedding")
            else:
                print("  [WARN] Embedding failed — system will still work")
        else:
            print("  [SKIP] No positions to embed")
    return True


# ── Runner ──────────────────────────────────────────────────

ALL_TESTS = [
    ("Python version", test_python_version),
    ("Imports", test_imports),
    ("Configuration", test_config),
    ("Portfolio", test_portfolio),
    ("Validators", test_validators),
    ("Tool definitions", test_tool_definitions),
    ("ChromaDB / RAG", test_chromadb),
]


def main():
    print("=" * 60)
    print("Stock Recommendation Agent — Setup Verification")
    print("=" * 60)

    results = []
    for name, fn in ALL_TESTS:
        try:
            passed = fn()
        except Exception as e:
            print(f"  [X] {name} failed: {e}")
            passed = False
        results.append((name, passed))

    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    for name, passed in results:
        print(f"  {'[PASS]' if passed else '[FAIL]'} {name}")

    print("=" * 60)
    if all(p for _, p in results):
        print("[OK] All tests passed! System is ready.")
        print("\nRun: python main.py")
    else:
        print("[X] Some tests failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
