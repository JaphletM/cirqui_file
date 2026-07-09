import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
load_dotenv(Path(__file__).resolve().parents[2] / "src" / ".env")

from Extractors.TermMatcher import normalize_term
from Savers.QdrantSaver import search_similar_terms

print(search_similar_terms("Docker", limit=3))   # ongewijzigd
print(search_similar_terms("docker", limit=3))   # zoals normalize_term het zou maken
