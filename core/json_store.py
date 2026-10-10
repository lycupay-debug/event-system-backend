from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class JSONStore:
    """Read and atomically replace independent JSON files under one project root."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir).resolve() if base_dir is not None else Path(__file__).resolve().parent.parent

    def _resolve(self, file_path: str | Path) -> Path:
        path = Path(file_path)
        if path.is_absolute():
            raise ValueError("file_path must be relative to the project root")
        resolved = (self.base_dir / path).resolve()
        if not resolved.is_relative_to(self.base_dir):
            raise ValueError("file_path must remain inside the project root")
        return resolved

    def load(self, file_path: str | Path) -> Any:
        path = self._resolve(file_path)
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)

    def save(self, file_path: str | Path, data: Any) -> Any:
        path = self._resolve(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, path)
            if os.name == "posix":
                dir_fd = os.open(path.parent, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        except Exception:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise
        return data
