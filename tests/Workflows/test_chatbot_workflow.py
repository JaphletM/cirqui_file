from types import SimpleNamespace
from unittest.mock import patch

from Workflows.ChatbotWorkflow import resolve_query_terms, gather_query_results, gather_technologies_for_companies


def test_resolve_query_terms_returns_exact_match_without_calling_qdrant():
    intent = {"intent": "definitie", "terms": ["Java"]}
    existing_terms = [{"term": "Java", "definition": "programmeertaal"}]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms") as mocked_search:
        resolved = resolve_query_terms(intent)

    mocked_search.assert_not_called()
    assert resolved == {"Java": [{"term": "Java", "definition": "programmeertaal", "score": 1.0}]}


def test_resolve_query_terms_exact_match_is_case_insensitive():
    intent = {"intent": "definitie", "terms": ["java"]}
    existing_terms = [{"term": "Java", "definition": "programmeertaal"}]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms") as mocked_search:
        resolved = resolve_query_terms(intent)

    mocked_search.assert_not_called()
    assert resolved == {"java": [{"term": "Java", "definition": "programmeertaal", "score": 1.0}]}


def test_resolve_query_terms_returns_confident_matches_per_term():
    intent = {"intent": "definitie", "terms": ["Kubernetes"]}
    fake_results = [
        SimpleNamespace(payload={"term": "Kubernetes", "definition": "container orchestration"}, score=0.95)
    ]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms", return_value=fake_results) as mocked_search:
        resolved = resolve_query_terms(intent)

    mocked_search.assert_called_once_with("Kubernetes")
    assert resolved == {
        "Kubernetes": [{"term": "Kubernetes", "definition": "container orchestration", "score": 0.95}]
    }


def test_resolve_query_terms_finds_match_when_user_types_lowercase():
    intent = {"intent": "definitie", "terms": ["docker"]}

    def fake_search(query, *args, **kwargs):
        if query == "Docker":
            return [SimpleNamespace(payload={"term": "Docker", "definition": "container platform"}, score=0.81)]
        return [SimpleNamespace(payload={"term": "Docker", "definition": "container platform"}, score=0.57)]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms", side_effect=fake_search) as mocked_search:
        resolved = resolve_query_terms(intent)

    assert mocked_search.call_count == 2
    mocked_search.assert_any_call("docker")
    mocked_search.assert_any_call("Docker")
    assert resolved["docker"] == [{"term": "Docker", "definition": "container platform", "score": 0.81}]


def test_resolve_query_terms_does_not_search_twice_when_already_capitalized():
    intent = {"intent": "definitie", "terms": ["Kubernetes"]}
    fake_results = [
        SimpleNamespace(payload={"term": "Kubernetes", "definition": "container orchestration"}, score=0.95)
    ]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms", return_value=fake_results) as mocked_search:
        resolve_query_terms(intent)

    assert mocked_search.call_count == 1


def test_resolve_query_terms_keeps_highest_score_when_both_queries_match():
    intent = {"intent": "definitie", "terms": ["docker"]}

    def fake_search(query, *args, **kwargs):
        score = 0.60 if query == "docker" else 0.90
        return [SimpleNamespace(payload={"term": "Docker", "definition": "container platform"}, score=score)]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms", side_effect=fake_search):
        resolved = resolve_query_terms(intent)

    assert resolved["docker"] == [{"term": "Docker", "definition": "container platform", "score": 0.90}]


def test_resolve_query_terms_returns_empty_list_for_term_without_confident_match():
    intent = {"intent": "definitie", "terms": ["Foo"]}
    fake_results = [
        SimpleNamespace(payload={"term": "Foo", "definition": "onduidelijk"}, score=0.40)
    ]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms", return_value=fake_results):
        resolved = resolve_query_terms(intent)

    assert resolved == {"Foo": []}


def test_resolve_query_terms_handles_multiple_terms_independently():
    intent = {"intent": "bedrijven", "terms": ["Kubernetes", "Java"]}
    fake_results_by_query = {
        "Kubernetes": [SimpleNamespace(payload={"term": "Kubernetes", "definition": ""}, score=0.90)],
        "Java": [SimpleNamespace(payload={"term": "Java", "definition": ""}, score=0.30)],
    }

    def fake_search(query, *args, **kwargs):
        return fake_results_by_query[query]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]), \
         patch("Workflows.ChatbotWorkflow.search_similar_terms", side_effect=fake_search):
        resolved = resolve_query_terms(intent)

    assert resolved["Kubernetes"] == [{"term": "Kubernetes", "definition": "", "score": 0.90}]
    assert resolved["Java"] == []


def test_gather_query_results_definitie_returns_definitions_for_confirmed_terms_only():
    intent = {"intent": "definitie", "terms": ["Kubernetes", "Java", "Linux"]}
    resolved_terms = {
        "Kubernetes": [{"term": "Kubernetes", "definition": "container orchestration", "score": 0.95}],
        "Java": [{"term": "Java", "definition": "programmeertaal", "score": 0.90}],
        "Linux": []
    }

    result = gather_query_results(intent, resolved_terms)

    assert result["definitions"] == {
        "Kubernetes": "container orchestration",
        "Java": "programmeertaal"
    }
    assert result["found"] is True
    assert result["companies_per_term"] is None
    assert result["companies_intersection"] is None


