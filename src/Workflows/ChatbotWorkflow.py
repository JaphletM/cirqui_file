from Extractors.AnswerComposer import compose_answer
from Extractors.TermMatcher import select_confident_matches, intersect_companies, find_technologies_for_company
from Extractors.TermComparator import find_existing_term
from Savers.QdrantSaver import search_similar_terms
from Savers.MongoSaver import load_existing_terms
from Extractors.QueryIntentExtractor import extract_query_intent


def run_chatbot_query(request: dict, llm_client) -> str:
    prompt_templates = request["prompt_templates"]

    intent_request = {"question": request["question"], "prompt_template": prompt_templates["intent"]}
    intent = extract_query_intent(intent_request, llm_client)

    query_results = gather_results_for_intent(intent)

    answer_request = {"result": query_results, "prompt_template": prompt_templates["answer"]}
    return compose_answer(answer_request, llm_client)


def gather_results_for_intent(intent: dict) -> dict:
    if intent["intent"] == "technologieen":
        return gather_technologies_for_companies(intent)

    resolved_terms = resolve_query_terms(intent)
    return gather_query_results(intent, resolved_terms)


def resolve_query_terms(intent: dict) -> dict:
    existing_terms = load_existing_terms()
    resolved_terms = {}

    for term in intent["terms"]:
        resolved_terms[term] = resolve_single_term(term, existing_terms)

    return resolved_terms


def resolve_single_term(term: str, existing_terms: list) -> list:
    exact_match = find_existing_term(term, existing_terms)

    if not exact_match:
        candidates = search_qdrant_candidates(term)
        return select_confident_matches(candidates)

    return [{
        "term": exact_match["term"],
        "definition": exact_match.get("definition", ""),
        "score": 1.0
    }]


def search_qdrant_candidates(term: str) -> list:
    queries = {term, term.capitalize()}
    candidates_by_term = {}

    for query in queries:
        results = search_similar_terms(query)
        merge_candidates(candidates_by_term, results)

    return list(candidates_by_term.values())


def merge_candidates(candidates_by_term: dict, results: list) -> None:
    for result in results:
        candidate = {
            "term": result.payload["term"],
            "definition": result.payload.get("definition", ""),
            "score": result.score
        }
        keep_highest_scoring(candidates_by_term, candidate)


def keep_highest_scoring(candidates_by_term: dict, candidate: dict) -> None:
    matched_term = candidate["term"]
    existing = candidates_by_term.get(matched_term)

    if not existing or candidate["score"] > existing["score"]:
        candidates_by_term[matched_term] = candidate


def gather_query_results(intent: dict, resolved_terms: dict) -> dict:
    if intent["intent"] == "definitie":
        return gather_definitions(intent, resolved_terms)

    return gather_companies(intent, resolved_terms)


def gather_definitions(intent: dict, resolved_terms: dict) -> dict:
    terms = intent["terms"]
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
        "definitions": definitions,
        "technologies_per_company": None
    }


def gather_companies(intent: dict, resolved_terms: dict) -> dict:
    terms = intent["terms"]
    existing_terms = load_existing_terms()
    companies_per_term = {
        term: find_companies_for_resolved_term(resolved_terms[term], existing_terms)
        for term in terms
    }

    companies_intersection = intersect_companies(companies_per_term) if len(terms) >= 2 else None
    found = any(companies_per_term[term] for term in terms)

    return {
        "intent": intent["intent"],
        "terms": terms,
        "found": found,
        "companies_per_term": companies_per_term,
        "companies_intersection": companies_intersection,
        "definitions": None,
        "technologies_per_company": None
    }


def find_companies_for_resolved_term(matches: list, existing_terms: list) -> list:
    if not matches:
        return []

    matched_term_name = matches[0]["term"]
    term_doc = find_existing_term(matched_term_name, existing_terms)

    if not term_doc:
        return []

    return term_doc.get("companies", [])


def gather_technologies_for_companies(intent: dict) -> dict:
    companies = intent["terms"]
    existing_terms = load_existing_terms()
    technologies_per_company = {
        company: find_technologies_for_company(company, existing_terms)
        for company in companies
    }

    found = any(technologies_per_company[company] for company in companies)

    return {
        "intent": intent["intent"],
        "terms": companies,
        "found": found,
        "companies_per_term": None,
        "companies_intersection": None,
        "definitions": None,
        "technologies_per_company": technologies_per_company
    }
