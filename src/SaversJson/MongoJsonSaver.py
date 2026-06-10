import json
from pathlib import Path


def read_mongo_json(file_path: str = "src/database/MongoDB.json") -> dict:
    """Read and return JSON data from MongoDB.json."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_mongo_json_safe(file_path: str = "src/database/MongoDB.json") -> dict:
    """Read JSON file and return an empty dict if the file is missing or invalid."""
    try:
        return read_mongo_json(file_path)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_to_mongo_json(data: dict, file_path: str = "src/database/MongoDB.json"):
    """Save the given data to MongoDB.json."""
    path = Path(file_path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)

def append_to_mongo_json(new_data, file_path="src/database/MongoDB.json"):
    existing_data = read_mongo_json_safe(file_path)

    if not isinstance(existing_data, list):
        existing_data = []

    existing_data.append(new_data)

    save_to_mongo_json(existing_data, file_path)
  

