from Extractors.TermMatcher import normalize_term, select_confident_matches, intersect_companies


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


def test_intersect_companies_with_userstory_example():
    companies_per_term = {
        "Kubernetes": ["Google", "ASML"],
        "Java": ["Google", "Booking"],
        "Linux": ["Google", "ASML", "Booking"]
    }

    assert intersect_companies(companies_per_term) == ["Google"]


def test_intersect_companies_with_empty_dict_returns_empty_list():
    assert intersect_companies({}) == []


def test_intersect_companies_with_one_term_having_empty_list_returns_empty_list():
    companies_per_term = {"Kubernetes": ["Google", "ASML"], "Foo": []}

    assert intersect_companies(companies_per_term) == []


def test_intersect_companies_with_single_term_returns_it_unchanged():
    companies_per_term = {"Kubernetes": ["Google", "ASML"]}

    assert intersect_companies(companies_per_term) == ["Google", "ASML"]
