# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Utils | Logging Utilities

# COMMAND ----------
import logging
from datetime import datetime

def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        ))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def log_pipeline_start(logger, layer: str, table: str):
    logger.info(f"[START] Layer={layer}, Table={table}, Time={datetime.now()}")


def log_pipeline_end(logger, layer: str, table: str, record_count: int):
    logger.info(f"[END] Layer={layer}, Table={table}, Records={record_count}, Time={datetime.now()}")


def log_dq_summary(logger, table: str, total: int, passed: int, failed: int):
    pct = round(passed / total * 100, 2) if total > 0 else 0
    logger.info(
        f"[DQ] Table={table}, Total={total}, Passed={passed} ({pct}%), Failed={failed}"
    )
