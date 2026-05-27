def find_existing_term(term_name, existing_terms):
    term_name = term_name.lower().strip()

    for existing_term in existing_terms:
        existing_name = existing_term.get("term", "").lower().strip()

        if existing_name == term_name:
            return existing_term

    return None


def compare_terms(extracted_terms, existing_terms):
    results = []

    for extracted_term in extracted_terms:
        match = find_existing_term(
            extracted_term.get("term", ""),
            existing_terms
        )

        if match:
            results.append({
                "term": extracted_term.get("term", ""),
                "definition": extracted_term.get("definition", ""),
                "category": extracted_term.get("category", ""),
                "status": "exists"
            })
        else:
            results.append({
                "term": extracted_term.get("term", ""),
                "definition": extracted_term.get("definition", ""),
                "category": extracted_term.get("category", ""),
                "status": "new"
            })

    return results