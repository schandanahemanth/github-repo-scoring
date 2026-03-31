from __future__ import annotations

import logging

LOGGER_NAME = "github_repo_scoring_service"


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    )

    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = configure_logging()
