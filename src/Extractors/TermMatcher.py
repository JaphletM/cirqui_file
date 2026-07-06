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
