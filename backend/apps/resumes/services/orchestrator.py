import logging
from typing import Dict, List, Any, Optional, Callable

from .pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Coordinates execution of all parsing stages with retries and fallbacks.
    """

    def __init__(self):
        self.pipeline_manager = PipelineManager()

    def execute_with_retry(
        self,
        func: Callable[[], Any],
        max_retries: int = 3,
        fallback_func: Optional[Callable[[], Any]] = None
    ) -> Any:
        attempts = 0
        while attempts < max_retries:
            try:
                return func()
            except Exception as e:
                attempts += 1
                logger.warning(f"Orchestrator execution attempt {attempts} failed: {str(e)}")
                if attempts >= max_retries:
                    if fallback_func:
                        logger.info("Executing fallback strategy...")
                        return fallback_func()
                    raise e
