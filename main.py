"""
Stock Recommendation Agent - Main CLI Interface
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.markdown import Markdown

from agent.orchestrator import create_agent
from portfolio.manager import PortfolioManager
from rag.embedder import PortfolioEmbedder
from tools.rag_tools import refresh_embeddings
from utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class StockAgentCLI:
    """Command-line interface for Stock Agent"""

    def __init__(self):
        """Initialize CLI"""
        self.agent = None
        self.portfolio_mgr = PortfolioManager()

    def display_banner(self):
        """Display welcome banner"""
        banner = """
[bold cyan]============================================================

        Stock Recommendation Agent

        AI-Powered Investment Analysis & Portfolio
                    Management System

============================================================[/bold cyan]
        """
        console.print(banner)

    def display_menu(self):
        """Display main menu"""
        menu = Table(show_header=False, box=None, padding=(0, 2))
        menu.add_column(style="cyan bold", width=3)
        menu.add_column(style="white")

        menu.add_row("1.", "Chat with Agent (Stock Analysis & Recommendations)")
        menu.add_row("2.", "View Portfolio Summary")
        menu.add_row("3.", "Add Position to Portfolio")
        menu.add_row("4.", "Remove Position from Portfolio")
        menu.add_row("5.", "Refresh Portfolio Embeddings")
        menu.add_row("6.", "About")
        menu.add_row("0.", "Exit")

        console.print("\n")
        console.print(Panel(menu, title="[bold]Main Menu[/bold]", border_style="cyan"))

    def initialize_agent(self):
        """Initialize the agent (lazy loading)"""
        if self.agent is None:
            try:
                with console.status("[bold cyan]Initializing AI agent...", spinner="dots"):
                    self.agent = create_agent()
                console.print("[green][OK][/green] Agent initialized successfully!")
            except ValueError as e:
                console.print(f"[red][X][/red] {str(e)}")
                console.print("\n[yellow]Please set your ANTHROPIC_API_KEY in the .env file.[/yellow]")
                return False
            except Exception as e:
                console.print(f"[red][X][/red] Failed to initialize agent: {e}")
                return False
        return True

    def chat_with_agent(self):
        """Interactive chat with the agent"""
        if not self.initialize_agent():
            return

        console.print("\n[bold cyan]Chat Mode[/bold cyan]")
        console.print("Ask questions about stocks, request analysis, or get recommendations.")
        console.print("Type 'back' to return to main menu, 'clear' to reset conversation.\n")

        while True:
            try:
                user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

                if user_input.lower() in ['back', 'exit', 'quit']:
                    break

                if user_input.lower() == 'clear':
                    self.agent.reset_conversation()
                    console.print("[green][OK][/green] Conversation cleared.")
                    continue

                if not user_input.strip():
                    continue

                # Get agent response
                with console.status("[bold cyan]Analyzing...", spinner="dots"):
                    response = self.agent.run(user_input)

                # Display response
                console.print("\n[bold green]Agent:[/bold green]")
                console.print(Panel(Markdown(response), border_style="green"))
                console.print()

            except KeyboardInterrupt:
                console.print("\n[yellow]Returning to main menu...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    def view_portfolio_summary(self):
        """Display portfolio summary"""
        try:
            self.portfolio_mgr.load_portfolio()
            portfolio = self.portfolio_mgr.portfolio

            if portfolio.total_positions() == 0:
                console.print("\n[yellow]Portfolio is empty.[/yellow]\n")
                return

            # Get portfolio summary with current values
            from tools.portfolio_tools import get_portfolio_summary_tool
            summary = get_portfolio_summary_tool()

            if "error" in summary:
                console.print(f"[red]Error:[/red] {summary['error']}")
                return

            # Display summary table
            table = Table(title="📊 Portfolio Summary", show_lines=True)
            table.add_column("Ticker", style="cyan bold", width=8)
            table.add_column("Shares", justify="right", style="white")
            table.add_column("Avg Cost", justify="right", style="white")
            table.add_column("Current", justify="right", style="white")
            table.add_column("Value", justify="right", style="white")
            table.add_column("Gain/Loss", justify="right", style="white")
            table.add_column("%", justify="right", style="white")

            for pos in summary['positions']:
                gain_loss_str = f"${pos['gain_loss']:,.2f}"
                gain_loss_pct_str = f"{pos['gain_loss_pct']:+.2f}%"

                # Color code gains/losses
                if pos['gain_loss'] >= 0:
                    gain_color = "green"
                else:
                    gain_color = "red"

                table.add_row(
                    pos['ticker'],
                    f"{pos['shares']:.2f}",
                    f"${pos['purchase_price']:.2f}",
                    f"${pos['current_price']:.2f}",
                    f"${pos['current_value']:,.2f}",
                    f"[{gain_color}]{gain_loss_str}[/{gain_color}]",
                    f"[{gain_color}]{gain_loss_pct_str}[/{gain_color}]"
                )

            console.print("\n")
            console.print(table)

            # Display totals
            total_gain_color = "green" if summary['total_gain_loss'] >= 0 else "red"
            console.print(f"\n[bold]Total Portfolio Value:[/bold] ${summary['total_value']:,.2f}")
            console.print(f"[bold]Total Cost Basis:[/bold] ${summary['total_cost']:,.2f}")
            console.print(
                f"[bold]Total Gain/Loss:[/bold] "
                f"[{total_gain_color}]${summary['total_gain_loss']:,.2f} "
                f"({summary['total_gain_loss_pct']:+.2f}%)[/{total_gain_color}]\n"
            )

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    def add_position(self):
        """Add a position to portfolio"""
        try:
            console.print("\n[bold cyan]Add Position[/bold cyan]")

            ticker = Prompt.ask("Stock ticker").upper()
            shares = float(Prompt.ask("Number of shares"))
            price = float(Prompt.ask("Purchase price per share"))
            date = Prompt.ask("Purchase date (YYYY-MM-DD)", default="today")

            if date.lower() == "today":
                date = None

            from tools.portfolio_tools import add_position_tool
            result = add_position_tool(ticker, shares, price, date)

            if result.get("success"):
                console.print(f"\n[green][OK][/green] {result['message']}")
                console.print(f"Total shares: {result['total_shares']:.2f} @ ${result['avg_price']:.2f} avg\n")
            else:
                console.print(f"\n[red][X][/red] {result.get('error', 'Failed to add position')}\n")

        except ValueError as e:
            console.print(f"[red]Invalid input:[/red] {e}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    def remove_position(self):
        """Remove a position from portfolio"""
        try:
            console.print("\n[bold cyan]Remove Position[/bold cyan]")

            ticker = Prompt.ask("Stock ticker").upper()
            remove_all = Confirm.ask("Remove entire position?", default=True)

            shares = None
            if not remove_all:
                shares = float(Prompt.ask("Number of shares to remove"))

            from tools.portfolio_tools import remove_position_tool
            result = remove_position_tool(ticker, shares)

            if result.get("success"):
                console.print(f"\n[green][OK][/green] {result['message']}")
                if not result['fully_removed']:
                    console.print(f"Remaining shares: {result['remaining_shares']:.2f}\n")
            else:
                console.print(f"\n[red][X][/red] {result.get('error', 'Failed to remove position')}\n")

        except ValueError as e:
            console.print(f"[red]Invalid input:[/red] {e}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    def refresh_embeddings_menu(self):
        """Refresh portfolio embeddings"""
        try:
            with console.status("[bold cyan]Refreshing embeddings...", spinner="dots"):
                result = refresh_embeddings()

            if result.get("success"):
                console.print(f"\n[green][OK][/green] {result['message']}\n")
            else:
                console.print(f"\n[red][X][/red] {result.get('message', 'Failed to refresh embeddings')}\n")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    def display_about(self):
        """Display about information"""
        about_text = """
