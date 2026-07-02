import pytest
from Extractors.QueryIntentExtractor import validate_intent

def test_unknown_intent_raises():
    with pytest.raises(ValueError):
        validate_intent({"intent": "onzin", "terms": ["Kubernetes"]})

def test_missing_terms_key_raises():
    with pytest.raises(ValueError):
        validate_intent({"intent": "bedrijven"})    

def test_empty_terms_list_raises():
    with pytest.raises(ValueError):
        validate_intent({"intent": "bedrijven", "terms": []})   

def test_terms_with_empty_string_raises():
    with pytest.raises(ValueError):
        validate_intent({"intent": "bedrijven", "terms": [""]}) 

def test_valid_intent_with_single_term():
    result = validate_intent({"intent": "bedrijven", "terms": ["Kubernetes"]})
    assert result == {"intent": "bedrijven", "terms": ["Kubernetes"]}

def test_valid_intent_with_multiple_terms():
    result = validate_intent({"intent": "definitie", "terms": ["Kubernetes", "Java", "Linux"]})
    assert result == {"intent": "definitie", "terms": ["Kubernetes", "Java", "Linux"]}

def test_valid_intent_with_multiple_terms_no_cardinality_limit():
    result = validate_intent({"intent": "definitie", "terms": ["Kubernetes", "Java", "Linux", "Python"]})
    assert result == {"intent": "definitie", "terms": ["Kubernetes", "Java", "Linux", "Python"]}

def test_terms_with_non_string_raises():
    with pytest.raises(ValueError):
        validate_intent({"intent": "bedrijven", "terms": ["Kubernetes", 123]})  


        


# #- geldige input (`bedrijven`, 1 term) → correcte `QueryIntent`-dict
#- geldige input (`bedrijven`, 3 termen) → correcte `QueryIntent`-dict
#  (meerdere termen zijn toegestaan, geen aparte intent nodig)
#- geldige input (`definitie`, 1 term) → correcte `QueryIntent`-dict
#- geldige input (`definitie`, 3 termen, bijv. Kubernetes/Java/Linux) →
#  correcte `QueryIntent`-dict (geen cardinaliteitsgrens meer)
#- ontbrekende `terms`-key → `ValueError` met "terms" in de boodschap
#- lege `terms`-lijst → raises `ValueError`
##- `terms` bevat een lege string → raises `ValueError`
#- onbekende `intent`-waarde → `ValueError` met "intent" in de boodschap
#- `extract_query_intent` met LLM-mock die niet-JSON teruggeeft →
#  `ValueError`, geen stille lege default 
