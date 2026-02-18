"""
Semantic search and retrieval over portfolio embeddings
"""
from typing import List, Dict, Any, Optional

import config
from rag.chromadb_wrapper import get_chromadb_client, is_available, Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioRetriever:
    """Performs semantic search over embedded portfolio positions"""

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
                try:
                    self.collection = self.client.get_collection(name=config.CHROMA_COLLECTION_NAME)
                    logger.info("Connected to portfolio embeddings collection")
                except:
                    logger.warning("Portfolio collection not found, may need to embed first")
                    self.collection = None
            else:
                self.available = False
                self.collection = None

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB retriever: {e}")
            self.available = False
            self.client = None
            self.collection = None

    def search(self, query: str, n_results: int = None) -> Dict[str, Any]:
        """
        Perform semantic search over portfolio

        Args:
            query: Search query (e.g., "tech stocks", "high growth")
            n_results: Number of results to return

        Returns:
            Dict with relevant positions and context
        """
        if not self.available:
            return {
                "error": "RAG features not available (ChromaDB compatibility issue with Python 3.14)",
                "relevant_positions": [],
                "context_summary": "Please use Python 3.11 or 3.12 for RAG features"
            }

        try:
            if self.collection is None:
                return {
                    "error": "Portfolio not embedded yet",
                    "relevant_positions": [],
                    "context_summary": "No data available"
                }

            if n_results is None:
                n_results = config.RAG_TOP_K_RESULTS

            # Perform query
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )

            if not results['documents'] or not results['documents'][0]:
                return {
                    "query": query,
                    "relevant_positions": [],
                    "context_summary": "No matching positions found"
                }

            # Extract and format results
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]

            relevant_positions = []
            for doc, metadata, distance in zip(documents, metadatas, distances):
                relevant_positions.append({
                    "ticker": metadata['ticker'],
                    "shares": metadata['shares'],
                    "purchase_price": metadata['purchase_price'],
                    "purchase_date": metadata['purchase_date'],
                    "sector": metadata.get('sector', 'Unknown'),
                    "industry": metadata.get('industry', 'Unknown'),
                    "relevance_score": round(1 - distance, 3),  # Convert distance to similarity
                    "summary": doc[:200] + "..." if len(doc) > 200 else doc
                })

            # Create context summary
            tickers = [p['ticker'] for p in relevant_positions]
            sectors = list(set([p['sector'] for p in relevant_positions if p['sector'] != 'Unknown']))

            context_summary = f"Found {len(relevant_positions)} relevant position(s): {', '.join(tickers)}."
            if sectors:
                context_summary += f" Sectors: {', '.join(sectors)}."

            result = {
                "query": query,
                "relevant_positions": relevant_positions,
                "context_summary": context_summary,
                "total_results": len(relevant_positions)
            }

            logger.info(f"Search for '{query}' returned {len(relevant_positions)} results")
            return result

        except Exception as e:
            logger.error(f"Error during search: {e}")
            return {
                "error": str(e),
                "relevant_positions": [],
                "context_summary": "Error during search"
            }

    def get_by_sector(self, sector: str) -> Dict[str, Any]:
        """
        Get all positions in a specific sector

        Args:
            sector: Sector name (e.g., "Technology", "Healthcare")

        Returns:
            Dict with positions in that sector
        """
        if not self.available:
            return {"error": "RAG features not available", "positions": []}

        try:
            if self.collection is None:
                return {"error": "Portfolio not embedded yet", "positions": []}

            # Query with sector filter
            results = self.collection.get(
                where={"sector": sector},
                include=["documents", "metadatas"]
            )

            if not results['metadatas']:
                return {
                    "sector": sector,
                    "positions": [],
                    "total_positions": 0,
                    "message": f"No positions found in {sector}"
                }

            positions = []
            for metadata, doc in zip(results['metadatas'], results['documents']):
                positions.append({
                    "ticker": metadata['ticker'],
                    "shares": metadata['shares'],
                    "purchase_price": metadata['purchase_price'],
                    "sector": metadata.get('sector', 'Unknown'),
                    "industry": metadata.get('industry', 'Unknown')
                })

            return {
                "sector": sector,
                "positions": positions,
                "total_positions": len(positions)
            }

        except Exception as e:
            logger.error(f"Error getting sector {sector}: {e}")
            return {"error": str(e), "positions": []}

    def find_similar_to_ticker(self, ticker: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Find positions similar to a given ticker

        Args:
            ticker: Stock ticker to find similar positions to
            n_results: Number of similar positions to return

        Returns:
            Dict with similar positions
        """
        if not self.available:
            return {"error": "RAG features not available", "similar_positions": []}

        try:
            if self.collection is None:
                return {"error": "Portfolio not embedded yet", "similar_positions": []}

            ticker = ticker.upper()

            # Get the document for the target ticker
            doc_id = f"pos_{ticker}"
            target_doc = self.collection.get(
                ids=[doc_id],
                include=["documents"]
            )

            if not target_doc['documents']:
                # Ticker not in portfolio, search by ticker name
                return self.search(f"similar to {ticker}", n_results=n_results)

            # Use the document text as query to find similar
            query_text = target_doc['documents'][0]
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results + 1  # +1 because it will include itself
            )

            # Filter out the target ticker itself
            similar_positions = []
            for metadata, doc, distance in zip(
                results['metadatas'][0],
                results['documents'][0],
                results['distances'][0]
            ):
                if metadata['ticker'] != ticker:
                    similar_positions.append({
                        "ticker": metadata['ticker'],
                        "sector": metadata.get('sector', 'Unknown'),
                        "industry": metadata.get('industry', 'Unknown'),
                        "similarity_score": round(1 - distance, 3)
                    })

            return {
                "target_ticker": ticker,
                "similar_positions": similar_positions[:n_results],
                "total_found": len(similar_positions)
            }

        except Exception as e:
            logger.error(f"Error finding similar to {ticker}: {e}")
            return {"error": str(e), "similar_positions": []}
