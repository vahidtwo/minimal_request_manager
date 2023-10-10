import asyncio
import logging

from request_manager.log import logger
from request_manager.cli import cli

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    asyncio.run(cli())
