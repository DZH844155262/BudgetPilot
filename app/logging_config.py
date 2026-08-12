import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOG_DIR = PROJECT_ROOT / "logs"

LOG_FILE = LOG_DIR / "budgetpilot.log"


def configure_logging() -> None:
    """配置BudgetPilot统一日志。"""

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    root_logger = logging.getLogger()

    # 避免uvicorn --reload时重复添加Handler
    if getattr(
        root_logger,
        "_budgetpilot_configured",
        False,
    ):
        return

    root_logger.setLevel(
        logging.INFO
    )

    formatter = logging.Formatter(
        (
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )
    )

    # 终端输出
    console_handler = (
        logging.StreamHandler()
    )

    console_handler.setFormatter(
        formatter
    )

    # 文件日志
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )

    file_handler.setFormatter(
        formatter
    )

    root_logger.addHandler(
        console_handler
    )

    root_logger.addHandler(
        file_handler
    )

    root_logger._budgetpilot_configured = True