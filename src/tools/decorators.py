from functools import wraps
from src.tools.logger import Logger

logger = Logger("node_trace")

def log_node(func):
    @wraps(func)
    def wrapper(self, state, *args, **kwargs):
        node_name = func.__name__
        logger.info(f"🟢 Entering node: {node_name}")
        logger.debug(f"State before: {state.__dict__}")

        result = func(self, state, *args, **kwargs)

        logger.debug(f"State after: {state.__dict__}")
        logger.info(f"✅ Exiting node: {node_name}")

        return result  # ✅ Must return WorkflowState!
    return wrapper
