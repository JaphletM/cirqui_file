def build_answer_context(result: dict) -> dict:
    """
    Vertaalt de QueryResult-dict (keys: found, terms, companies_per_term,
    companies_intersection, definitions, technologies_per_company) naar
    de Nederlandse vorm die de antwoord-prompt gebruikt.
    """
    return {
        "gevonden": result.get("found"),
        "termen": result.get("terms", []),
        "bedrijven_per_term": result.get("companies_per_term"),
        "bedrijven_intersectie": result.get("companies_intersection"),
        "definities": result.get("definitions"),
        "technologieen_per_bedrijf": result.get("technologies_per_company")
    }


def compose_answer(request: dict, llm_client) -> str:
    result = request["result"]

    if result.get("found") is False:
        return f"Geen informatie gevonden over: {', '.join(result.get('terms', []))}."

    filled_prompt = build_filled_prompt(result, request["prompt_template"])
    return llm_client.ask(filled_prompt)


def build_filled_prompt(result: dict, prompt_template: str) -> str:
    context = build_answer_context(result)

    return (
        prompt_template
        .replace("{GEVONDEN}", str(context["gevonden"]))
        .replace("{TERMEN}", ", ".join(context["termen"]))
        .replace("{BEDRIJVEN_PER_TERM}", str(context["bedrijven_per_term"]))
        .replace("{BEDRIJVEN_INTERSECTIE}", str(context["bedrijven_intersectie"]))
        .replace("{DEFINITIES}", str(context["definities"]))
        .replace("{TECHNOLOGIEEN_PER_BEDRIJF}", str(context["technologieen_per_bedrijf"]))
    )
