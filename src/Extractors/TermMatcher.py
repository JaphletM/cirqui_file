def normalize_term(term: str) -> str:
    return term.lower().strip()


def select_confident_matches(candidates: list[dict], threshold: float = 0.80) -> list[dict]:
    return [candidate for candidate in candidates if candidate["score"] >= threshold]
