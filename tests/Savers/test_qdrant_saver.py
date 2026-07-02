from types import SimpleNamespace
from unittest.mock import patch

from Savers.QdrantSaver import find_existing_term


def test_find_existing_term_returns_payload_when_score_above_threshold():
    fake_results = [
        SimpleNamespace(payload={"term": "Kubernetes", "definition": "container orchestration"}, score=0.95)
    ]

    with patch("Savers.QdrantSaver.search_similar_terms", return_value=fake_results):
        match = find_existing_term("Kubernetes", "container orchestration")

    assert match == {"term": "Kubernetes", "definition": "container orchestration"}


def test_find_existing_term_returns_none_when_score_below_threshold():
    fake_results = [
        SimpleNamespace(payload={"term": "Kubernetes", "definition": "container orchestration"}, score=0.50)
    ]

    with patch("Savers.QdrantSaver.search_similar_terms", return_value=fake_results):
        match = find_existing_term("Kubernetes", "container orchestration")

    assert match is None


def test_find_existing_term_returns_none_when_no_results():
    with patch("Savers.QdrantSaver.search_similar_terms", return_value=[]):
        match = find_existing_term("Kubernetes", "container orchestration")

    assert match is None
