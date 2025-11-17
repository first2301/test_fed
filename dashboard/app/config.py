# app/config.py
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)
SERVERS_FILE = CONFIG_DIR / "servers.yaml"

