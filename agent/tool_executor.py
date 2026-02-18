"""
Tool executor that routes tool calls to their implementations
"""
from typing import Dict, Any
import json

from tools.stock_data import (
    get_current_stock_price,
    get_stock_fundamentals,
    get_historical_data,
    get_stock_news
)
from tools.portfolio_tools import (
    get_portfolio_summary_tool,
    get_position_details,
    add_position_tool,
    remove_position_tool
)
from tools.rag_tools import (
    search_portfolio_context,
    get_sector_exposure,
    find_similar_holdings
)
from tools.analysis_tools import (
    analyze_stock_valuation_tool,
    calculate_portfolio_metrics_tool,
    recommend_action_tool
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ToolExecutor:
    """Executes tool calls from Claude"""

    def __init__(self):
        """Initialize tool executor with function mappings"""
        self.tool_map = {
            # Stock data tools
            "get_current_stock_price": get_current_stock_price,
            "get_stock_fundamentals": get_stock_fundamentals,
            "get_historical_data": get_historical_data,
            "get_stock_news": get_stock_news,

            # Portfolio tools
            "get_portfolio_summary": get_portfolio_summary_tool,
            "get_position_details": get_position_details,
            "add_position": add_position_tool,
            "remove_position": remove_position_tool,

            # RAG tools
            "search_portfolio_context": search_portfolio_context,
            "get_sector_exposure": get_sector_exposure,
            "find_similar_holdings": find_similar_holdings,

            # Analysis tools
            "analyze_stock_valuation": analyze_stock_valuation_tool,
            "calculate_portfolio_metrics": calculate_portfolio_metrics_tool,
            "recommend_action": recommend_action_tool,
        }

    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        try:
            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

            if tool_name not in self.tool_map:
                error_msg = f"Unknown tool: {tool_name}"
                logger.error(error_msg)
                return {"error": error_msg}

            # Get the function
            func = self.tool_map[tool_name]

            # Execute the function with unpacked parameters
            result = func(**tool_input)

            logger.info(f"Tool {tool_name} executed successfully")
            return result

        except TypeError as e:
            error_msg = f"Invalid parameters for tool {tool_name}: {e}"
            logger.error(error_msg)
            return {"error": error_msg}

        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {e}"
            logger.error(error_msg)
            return {"error": error_msg}

    def format_result_for_claude(self, result: Dict[str, Any]) -> str:
        """
        Format tool result as a string for Claude

        Args:
            result: Tool execution result

        Returns:
            Formatted string
        """
        try:
            # Convert to JSON string with pretty formatting
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error formatting result: {e}")
            return str(result)

    def execute_batch(self, tool_calls: list) -> list:
        """
        Execute multiple tool calls

        Args:
            tool_calls: List of tool call objects from Claude

        Returns:
            List of results
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_input = tool_call.get("input", {})

            result = self.execute(tool_name, tool_input)
            results.append({
                "tool_name": tool_name,
                "result": result
            })

        return results
