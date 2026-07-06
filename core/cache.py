import json
from pathlib import Path


class Cache:

    def __init__(self):

        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _safe_key(self, key):

        key = str(key)

        for ch in '<>:"/\\|?*&=%':
            key = key.replace(ch, "_")

        return key[:200]

    def _path(self, key):

        return self.cache_dir / f"{self._safe_key(key)}.json"

    def exists(self, key):

        return self._path(key).exists()

    def get(self, key):

        path = self._path(key)

        if not path.exists():
            return None

        try:

            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception:

            return None

    def set(self, key, value):

        path = self._path(key)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                value,
                f,
                indent=2,
                ensure_ascii=False,
            )

    def delete(self, key):

        path = self._path(key)

        if path.exists():
            path.unlink()

    def clear(self):

        for file in self.cache_dir.glob("*.json"):
            file.unlink()


cache = Cache()