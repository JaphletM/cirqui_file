import pytest
from Extractors.QueryIntentExtractor import validate_intent

def test_unknown_intent_raises():
    with pytest.raises(ValueError):
        validate_intent({"intent": "onzin", "terms": ["Kubernetes"]})