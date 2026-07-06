from Extractors.TermMatcher import normalize_term, select_confident_matches, intersect_companies
from Extractors.TermComparator import find_existing_term
from Savers.QdrantSaver import search_similar_terms
from Savers.MongoSaver import load_existing_terms


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


def gather_query_results(intent: dict, resolved_terms: dict) -> dict:
    terms = intent["terms"]

    if intent["intent"] == "definitie":
        definitions = {
            term: resolved_terms[term][0]["definition"]
            for term in terms
            if resolved_terms[term]
        }

        return {
            "intent": intent["intent"],
            "terms": terms,
            "found": bool(definitions),
            "companies_per_term": None,
            "companies_intersection": None,
            "definitions": definitions
        }

    existing_terms = load_existing_terms()
    companies_per_term = {}

    for term in terms:
        if not resolved_terms[term]:
            companies_per_term[term] = []
            continue

        matched_term_name = resolved_terms[term][0]["term"]
        term_doc = find_existing_term(matched_term_name, existing_terms)
        companies_per_term[term] = term_doc.get("companies", []) if term_doc else []

    companies_intersection = intersect_companies(companies_per_term) if len(terms) >= 2 else None
    found = any(companies_per_term[term] for term in terms)

    return {
        "intent": intent["intent"],
        "terms": terms,
        "found": found,
        "companies_per_term": companies_per_term,
        "companies_intersection": companies_intersection,
        "definitions": None
    }
