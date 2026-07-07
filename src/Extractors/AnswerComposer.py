def build_answer_context(result: dict) -> dict:
    """
    Vertaalt de QueryResult-dict (keys: found, terms, companies_per_term,
    companies_intersection, definitions) naar de Nederlandse vorm die de
    antwoord-prompt gebruikt.
    """
    return {
        "gevonden": result.get("found"),
        "termen": result.get("terms", []),
        "bedrijven_per_term": result.get("companies_per_term"),
        "bedrijven_intersectie": result.get("companies_intersection"),
        "definities": result.get("definitions")
    }


def compose_answer(result: dict, llm_client, prompt_template: str) -> str:
    if result.get("found") is False:
        return f"Geen informatie gevonden over: {', '.join(result.get('terms', []))}."

    context = build_answer_context(result)

    filled_prompt = (
        prompt_template
        .replace("{GEVONDEN}", str(context["gevonden"]))
        .replace("{TERMEN}", ", ".join(context["termen"]))
        .replace("{BEDRIJVEN_PER_TERM}", str(context["bedrijven_per_term"]))
        .replace("{BEDRIJVEN_INTERSECTIE}", str(context["bedrijven_intersectie"]))
        .replace("{DEFINITIES}", str(context["definities"]))
    )

    return llm_client.ask(filled_prompt)
