import logging
from typing import Dict, List, Tuple, Optional, Any

from .knowledge_base import KnowledgeBase
from .ontology_engine import OntologyEngine, VALIDATION_CATEGORIES
from .semantic_matcher import SemanticMatcher

logger = logging.getLogger(__name__)


class EntityClassifier:
    """
    Multiclass Entity Classifier classifying extracted resume strings into
    one of 16 Validation Categories using Knowledge Base lookup, Ontology rules,
    and Semantic Similarity.
    """

    def __init__(self):
        self.kb = KnowledgeBase()

    def classify_entity(self, value: str, context_section: str = "") -> Dict[str, Any]:
        """
        Classifies value into one of 16 VALIDATION_CATEGORIES.
        Returns top_category, score, category_scores, and rationale.
        """
        if not value or not str(value).strip():
            return {
                "top_category": "UNKNOWN",
                "confidence_score": 0.0,
                "category_scores": {cat: 0.0 for cat in VALIDATION_CATEGORIES},
                "explanation": "Empty or whitespace entity value"
            }

        val_clean = str(value).strip()
        cat_scores: Dict[str, float] = {cat: 0.0 for cat in VALIDATION_CATEGORIES}
        explanations: Dict[str, str] = {}

        # 1. Direct Knowledge Base Exact Lookup
        exact_cat = self.kb.get_category_by_entity(val_clean)
        if exact_cat:
            cat_scores[exact_cat] = 98.0
            explanations[exact_cat] = f"Exact match in Knowledge Base ontology for {exact_cat}"

        # 2. Specialized Ontology Rule Evaluation
        # PERSON
        is_person, p_score, p_reason = OntologyEngine.validate_person_name(val_clean)
        if is_person and cat_scores["PERSON"] < p_score:
            cat_scores["PERSON"] = p_score
            explanations["PERSON"] = p_reason
        elif not is_person:
            cat_scores["PERSON"] = p_score
            explanations["PERSON"] = p_reason

        # UNIVERSITY
        is_univ, u_score, u_reason = OntologyEngine.validate_university(val_clean)
        if is_univ and cat_scores["UNIVERSITY"] < u_score:
            cat_scores["UNIVERSITY"] = u_score
            explanations["UNIVERSITY"] = u_reason

        # COMPANY
        is_comp, c_score, c_reason = OntologyEngine.validate_company(val_clean)
        if is_comp and cat_scores["COMPANY"] < c_score:
            cat_scores["COMPANY"] = c_score
            explanations["COMPANY"] = c_reason

        # CERTIFICATE
        is_cert, cert_score, cert_reason = OntologyEngine.validate_certificate(val_clean)
        if is_cert and cat_scores["CERTIFICATE"] < cert_score:
            cat_scores["CERTIFICATE"] = cert_score
            explanations["CERTIFICATE"] = cert_reason

        # DATE
        is_date, d_score, d_reason = OntologyEngine.validate_date(val_clean)
        if is_date and cat_scores["DATE"] < d_score:
            cat_scores["DATE"] = d_score
            explanations["DATE"] = d_reason

        # LANGUAGE
        is_lang, l_score, l_reason = OntologyEngine.validate_language(val_clean)
        if is_lang and cat_scores["LANGUAGE"] < l_score:
            cat_scores["LANGUAGE"] = l_score
            explanations["LANGUAGE"] = l_reason

        # DESIGNATION / ROLE
        is_desig, des_score, des_reason = OntologyEngine.validate_designation(val_clean)
        if is_desig and cat_scores["DESIGNATION"] < des_score:
            cat_scores["DESIGNATION"] = des_score
            explanations["DESIGNATION"] = des_reason
            if cat_scores["ROLE"] < des_score:
                cat_scores["ROLE"] = des_score
                explanations["ROLE"] = des_reason

        # COUNTRY / CITY
        is_country, count_score, count_reason = OntologyEngine.validate_country(val_clean)
        if is_country and cat_scores["COUNTRY"] < count_score:
            cat_scores["COUNTRY"] = count_score
            explanations["COUNTRY"] = count_reason

        is_city, city_score, city_reason = OntologyEngine.validate_city(val_clean)
        if is_city and cat_scores["CITY"] < city_score:
            cat_scores["CITY"] = city_score
            explanations["CITY"] = city_reason

        # PUBLICATION / AWARD
        is_pub, pub_score, pub_reason = OntologyEngine.validate_publication(val_clean)
        if is_pub and cat_scores["PUBLICATION"] < pub_score:
            cat_scores["PUBLICATION"] = pub_score
            explanations["PUBLICATION"] = pub_reason

        is_award, aw_score, aw_reason = OntologyEngine.validate_award(val_clean)
        if is_award and cat_scores["AWARD"] < aw_score:
            cat_scores["AWARD"] = aw_score
            explanations["AWARD"] = aw_reason

        # 3. Knowledge Base Keyword & Similarity Fallback Matching
        for category in VALIDATION_CATEGORIES:
            if cat_scores[category] >= 90.0:
                continue

            entities = self.kb.get_entities(category)
            keywords = self.kb.get_keywords(category)

            if entities or keywords:
                match_score = SemanticMatcher.match_against_category(val_clean, entities, keywords)
                if match_score > cat_scores[category]:
                    cat_scores[category] = match_score
                    explanations[category] = f"Semantic matcher score {match_score:.1f}% for category {category}"

        # Determine top category candidate
        top_cat = max(cat_scores, key=cat_scores.get)
        top_score = cat_scores[top_cat]

        # If top score is too low, fallback to SKILL / PROJECT / PERSON depending on context
        if top_score < 40.0:
            if context_section in ["skills", "skill"]:
                top_cat = "SKILL"
                top_score = 60.0
                explanations[top_cat] = "Fallback classification based on skills section context"
            elif context_section in ["education"]:
                top_cat = "UNIVERSITY"
                top_score = 60.0
                explanations[top_cat] = "Fallback classification based on education section context"

        return {
            "top_category": top_cat,
            "confidence_score": round(top_score, 1),
            "category_scores": {k: round(v, 1) for k, v in cat_scores.items()},
            "explanation": explanations.get(top_cat, f"Classified as {top_cat}")
        }
