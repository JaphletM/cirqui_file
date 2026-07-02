from Extractors.TermComparator import find_existing_term


def test_find_existing_term_matches_case_insensitively():
    existing_terms = [{"term": "Kubernetes", "definition": "container orchestration"}]

    match = find_existing_term("KUBERNETES", existing_terms)

    assert match == existing_terms[0]


def test_find_existing_term_matches_with_surrounding_whitespace():
    existing_terms = [{"term": "Kubernetes", "definition": "container orchestration"}]

    match = find_existing_term("  kubernetes  ", existing_terms)

    assert match == existing_terms[0]


def test_find_existing_term_returns_none_when_no_match():
    existing_terms = [{"term": "Kubernetes", "definition": "container orchestration"}]

    match = find_existing_term("Docker", existing_terms)

    assert match is None
