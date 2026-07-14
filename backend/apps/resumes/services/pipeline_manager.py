import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

STAGES = [
    "upload",
    "extract_text",
    "section_detection",
    "regex_extraction",
    "spacy_extraction",
    "gemini_parsing",
    "confidence_engine",
    "semantic_validation",
    "error_detection",
    "ai_recovery",
    "consistency_checking",
    "source_tracking",
    "master_builder"
]


class PipelineManager:
    """
    Manages pipeline execution state, step tracking, and status logging.
    """

    def __init__(self):
        self.stage_statuses: Dict[str, str] = {s: "pending" for s in STAGES}
        self.execution_logs: List[Dict[str, Any]] = []

    def start_stage(self, stage_name: str):
        if stage_name in self.stage_statuses:
            self.stage_statuses[stage_name] = "in_progress"
            self._log(stage_name, "started")

    def complete_stage(self, stage_name: str, status_val: str = "completed", details: Optional[Dict[str, Any]] = None):
        if stage_name in self.stage_statuses:
            self.stage_statuses[stage_name] = status_val
            self._log(stage_name, status_val, details)

    def _log(self, stage: str, status_val: str, details: Optional[Dict[str, Any]] = None):
        log_entry = {
            "stage": stage,
            "status": status_val,
            "details": details or {}
        }
        self.execution_logs.append(log_entry)
        logger.info(f"Pipeline Stage [{stage}]: {status_val}")

    def get_pipeline_summary(self) -> Dict[str, Any]:
        completed_count = sum(1 for s in self.stage_statuses.values() if s == "completed")
        progress = round((completed_count / len(STAGES)) * 100.0, 1)

        return {
            "progress_percent": progress,
            "stage_statuses": self.stage_statuses,
            "logs": self.execution_logs
        }
