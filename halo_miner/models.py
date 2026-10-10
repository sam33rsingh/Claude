"""Core data model shared by every source and every analysis step."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional

_WORD_RE = re.compile(r"[A-Za-z0-9'’]+")


@dataclass
class Post:
    """One unit of customer voice: a Reddit post/comment or a review."""

    source: str                      # reddit | yelp | google | csv
    text: str
    title: str = ""
    rating: Optional[float] = None   # 1-5 stars for reviews, None for Reddit
    author: str = ""
    url: str = ""
    created: str = ""                # ISO-8601 date string when known
    upvotes: int = 0                 # Reddit score / review "useful" votes
    comments: int = 0                # Reddit comment count
    venue: str = ""                  # subreddit or business name
    query: str = ""                  # search term that surfaced the post
    kind: str = "review"             # review | post | comment
    id: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.text = (self.text or "").strip()
        self.title = (self.title or "").strip()
        if self.rating is not None:
            try:
                self.rating = float(self.rating)
            except (TypeError, ValueError):
                self.rating = None
        if not self.id:
            key = f"{self.source}|{self.url}|{self.title}|{self.text[:200]}"
            self.id = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

    @property
    def full_text(self) -> str:
        if not self.title:
            return self.text
        sep = " " if self.title.rstrip().endswith((".", "!", "?")) else ". "
        return f"{self.title}{sep}{self.text}".strip()

    @property
    def word_count(self) -> int:
        return len(_WORD_RE.findall(self.full_text))

    @property
    def char_count(self) -> int:
        return len(self.full_text)

    @property
    def star_band(self) -> str:
        """Bucket ratings the way the Halo Strategy reads them."""
        if self.rating is None:
            return "unrated"
        if self.rating >= 4.5:
            return "5-star"
        if self.rating >= 3.0:
            return "3-4 star"   # the balanced, most useful reviews
        return "1-2 star"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["word_count"] = self.word_count
        d["star_band"] = self.star_band
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Post":
        allowed = {k for k in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in d.items() if k in allowed})
