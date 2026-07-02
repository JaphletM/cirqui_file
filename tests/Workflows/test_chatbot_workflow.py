from types import SimpleNamespace
from unittest.mock import patch

from Workflows.ChatbotWorkflow import resolve_query_terms


def test_resolve_query_terms_returns_confident_matches_per_term():
    intent = {"intent": "definitie", "terms": ["Kubernetes"]}
    fake_results = [
        SimpleNamespace(payload={"term": "Kubernetes", "definition": "container orchestration"}, score=0.95)
    ]

    with patch("Workflows.ChatbotWorkflow.search_similar_terms", return_value=fake_results) as mocked_search:
        resolved = resolve_query_terms(intent)

    mocked_search.assert_called_once_with("kubernetes")
    assert resolved == {
        "Kubernetes": [{"term": "Kubernetes", "definition": "container orchestration", "score": 0.95}]
    }


def test_resolve_query_terms_returns_empty_list_for_term_without_confident_match():
    intent = {"intent": "definitie", "terms": ["Foo"]}
    fake_results = [
        SimpleNamespace(payload={"term": "Foo", "definition": "onduidelijk"}, score=0.40)
    ]

    with patch("Workflows.ChatbotWorkflow.search_similar_terms", return_value=fake_results):
        resolved = resolve_query_terms(intent)

    assert resolved == {"Foo": []}


def test_resolve_query_terms_handles_multiple_terms_independently():
    intent = {"intent": "bedrijven", "terms": ["Kubernetes", "Java"]}
    fake_results_by_query = {
        "kubernetes": [SimpleNamespace(payload={"term": "Kubernetes", "definition": ""}, score=0.90)],
        "java": [SimpleNamespace(payload={"term": "Java", "definition": ""}, score=0.30)],
    }

    def fake_search(query, *args, **kwargs):
        return fake_results_by_query[query]

    with patch("Workflows.ChatbotWorkflow.search_similar_terms", side_effect=fake_search):
        resolved = resolve_query_terms(intent)

    assert resolved["Kubernetes"] == [{"term": "Kubernetes", "definition": "", "score": 0.90}]
    assert resolved["Java"] == []
