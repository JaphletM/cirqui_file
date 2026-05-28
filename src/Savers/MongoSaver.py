from pymongo import MongoClient


def get_terms_collection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["cirqui"]
    return db["terms"]


def load_existing_terms():
    collection = get_terms_collection()

    return list(
        collection.find({}, {"_id": 0})
    )


def save_new_terms(comparison_results):
    collection = get_terms_collection()

    new_terms = [
        {
            "term": item["term"],
            "definition": item["definition"],
            "category": item["category"]
        }
        for item in comparison_results
        if item["status"] == "new"
    ]

    if not new_terms:
        print("No new terms to save.")
        return

    collection.insert_many(new_terms)

    print(f"Saved {len(new_terms)} new terms.")