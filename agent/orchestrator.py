"""
Main agent orchestrator for Claude API integration
"""
import anthropic
from typing import List, Dict, Any, Optional
import json

import config
from agent.tool_definitions import get_tool_definitions
from agent.tool_executor import ToolExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class StockAgent:
    """Main agent for stock recommendation system"""

    def __init__(self):
        """Initialize the agent"""
        if not config.ANTHROPIC_API_KEY or config.ANTHROPIC_API_KEY == "your_api_key_here":
            raise ValueError(
                "ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not set in .env file. "
                "Please add your API credentials to the .env file."
            )

        # Initialize client with optional base_url for custom endpoints
        client_kwargs = {"api_key": config.ANTHROPIC_API_KEY}
        if config.ANTHROPIC_BASE_URL:
            client_kwargs["base_url"] = config.ANTHROPIC_BASE_URL
            logger.info(f"Using custom Anthropic endpoint: {config.ANTHROPIC_BASE_URL}")

        self.client = anthropic.Anthropic(**client_kwargs)
        self.tool_executor = ToolExecutor()
        self.conversation_history = []
        self.system_prompt = self._create_system_prompt()

        logger.info("Stock Agent initialized")

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent"""
        # Check if RAG is available
        from rag.chromadb_wrapper import is_available as rag_available

        rag_note = ""
        if not rag_available():
            rag_note = "\n\nNOTE: RAG features (search_portfolio_context, get_sector_exposure, find_similar_holdings) are currently unavailable due to ChromaDB compatibility. Use get_portfolio_summary and analyze sectors manually."

        return f"""You are an expert stock recommendation agent with access to real-time market data,
portfolio analysis tools, and comprehensive financial analysis capabilities.

Your responsibilities:
1. Provide investment recommendations (buy/sell/hold) based on thorough analysis
2. Analyze stock fundamentals, valuation, growth, and risk factors
3. Consider the user's existing portfolio and diversification when making recommendations
4. Use available tools to find relevant portfolio context
5. Explain your reasoning clearly and concisely

Guidelines:
- Always fetch current data using the tools before making recommendations
- Consider portfolio context (sector exposure, diversification, existing positions)
- Provide specific, actionable recommendations with confidence levels
- Explain the key factors behind your recommendations
- When analyzing a stock, typically use: get_current_stock_price, get_stock_fundamentals,
  and recommend_action tools at minimum
- Be concise but thorough in your analysis

Available tools:
- Stock data: get_current_stock_price, get_stock_fundamentals, get_historical_data, get_stock_news
- Portfolio: get_portfolio_summary, get_position_details, add_position, remove_position
- RAG: search_portfolio_context, get_sector_exposure, find_similar_holdings (if available)
- Analysis: analyze_stock_valuation, calculate_portfolio_metrics, recommend_action{rag_note}

Remember: You are helping users make informed investment decisions. Be thorough but decisive."""

    def run(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response

        Args:
            user_message: User's input message

        Returns:
            Agent's response string
        """
        try:
            logger.info(f"Processing user message: {user_message[:100]}...")

            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Agent loop
            iteration = 0
            max_iterations = config.MAX_AGENT_ITERATIONS

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Agent iteration {iteration}/{max_iterations}")

                # Call Claude API
                # Build API call parameters
                api_params = {
                    "max_tokens": 4096,
                    "system": self.system_prompt,
                    "tools": get_tool_definitions(),
                    "messages": self.conversation_history
                }

                # Only add model if one is specified, otherwise use endpoint default
                if config.AGENT_MODEL:
                    api_params["model"] = config.AGENT_MODEL
                    logger.info(f"Using model: {config.AGENT_MODEL}")
                else:
                    logger.info("No model specified - using endpoint's default")
                    # Don't include model parameter at all
                    pass

                response = self.client.messages.create(**api_params)

                logger.info(f"Received response with stop_reason: {response.stop_reason}")

                # Process response
                if response.stop_reason == "tool_use":
                    # Extract tool calls and text
                    assistant_content = []
                    tool_calls = []

                    for block in response.content:
                        if block.type == "text":
                            assistant_content.append({
                                "type": "text",
                                "text": block.text
                            })
                        elif block.type == "tool_use":
                            tool_calls.append(block)
                            assistant_content.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            })

                    # Add assistant message to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_content
                    })

                    # Execute tools
                    logger.info(f"Executing {len(tool_calls)} tool(s)")
                    tool_results = []

                    for tool_call in tool_calls:
                        logger.info(f"Tool: {tool_call.name}")
                        result = self.tool_executor.execute(tool_call.name, tool_call.input)
                        result_str = self.tool_executor.format_result_for_claude(result)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_call.id,
                            "content": result_str
                        })

                    # Add tool results to history
                    self.conversation_history.append({
                        "role": "user",
                        "content": tool_results
                    })

                    # Continue loop to get next response
                    continue

                elif response.stop_reason == "end_turn":
                    # Extract final response text
                    response_text = ""
                    for block in response.content:
                        if block.type == "text":
                            response_text += block.text

                    # Add to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    logger.info("Agent completed successfully")
                    return response_text

                else:
                    logger.warning(f"Unexpected stop_reason: {response.stop_reason}")
                    return "I encountered an unexpected issue. Please try again."

            # Max iterations reached
            logger.warning("Max iterations reached")
            return "I've reached the maximum number of analysis steps. Please try rephrasing your question or breaking it into smaller requests."

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return f"API Error: {str(e)}"

        except Exception as e:
            logger.error(f"Error in agent run: {e}")
            return f"Error: {str(e)}"

    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return {
            "message_count": len(self.conversation_history),
            "messages": self.conversation_history
        }


def create_agent() -> StockAgent:
    """Factory function to create a new agent instance"""
    return StockAgent()
