import hashlib
import json
from pathlib import Path


class Cache:

    def __init__(self):

        self.base = Path("cache")

        (self.base / "pages").mkdir(parents=True, exist_ok=True)
        (self.base / "llm").mkdir(parents=True, exist_ok=True)
        (self.base / "search").mkdir(parents=True, exist_ok=True)

    def _path(self, folder, key):

        filename = hashlib.md5(key.encode()).hexdigest() + ".json"

        return self.base / folder / filename

    def load(self, folder, key):

        path = self._path(folder, key)

        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, folder, key, value):

        path = self._path(folder, key)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=2, ensure_ascii=False)


cache = Cache()