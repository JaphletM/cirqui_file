from unittest.mock import MagicMock

from Extractors.AnswerComposer import compose_answer, build_answer_context


def test_compose_answer_returns_fixed_message_without_calling_llm_when_not_found():
    result = {
        "intent": "bedrijven",
        "terms": ["Foo"],
        "found": False,
        "companies_per_term": None,
        "companies_intersection": None,
        "definitions": None
    }
    llm_client = MagicMock()

    answer = compose_answer(result, llm_client, prompt_template="irrelevant")

    assert answer == "Geen informatie gevonden over: Foo."
    llm_client.ask.assert_not_called()

def test_build_answer_context_translates_keys_correctly():
        result = {
            "found": True,
            "terms": ["Foo", "Bar"],
            "companies_per_term": {"Foo": ["Company1"], "Bar": ["Company2"]},
            "companies_intersection": ["Company1"],
            "definitions": {"Foo": "Definition of Foo", "Bar": "Definition of Bar"}
        }

        context = build_answer_context(result)

        assert context == {
            "gevonden": True,
            "termen": ["Foo", "Bar"],
            "bedrijven_per_term": {"Foo": ["Company1"], "Bar": ["Company2"]},
            "bedrijven_intersectie": ["Company1"],
            "definities": {"Foo": "Definition of Foo", "Bar": "Definition of Bar"}
        }

def test_compose_answer_calls_llm_with_filled_prompt_when_found():
    result = {
        "intent": "bedrijven",
        "terms": ["Foo", "Bar"],
        "found": True,
        "companies_per_term": {"Foo": ["Company1"], "Bar": ["Company2"]},
        "companies_intersection": ["Company1"],
        "definitions": {"Foo": "Definition of Foo", "Bar": "Definition of Bar"}
    }
    llm_client = MagicMock()
    llm_client.ask.return_value = "LLM response"
    prompt_template = (
        "Gevonden: {GEVONDEN}\n"
        "Termen: {TERMEN}\n"
        "Bedrijven per term: {BEDRIJVEN_PER_TERM}\n"
        "Bedrijven intersectie: {BEDRIJVEN_INTERSECTIE}\n"
        "Definities: {DEFINITIES}"
    )   
    assert compose_answer(result, llm_client, prompt_template) == "LLM response"