def test_gather_query_results_definitie_returns_not_found_when_nothing_confirmed():
    intent = {"intent": "definitie", "terms": ["Foo"]}
    resolved_terms = {"Foo": []}

    result = gather_query_results(intent, resolved_terms)

    assert result["definitions"] == {}
    assert result["found"] is False


def test_gather_query_results_bedrijven_calls_load_existing_terms_exactly_once():
    intent = {"intent": "bedrijven", "terms": ["Kubernetes", "Java"]}
    resolved_terms = {
        "Kubernetes": [{"term": "Kubernetes", "definition": "", "score": 0.95}],
        "Java": [{"term": "Java", "definition": "", "score": 0.95}]
    }
    existing_terms = [
        {"term": "Kubernetes", "companies": ["Google", "ASML"]},
        {"term": "Java", "companies": ["Google", "Booking"]}
    ]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms) as mocked_load:
        gather_query_results(intent, resolved_terms)

    mocked_load.assert_called_once()


def test_gather_query_results_bedrijven_missing_companies_key_treated_as_empty():
    intent = {"intent": "bedrijven", "terms": ["Kubernetes"]}
    resolved_terms = {"Kubernetes": [{"term": "Kubernetes", "definition": "", "score": 0.95}]}
    existing_terms = [{"term": "Kubernetes"}]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms):
        result = gather_query_results(intent, resolved_terms)

    assert result["companies_per_term"]["Kubernetes"] == []
    assert result["found"] is False


def test_gather_query_results_bedrijven_single_term_without_confirmed_match():
    intent = {"intent": "bedrijven", "terms": ["Foo"]}
    resolved_terms = {"Foo": []}

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]):
        result = gather_query_results(intent, resolved_terms)

    assert result["found"] is False
    assert result["companies_intersection"] is None
    assert result["companies_per_term"] == {"Foo": []}


def test_gather_query_results_bedrijven_three_terms_returns_intersection():
    intent = {"intent": "bedrijven", "terms": ["Kubernetes", "Java", "Linux"]}
    resolved_terms = {
        "Kubernetes": [{"term": "Kubernetes", "definition": "", "score": 0.95}],
        "Java": [{"term": "Java", "definition": "", "score": 0.95}],
        "Linux": [{"term": "Linux", "definition": "", "score": 0.95}]
    }
    existing_terms = [
        {"term": "Kubernetes", "companies": ["Google", "ASML"]},
        {"term": "Java", "companies": ["Google", "Booking"]},
        {"term": "Linux", "companies": ["Google", "ASML", "Booking"]}
    ]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms):
        result = gather_query_results(intent, resolved_terms)

    assert result["companies_per_term"] == {
        "Kubernetes": ["Google", "ASML"],
        "Java": ["Google", "Booking"],
        "Linux": ["Google", "ASML", "Booking"]
    }
    assert result["companies_intersection"] == ["Google"]
    assert result["found"] is True


def test_gather_query_results_bedrijven_partial_match_still_found():
    intent = {"intent": "bedrijven", "terms": ["Kubernetes", "Foo"]}
    resolved_terms = {
        "Kubernetes": [{"term": "Kubernetes", "definition": "", "score": 0.95}],
        "Foo": []
    }
    existing_terms = [{"term": "Kubernetes", "companies": ["Google", "ASML"]}]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms):
        result = gather_query_results(intent, resolved_terms)

    assert result["found"] is True
    assert result["companies_per_term"]["Foo"] == []
    assert result["companies_intersection"] == []


def test_gather_query_results_bedrijven_no_match_at_all():
    intent = {"intent": "bedrijven", "terms": ["Foo"]}
    resolved_terms = {"Foo": []}

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]):
        result = gather_query_results(intent, resolved_terms)

    assert result["found"] is False


def test_gather_technologies_for_companies_returns_matching_technologies():
    intent = {"intent": "technologieen", "terms": ["Google"]}
    existing_terms = [
        {"term": "Docker", "companies": ["Google", "ASML"]},
        {"term": "Kubernetes", "companies": ["Google"]},
        {"term": "Java", "companies": ["Booking"]}
    ]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms):
        result = gather_technologies_for_companies(intent)

    assert result["technologies_per_company"] == {"Google": ["Docker", "Kubernetes"]}
    assert result["found"] is True
    assert result["companies_per_term"] is None
    assert result["definitions"] is None


def test_gather_technologies_for_companies_returns_not_found_when_no_match():
    intent = {"intent": "technologieen", "terms": ["OnbekendBedrijf"]}

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=[]):
        result = gather_technologies_for_companies(intent)

    assert result["found"] is False
    assert result["technologies_per_company"] == {"OnbekendBedrijf": []}


def test_gather_technologies_for_companies_partial_match_still_found():
    intent = {"intent": "technologieen", "terms": ["Google", "OnbekendBedrijf"]}
    existing_terms = [{"term": "Docker", "companies": ["Google"]}]

    with patch("Workflows.ChatbotWorkflow.load_existing_terms", return_value=existing_terms):
        result = gather_technologies_for_companies(intent)

    assert result["found"] is True
    assert result["technologies_per_company"]["OnbekendBedrijf"] == []
