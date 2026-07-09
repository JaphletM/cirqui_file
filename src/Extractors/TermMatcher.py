def normalize_term(term: str) -> str:
    return term.lower().strip()


def select_confident_matches(candidates: list[dict], threshold: float = 0.80) -> list[dict]:
    return [candidate for candidate in candidates if candidate["score"] >= threshold]


def intersect_companies(companies_per_term: dict[str, list[str]]) -> list[str]:
    company_lists = list(companies_per_term.values())

    if not company_lists:
        return []

    common_companies = set(company_lists[0])
    for companies in company_lists[1:]:
        common_companies &= set(companies)

    return [company for company in company_lists[0] if company in common_companies]


def find_technologies_for_company(company_name: str, existing_terms: list[dict]) -> list[str]:
    normalized_company = normalize_term(company_name)

    return [
        term_doc["term"]
        for term_doc in existing_terms
        if normalized_company in [normalize_term(c) for c in term_doc.get("companies", [])]
    ]
