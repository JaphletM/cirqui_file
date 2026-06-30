import json
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import PyMongoError


JSON_FILE = Path("src/database/MongoDB.json")


def get_terms_collection():
    client = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=2000
    )
    client.admin.command("ping")

    db = client["cirqui"]
    return db["terms"]


def load_terms_from_json():
    if not JSON_FILE.exists():
        return []

    try:
        with JSON_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = data.get("terms", [])

        flattened_terms = []

        for item in data:
            if isinstance(item, list):
                flattened_terms.extend(item)
            elif isinstance(item, dict):
                flattened_terms.append(item)

        return flattened_terms

    except json.JSONDecodeError:
        return []


def save_terms_to_json(new_terms):
    existing_terms = load_terms_from_json()
    existing_terms.extend(new_terms)

    with JSON_FILE.open("w", encoding="utf-8") as file:
        json.dump(existing_terms, file, indent=4, ensure_ascii=False)


def load_existing_terms():
    try:
        collection = get_terms_collection()
        return list(collection.find({}, {"_id": 0}))
    except PyMongoError:
        print("MongoDB unavailable. Loading terms from JSON instead.")
        return load_terms_from_json()


#def save_new_terms(comparison_results, company_name):

   # new_terms = [
       # {
        #    "term": item["term"],
       #     "definition": item["definition"],
       #     "category": item["category"],
         #   "company": company_name
       # }
       # for item in comparison_results
      #  if item["status"] == "new"
    
   # ]
    
  #  if not new_terms:
  #      print("No new terms to save.")
   #     return

   # try:
    #    collection = get_terms_collection()
    #    collection.insert_many(new_terms)
    #    print(f"Saved {len(new_terms)} new terms to MongoDB.")
   # except PyMongoError:
      #  save_terms_to_json(new_terms)
    #    print(f"MongoDB unavailable. Saved {len(new_terms)} new terms to JSON.")

def save_new_terms(comparison_results, company_name):

    try:
        collection=get_terms_collection()
        for item in comparison_results:
                collection.update_one (
                    {"term":item["term"]},
                    {
                        "$set": {
                        "term": item["term"],
                        "definition": item["definition"],
                        "category": item["category"]},
                        "$addToSet": {"companies":{"$each": [company_name]}}
                        }
                    upsert=True,
                )
                
    except PyMongoError:
        save_terms_to_json(comparison_results)
        print(f"MongoDB unavailable. Saved {len(comparison_results)} new terms to JSON.")






