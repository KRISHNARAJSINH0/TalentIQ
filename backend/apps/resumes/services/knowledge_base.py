import json
import os
import logging
from typing import Dict, List, Set, Tuple, Optional

logger = logging.getLogger(__name__)

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "semantic_kb")


class KnowledgeBase:
    """
    Singleton Knowledge Base service managing semantic ontologies and category dictionaries.
    Loads and caches entity dictionaries for 16 validation categories.
    """

    _instance: Optional["KnowledgeBase"] = None

    def __new__(cls) -> "KnowledgeBase":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.category_entities: Dict[str, Set[str]] = {}
        self.category_keywords: Dict[str, List[str]] = {}
        self.category_patterns: Dict[str, List[str]] = {}
        self.entity_to_category: Dict[str, str] = {}

        self._load_knowledge_base()
        self._initialized = True

    def _load_knowledge_base(self):
        """Loads all JSON files from semantic_kb directory into cached memory structures."""
        if not os.path.exists(KB_DIR):
            logger.warning(f"KnowledgeBase directory {KB_DIR} does not exist. Creating empty KB.")
            os.makedirs(KB_DIR, exist_ok=True)
            return

        for filename in os.listdir(KB_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(KB_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    category = data.get("category", "").upper()
                    if not category:
                        continue

                    entities = data.get("entities", [])
                    keywords = data.get("keywords", [])
                    patterns = data.get("patterns", [])

                    if category not in self.category_entities:
                        self.category_entities[category] = set()
                    if category not in self.category_keywords:
                        self.category_keywords[category] = []
                    if category not in self.category_patterns:
                        self.category_patterns[category] = []

                    for ent in entities:
                        clean_ent = str(ent).strip()
                        self.category_entities[category].add(clean_ent.lower())
                        # Store exact reverse mapping for case-insensitive lookup
                        self.entity_to_category[clean_ent.lower()] = category

                    self.category_keywords[category].extend([str(k).strip() for k in keywords])
                    self.category_patterns[category].extend([str(p).strip() for p in patterns])

                    logger.debug(f"Loaded {len(entities)} entities for category {category} from {filename}")
                except Exception as e:
                    logger.error(f"Error loading KnowledgeBase file {filepath}: {e}")

    def is_exact_entity(self, category: str, value: str) -> bool:
        """Checks if exact string value exists under a specified category."""
        if not value:
            return False
        cat_upper = category.upper()
        clean_val = value.strip().lower()
        return clean_val in self.category_entities.get(cat_upper, set())

    def get_category_by_entity(self, value: str) -> Optional[str]:
        """Returns category name if value is an exact entity match in KB."""
        if not value:
            return None
        return self.entity_to_category.get(value.strip().lower())

    def contains_keyword(self, category: str, value: str) -> bool:
        """Checks if string value contains any keywords defined for a category."""
        if not value:
            return False
        cat_upper = category.upper()
        keywords = self.category_keywords.get(cat_upper, [])
        val_lower = value.strip().lower()

        for kw in keywords:
            kw_lower = kw.lower()
            # Boundary or substring match
            if kw_lower in val_lower:
                return True
        return False

    def contains_pattern(self, category: str, value: str) -> bool:
        """Checks if string value matches any suffix/pattern defined for a category."""
        if not value:
            return False
        cat_upper = category.upper()
        patterns = self.category_patterns.get(cat_upper, [])
        val_lower = value.strip().lower()

        for pat in patterns:
            pat_lower = pat.lower()
            if pat_lower in val_lower:
                return True
        return False

    def get_entities(self, category: str) -> List[str]:
        """Returns all entity strings for a given category."""
        cat_upper = category.upper()
        return list(self.category_entities.get(cat_upper, set()))

    def get_keywords(self, category: str) -> List[str]:
        """Returns all keywords for a given category."""
        cat_upper = category.upper()
        return self.category_keywords.get(cat_upper, [])

    def reload(self):
        """Forces reload of all JSON files."""
        self.category_entities.clear()
        self.category_keywords.clear()
        self.category_patterns.clear()
        self.entity_to_category.clear()
        self._load_knowledge_base()
