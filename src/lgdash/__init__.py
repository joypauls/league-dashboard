import logging

__version__ = "0.1.0"

# # configure the root logger or a base package logger
# logging.basicConfig(
#     level=logging.INFO, format="| %(asctime)s | %(name)s | %(levelname)s | %(message)s"
# )

# package_logger = logging.getLogger("lgdash")
# package_logger.setLevel(logging.INFO)

# logging.basicConfig(level=logging.DEBUG)

logging.getLogger("lgdash").addHandler(logging.NullHandler())
