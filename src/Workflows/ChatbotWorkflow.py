from Extractors.AnswerComposer import compose_answer
from Extractors.TermMatcher import select_confident_matches, intersect_companies, find_technologies_for_company
from Extractors.TermComparator import find_existing_term
from Savers.QdrantSaver import search_similar_terms
from Savers.MongoSaver import load_existing_terms
from Extractors.QueryIntentExtractor import extract_query_intent


def run_chatbot_query(question: str, llm_client, prompt_template_intent: str, prompt_template_answer: str) -> str:
    intent = extract_query_intent(question, llm_client, prompt_template_intent)

    if intent["intent"] == "technologieen":
        query_results = gather_technologies_for_companies(intent)
    else:
        resolved_terms = resolve_query_terms(intent)
        query_results = gather_query_results(intent, resolved_terms)

    answer = compose_answer(query_results, llm_client, prompt_template_answer)
    return answer



def resolve_query_terms(intent: dict) -> dict:
    existing_terms = load_existing_terms()
    resolved_terms = {}

    for term in intent["terms"]:
        exact_match = find_existing_term(term, existing_terms)

        if exact_match:
            resolved_terms[term] = [{
                "term": exact_match["term"],
                "definition": exact_match.get("definition", ""),
                "score": 1.0
            }]
            continue

        queries = {term, term.capitalize()}

        candidates_by_term = {}
        for query in queries:
            for result in search_similar_terms(query):
                matched_term = result.payload["term"]

                if matched_term not in candidates_by_term or result.score > candidates_by_term[matched_term]["score"]:
                    candidates_by_term[matched_term] = {
                        "term": matched_term,
                        "definition": result.payload.get("definition", ""),
                        "score": result.score
                    }

        resolved_terms[term] = select_confident_matches(list(candidates_by_term.values()))

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
            "definitions": definitions,
            "technologies_per_company": None
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
        "definitions": None,
        "technologies_per_company": None
    }


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