# About Stock Recommendation Agent

An AI-powered stock analysis and portfolio management system built with:

- **Claude AI** (Anthropic) for intelligent recommendations
- **yfinance** for real-time stock data
- **ChromaDB** for semantic portfolio search (RAG)
- **Rich** for beautiful CLI interface

## Features

- 📊 Real-time stock data and fundamentals
- 🤖 AI-powered buy/sell/hold recommendations
- 💼 Portfolio management and tracking
- 🔍 Semantic search over your holdings
- 📈 Comprehensive valuation and risk analysis
- 🎯 Diversification tracking

## Usage Tips

- Ask natural language questions: "Should I buy NVDA?"
- Request portfolio analysis: "How diversified is my portfolio?"
- Compare stocks: "Compare AAPL and MSFT"
- Get sector insights: "What's my tech exposure?"

---
Built with <3 using Claude AI
        """
        console.print("\n")
        console.print(Panel(Markdown(about_text), border_style="cyan"))
        console.print("\n")

    def run(self):
        """Main CLI loop"""
        self.display_banner()

        # Initialize portfolio and embeddings on startup
        try:
            with console.status("[bold cyan]Loading portfolio...", spinner="dots"):
                self.portfolio_mgr.load_portfolio()

                # Try to initialize embeddings if portfolio not empty
                if self.portfolio_mgr.portfolio.total_positions() > 0:
                    try:
                        embedder = PortfolioEmbedder()
                        if embedder.available and embedder.get_collection_count() == 0:
                            console.print("[yellow]Initializing portfolio embeddings...[/yellow]")
                            embedder.embed_portfolio(self.portfolio_mgr.portfolio, include_current_data=False)
                        elif not embedder.available:
                            console.print("[yellow]Note: RAG features unavailable[/yellow]")
                    except Exception as embed_error:
                        console.print(f"[yellow]Note: RAG features unavailable - {embed_error}[/yellow]")

            console.print("[green][OK][/green] Portfolio loaded successfully!")

        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] {e}")

        while True:
            try:
                self.display_menu()
                choice = Prompt.ask("\n[bold cyan]Select option[/bold cyan]", default="1")

                if choice == "1":
                    self.chat_with_agent()
                elif choice == "2":
                    self.view_portfolio_summary()
                elif choice == "3":
                    self.add_position()
                elif choice == "4":
                    self.remove_position()
                elif choice == "5":
                    self.refresh_embeddings_menu()
                elif choice == "6":
                    self.display_about()
                elif choice == "0":
                    console.print("\n[cyan]Thank you for using Stock Recommendation Agent![/cyan]\n")
                    break
                else:
                    console.print("[yellow]Invalid option. Please try again.[/yellow]")

            except KeyboardInterrupt:
                console.print("\n\n[cyan]Goodbye![/cyan]\n")
                break
            except Exception as e:
                console.print(f"[red]Unexpected error:[/red] {e}")
                logger.error(f"Unexpected error in main loop: {e}")


def main():
    """Entry point"""
    try:
        cli = StockAgentCLI()
        cli.run()
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {e}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
