from Extractors.TermMatcher import normalize_term, select_confident_matches


def test_normalize_term_strips_surrounding_whitespace():
    assert normalize_term("  Kubernetes ") == "kubernetes"


def test_normalize_term_lowercases_all_caps():
    assert normalize_term("KUBERNETES") == "kubernetes"


def test_select_confident_matches_includes_candidate_above_threshold():
    candidates = [{"term": "Kubernetes", "definition": "", "score": 0.95}]

    assert select_confident_matches(candidates, threshold=0.80) == candidates


def test_select_confident_matches_excludes_candidate_below_threshold():
    candidates = [{"term": "Kubernetes", "definition": "", "score": 0.50}]

    assert select_confident_matches(candidates, threshold=0.80) == []


def test_select_confident_matches_includes_candidate_at_exact_threshold():
    candidates = [{"term": "Kubernetes", "definition": "", "score": 0.80}]

    assert select_confident_matches(candidates, threshold=0.80) == candidates


def test_select_confident_matches_with_empty_candidates_returns_empty_list():
    assert select_confident_matches([], threshold=0.80) == []
