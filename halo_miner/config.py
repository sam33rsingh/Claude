from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

# Studio Quattro Design: Italian kitchen & cabinetry design studio, Solana Beach CA,
# serving San Diego and Orange County (Veneta Cucine, Sangiacomo, Kico lines).
DEFAULT_CONFIG: Dict[str, Any] = {
    "brand": "Studio Quattro Design",
    "website": "https://studioquattrodesign.com",
    "service": "Italian kitchen and cabinetry design",
    "location": "Solana Beach, CA (San Diego & Orange County)",
    "sources": {
        "reddit": {"enabled": True},
        "yelp": {"enabled": False, "businesses": [{"name": "Studio Quattro Design", "url": "https://www.yelp.com/biz/studio-quattro-design-solana-beach"}]},
        "google": {"enabled": False},
    },
    "weights": {},
    "lexicon_extra": {
        # Cabinetry / kitchen-showroom market specifics, layered on the base lexicon.
        "pains": [
            [r"\bparticle ?board\b|\bmdf\b|\bpeel(ing|ed)\b|\bchip(ped|ping)\b|\bwarp(ed|ing)\b|\bsag(ging|ged)\b", 2.5],
            [r"\bsoft[- ]close (broke|stopped|failed)\b|\bdrawers? (stick|sticking|fell|broke)\b|\bhinges? (broke|sagging)\b", 2.5],
            [r"\blead ?times?\b|\btook (months|forever) to (arrive|ship|come)\b|\bstill waiting on\b|\bback[- ]?ordered\b", 2.5],
            [r"\bdamaged in (shipping|transit)\b|\barrived damaged\b|\bwrong (size|color|finish|door)s?\b", 3.0],
            [r"\bgaps?\b|\bdoesn'?t line up\b|\bcrooked\b|\buneven\b|\bmisaligned\b|\bfiller strips?\b", 2.0],
            [r"\bbig[- ]box\b|\bhome depot\b|\blowe'?s\b|\bikea\b.*\b(fell apart|cheap|flimsy)\b", 2.0],
            [r"\binstaller\w* (no-?showed|disappeared|botched|rushed)\b|\binstall(ation)? was (a )?(mess|nightmare|sloppy)\b", 3.0],
        ],
        "fears": [
            [r"\bsight unseen\b|\bcan'?t (see|touch) (it|them) (first|in person)\b|\bordering (online|from a catalog)\b", 2.5],
            [r"\bcustom (means|so) no returns?\b|\bnon-?returnable\b|\bfinal sale\b|\bstuck with (the|these) cabinets\b", 3.0],
            [r"\bwill (it|they) (hold up|last)\b|\bhow (long|well) (do|will) (they|these) (last|hold up)\b", 2.0],
            [r"\bimport(ed|ing)? from (italy|europe)\b.*\b(delay|tariff|customs|risk)\w*", 2.0],
        ],
        "dreams": [
            [r"\bchef'?s kitchen\b|\bcook(ing)? (for|with) (friends|family)\b|\bgather (around|in) the kitchen\b", 3.0],
            [r"\bshowroom[- ]quality\b|\bmagazine[- ]worthy\b|\blooks? (like|straight out of) (a )?(magazine|showroom)\b", 2.5],
            [r"\bhandle-?less\b|\bsleek\b|\bclean lines\b|\bminimal(ist)?\b|\beuropean (look|style|feel)\b|\bitalian (look|style|feel|design)\b", 2.0],
            [r"\beverything (has|in) its place\b|\bhidden storage\b|\bclutter[- ]free\b|\borganized\b", 2.0],
        ],
        "testimonials": [
            [r"\bon schedule\b|\bclear communication\b|\bkept (us|me) (informed|updated)\b", 2.5],
            [r"\bknowledgeable\b|\bknew (the|her|his|their) (products|stuff|materials)\b|\bexpert(ise)?\b", 2.0],
            [r"\bhelped (us|me) (choose|pick|select|decide)\b|\bmaterial selection\b|\bsamples?\b", 2.0],
            [r"\bshowroom\b.*\b(beautiful|clean|helpful|friendly|welcoming)\b", 2.0],
            [r"\bbuilt (to last|like a tank)\b|\bsolid\b|\bquality (is|was) (incredible|outstanding|top)\b", 2.0],
        ],
    },
    "topics_extra": {
        "cabinetry & materials": r"\bcabinet\w*|\bcabinetry\b|\bdrawers?\b|\bdoors?\b|\bhinges?\b|\bsoft[- ]close\b|\bveneer\b|\blacquer\b|\bmelamine\b|\bplywood\b|\bparticle ?board\b|\bmdf\b|\bfinish(es)?\b|\bhardware\b|\bcountertops?\b|\bquartz\b|\bmarble\b",
        "showroom & selection": r"\bshowroom\b|\bsamples?\b|\bselection\b|\bdesign lab\b|\bin person\b|\bsee (it|them) in person\b|\bcollections?\b",
        "lead time & delivery": r"\blead ?times?\b|\bdeliver\w*|\bship\w*|\barriv\w*|\bimport\w*|\bfrom italy\b|\bcustoms\b|\bback-?order\w*",
    },
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
    # lexicon entries arrive as [pattern, weight] lists from YAML/JSON; normalise to tuples
    cfg["lexicon_extra"] = {k: [tuple(e) for e in v] for k, v in (cfg.get("lexicon_extra") or {}).items()}
    return cfg


def _deep_update(base: Dict[str, Any], upd: Dict[str, Any]) -> None:
    for k, v in upd.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
