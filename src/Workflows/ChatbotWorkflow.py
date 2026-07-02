from Extractors.TermMatcher import normalize_term, select_confident_matches
from Savers.QdrantSaver import search_similar_terms


def resolve_query_terms(intent: dict) -> dict:
    resolved_terms = {}

    for term in intent["terms"]:
        normalized_term = normalize_term(term)
        results = search_similar_terms(normalized_term)

        candidates = [
            {
                "term": result.payload["term"],
                "definition": result.payload.get("definition", ""),
                "score": result.score
            }
            for result in results
        ]

        resolved_terms[term] = select_confident_matches(candidates)

    return resolved_terms
