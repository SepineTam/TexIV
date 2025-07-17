"""Rich utilities for enhanced terminal output."""

from typing import Optional, Any
import logging
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    TaskID,
)
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.logging import RichHandler
import time


class RichHelper:
    """Helper class for rich terminal output."""
    
    def __init__(self, quiet: bool = False):
        """Initialize RichHelper.
        
        Args:
            quiet: If True, suppress all output except errors
        """
        self.console = Console(quiet=quiet)
        self.quiet = quiet
    
    def print_success(self, message: str) -> None:
        """Print success message."""
        if not self.quiet:
            self.console.print(f"✅ {message}", style="green")
    
    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"❌ {message}", style="bold red")
    
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        if not self.quiet:
            self.console.print(f"⚠️  {message}", style="yellow")
    
    def print_info(self, message: str) -> None:
        """Print info message."""
        if not self.quiet:
            self.console.print(f"ℹ️  {message}", style="blue")
    
    def create_progress(self, description: str = "Processing") -> Progress:
        """Create a progress bar with custom columns.
        
        Args:
            description: Description shown in progress bar
            
        Returns:
            Progress instance ready for use as context manager
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=self.console,
            disable=self.quiet,
        )
        
        return progress
    
    def display_results_table(self, title: str, data: dict[str, Any]) -> None:
        """Display results in a formatted table.
        
        Args:
            title: Table title
            data: Dictionary of results to display
        """
        if self.quiet:
            return
            
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white")
        
        for key, value in data.items():
            table.add_row(str(key), str(value))
        
        self.console.print(table)
    
    def display_status_panel(self, title: str, content: dict[str, Any]) -> None:
        """Display status information in a panel.
        
        Args:
            title: Panel title
            content: Dictionary of status information
        """
        if self.quiet:
            return
            
        text_content = "\n".join([f"{k}: {v}" for k, v in content.items()])
        panel = Panel(
            text_content,
            title=title,
            title_align="left",
            border_style="blue"
        )
        self.console.print(panel)

    def setup_logging(self, level: int = logging.INFO) -> None:
        """Setup rich formatted logging.
        
        Args:
            level: Logging level to use
        """
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)]
        )


def create_rich_helper(quiet: bool = False) -> RichHelper:
    """Factory function to create RichHelper instance.
    
    Args:
        quiet: Whether to suppress non-error output
        
    Returns:
        RichHelper instance
    """
    return RichHelper(quiet=quiet)