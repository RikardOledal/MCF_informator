from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = PROJECT_ROOT / "data" / "MCF_markdown"
VECTOR_DATABASE_PATH = PROJECT_ROOT / "data" / "lancedb"