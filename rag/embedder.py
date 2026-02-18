"""
Embed portfolio positions into ChromaDB
"""
from typing import List, Dict, Optional

import config
from portfolio.models import Portfolio
from rag.portfolio_processor import positions_to_documents
from rag.chromadb_wrapper import get_chromadb_client, is_available, Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioEmbedder:
    """Manages embedding portfolio positions into ChromaDB"""

    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.available = is_available()

        if not self.available:
            logger.warning("ChromaDB not available - RAG features disabled")
            self.client = None
            self.collection = None
            return

        try:
            self.client = get_chromadb_client(
                path=config.CHROMA_DB_PATH,
                settings=Settings(anonymized_telemetry=False)
            )

            if self.client:
                self.collection = self.client.get_or_create_collection(
                    name=config.CHROMA_COLLECTION_NAME,
                    metadata={"description": "Portfolio stock positions"}
                )
                logger.info(f"Initialized ChromaDB at {config.CHROMA_DB_PATH}")
            else:
                self.available = False
                self.collection = None
                logger.warning("ChromaDB client creation failed - RAG features disabled")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.available = False
            self.client = None
            self.collection = None

    def embed_portfolio(self, portfolio: Portfolio, include_current_data: bool = True) -> bool:
        """
        Embed all positions from portfolio into ChromaDB

        Args:
            portfolio: Portfolio object
            include_current_data: Whether to fetch current stock data

        Returns:
            True if successful
        """
        if not self.available or self.collection is None:
            logger.warning("ChromaDB not available - skipping embedding")
            return False

        try:
            # Clear existing collection if it has documents
            try:
                count = self.collection.count()
                if count > 0:
                    # Get all IDs and delete them
                    all_items = self.collection.get()
                    if all_items and all_items['ids']:
                        self.collection.delete(ids=all_items['ids'])
                        logger.info(f"Cleared {count} existing embeddings")
            except Exception as clear_error:
                logger.warning(f"Could not clear existing embeddings: {clear_error}")

            if portfolio.total_positions() == 0:
                logger.warning("Portfolio is empty, nothing to embed")
                return True

            # Convert positions to documents
            documents_data = positions_to_documents(
                portfolio.positions,
                include_current_data=include_current_data
            )

            if not documents_data:
                logger.warning("No documents created from positions")
                return False

            # Extract data for ChromaDB
            documents = [d["document"] for d in documents_data]
            metadatas = [d["metadata"] for d in documents_data]
            ids = [d["id"] for d in documents_data]

            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Embedded {len(documents)} positions into ChromaDB")
            return True

        except Exception as e:
            logger.error(f"Error embedding portfolio: {e}")
            return False

    def embed_single_position(self, position, include_current_data: bool = True) -> bool:
        """
        Embed or update a single position

        Args:
            position: Position object
            include_current_data: Whether to fetch current stock data

        Returns:
            True if successful
        """
        if not self.available or self.collection is None:
            logger.warning("ChromaDB not available - skipping embedding")
            return False

        try:
            from rag.portfolio_processor import position_to_document

            doc_text = position_to_document(position, include_current_data)

            metadata = {
                "ticker": position.ticker,
                "shares": position.shares,
                "purchase_price": position.purchase_price,
                "purchase_date": position.purchase_date,
            }

            if include_current_data:
                from tools.stock_data import get_stock_fundamentals
                fundamentals = get_stock_fundamentals(position.ticker)
                if "error" not in fundamentals:
                    metadata["sector"] = fundamentals.get("sector", "Unknown")
                    metadata["industry"] = fundamentals.get("industry", "Unknown")

            doc_id = f"pos_{position.ticker}"

            # Check if exists and update or add
            try:
                self.collection.delete(ids=[doc_id])
            except:
                pass  # ID doesn't exist, that's fine

            self.collection.add(
                documents=[doc_text],
                metadatas=[metadata],
                ids=[doc_id]
            )

            logger.info(f"Embedded position for {position.ticker}")
            return True

        except Exception as e:
            logger.error(f"Error embedding position {position.ticker}: {e}")
            return False

    def remove_position(self, ticker: str) -> bool:
        """
        Remove a position from the embeddings

        Args:
            ticker: Stock ticker symbol

        Returns:
            True if successful
        """
        if not self.available or self.collection is None:
            return True  # Return true since there's nothing to remove

        try:
            doc_id = f"pos_{ticker.upper()}"
            self.collection.delete(ids=[doc_id])
            logger.info(f"Removed embedding for {ticker}")
            return True

        except Exception as e:
            logger.error(f"Error removing position {ticker}: {e}")
            return False

    def get_collection_count(self) -> int:
        """Get the number of embedded positions"""
        if not self.available or self.collection is None:
            return 0

        try:
            return self.collection.count()
        except:
            return 0
