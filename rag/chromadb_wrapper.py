"""
Wrapper for ChromaDB to handle Python 3.14 compatibility issues
"""
import sys
import warnings

# Flag to track if ChromaDB is available
CHROMADB_AVAILABLE = False
chromadb = None

try:
    # Suppress the pydantic v1 warning
    warnings.filterwarnings('ignore', category=UserWarning, module='chromadb.config')

    # Try to import ChromaDB
    import chromadb as _chromadb
    from chromadb.config import Settings

    chromadb = _chromadb
    CHROMADB_AVAILABLE = True

except Exception as e:
    # ChromaDB not available - will use fallback mode
    CHROMADB_AVAILABLE = False
    print(f"[WARNING] ChromaDB not available: {e}")
    print("[WARNING] RAG features will be disabled. System will work with limited semantic search.")

    # Create mock objects
    class MockSettings:
        def __init__(self, **kwargs):
            pass

    Settings = MockSettings


def get_chromadb_client(path, settings=None):
    """
    Get ChromaDB client or return None if unavailable

    Args:
        path: Path to ChromaDB database
        settings: ChromaDB settings

    Returns:
        ChromaDB client or None
    """
    if not CHROMADB_AVAILABLE:
        return None

    try:
        if chromadb:
            return chromadb.PersistentClient(path=str(path), settings=settings)
    except Exception as e:
        print(f"[WARNING] Failed to create ChromaDB client: {e}")
        return None


def is_available():
    """Check if ChromaDB is available"""
    return CHROMADB_AVAILABLE
