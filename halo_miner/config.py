from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "brand": "Studio Quattro Design",
    "website": "https://studioquattrodesign.com",
    "service": "interior design",
    "sources": {
        "reddit": {"enabled": True},
        "yelp": {"enabled": False},
        "google": {"enabled": False},
    },
    "weights": {},
    "lexicon_extra": {},
    "topics_extra": {},
    "report": {"top_n": 15, "swipe_n": 12},
}


def load_config(path: str | None) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if not path:
        return cfg
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError as e:
            raise SystemExit("pip install pyyaml to read YAML configs (or use JSON)") from e
        user = yaml.safe_load(text) or {}
    else:
        user = json.loads(text)
    _deep_update(cfg, user)
    return cfg


def _deep_update(base: Dict[str, Any], upd: Dict[str, Any]) -> None:
    for k, v in upd.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
