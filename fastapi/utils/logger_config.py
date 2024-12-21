import logging
from logging import Logger

# Color codes
COLORS = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "ENDC": "\033[0m",  # Reset
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        # Store the original levelname
        levelname = record.levelname

        if levelname in COLORS:
            # Format the levelname with color
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['ENDC']}"
            # Format the message with the same color
            record.msg = f"{COLORS[levelname]}{record.msg}{COLORS['ENDC']}"

        return super().format(record)


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create console handler with color formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = ColorFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
