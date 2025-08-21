import logging
import sys
from datetime import datetime
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install
from rich.theme import Theme
from rich.text import Text
from rich.panel import Panel
from typing import Any, Dict

# Install rich traceback
install()

# Custom theme for rich
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "critical": "bold white on red",
    "success": "bold green",
    "debug": "dim blue",
    "orchestrator": "bold magenta",
    "rag": "bold blue",
    "user": "bold cyan",
    "system": "bold white"
})

console = Console(theme=custom_theme)

class CustomFormatter(logging.Formatter):
    """Custom formatter for file logging"""

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] [{record.levelname}] [{record.name}] {record.getMessage()}"

class Logger:
    def __init__(self, name: str = "RAG_Multi_Strategy"):
        self.logger = logging.getLogger(name)
        self.console = console
        self._setup_logger()

    def _setup_logger(self):
        """Setup logger with both file and rich console handlers"""
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler
        log_file = log_dir / f"rag_system_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(CustomFormatter())

        # Rich console handler
        rich_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        rich_handler.setLevel(logging.INFO)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(rich_handler)

    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message"""
        self.logger.info(message, extra=extra)

    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra)

    def error(self, message: str, extra: Dict[str, Any] = None):
        """Log error message"""
        self.logger.error(message, extra=extra)

    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra)

    def critical(self, message: str, extra: Dict[str, Any] = None):
        """Log critical message"""
        self.logger.critical(message, extra=extra)

    def success(self, message: str):
        """Log success message with green color"""
        self.console.print(f"✅ {message}", style="success")
        self.logger.info(f"SUCCESS: {message}")

    def step(self, step_name: str, description: str = ""):
        """Log a process step with visual separation"""
        text = Text()
        text.append("🚀 ", style="bold yellow")
        text.append(f"STEP: {step_name}", style="bold white")
        if description:
            text.append(f" - {description}", style="dim white")

        panel = Panel(text, border_style="blue", padding=(0, 1))
        self.console.print(panel)
        self.logger.info(f"STEP: {step_name} - {description}")

    def orchestrator_log(self, message: str, component: str = "Main"):
        """Special log for orchestrator components"""
        self.console.print(f"🎭 [{component} Orchestrator] {message}", style="orchestrator")
        self.logger.info(f"ORCHESTRATOR [{component}]: {message}")

    def rag_log(self, message: str, strategy: str = ""):
        """Special log for RAG operations"""
        strategy_text = f"[{strategy}] " if strategy else ""
        self.console.print(f"🔍 {strategy_text}{message}", style="rag")
        self.logger.info(f"RAG {strategy_text}: {message}")

    def user_interaction(self, message: str):
        """Log user interactions"""
        self.console.print(f"👤 USER: {message}", style="user")
        self.logger.info(f"USER INTERACTION: {message}")

    def system_response(self, message: str):
        """Log system responses"""
        self.console.print(f"🤖 SYSTEM: {message}", style="system")
        self.logger.info(f"SYSTEM RESPONSE: {message}")

    def separator(self, title: str = ""):
        """Print a visual separator"""
        if title:
            self.console.rule(f"[bold blue]{title}[/bold blue]")
        else:
            self.console.rule()

    def progress_start(self, message: str):
        """Start a progress indication"""
        self.console.print(f"⏳ {message}...", style="info")
        self.logger.info(f"PROGRESS START: {message}")

    def progress_end(self, message: str):
        """End a progress indication"""
        self.console.print(f"✨ {message}", style="success")
        self.logger.info(f"PROGRESS END: {message}")

# Global logger instance
logger = Logger()

def get_logger(name: str = None) -> Logger:
    """Get logger instance"""
    if name:
        return Logger(name)
    return logger
