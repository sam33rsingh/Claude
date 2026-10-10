"""The Halo lexicon.

Sabri Suby's research phase asks one question of every post a dream buyer
writes: *what does this reveal about their pains, fears, hopes and dreams,
and what proof language do they use when they are delighted?*  The phrase
lists below are the first-pass detector for each bucket.  They are tuned to
the residential interior-design / renovation market Studio Quattro serves,
but every list can be extended from ``config.yaml`` without touching code.

Each entry is ``(regex_pattern, weight)``.  Weights let an unmistakable
phrase ("worth every penny") count more than a weak signal ("good").
"""
from __future__ import annotations

import re
from typing import Dict, List, Pattern, Tuple

HALO_CATEGORIES = ["pains", "fears", "hopes", "dreams", "testimonials"]

CATEGORY_LABELS = {
    "pains": "Pains & frustrations (what hurts right now)",
    "fears": "Fears & anxieties (what they are afraid will happen)",
    "hopes": "Hopes (what they are actively seeking)",
    "dreams": "Dreams (the vivid after-picture they long for)",
    "testimonials": "Testimonials & proof language (how delight sounds)",
}

_LEXICON: Dict[str, List[Tuple[str, float]]] = {
    "pains": [
        (r"\bfrustrat\w*", 2.0), (r"\bannoy\w*", 1.5), (r"\bnightmare\b", 3.0),
        (r"\bover budget\b|\bwent over\b|\bblew (the|our) budget\b", 3.0),
        (r"\bdelay\w*|\bbehind schedule\b|\bmonths? late\b|\btook forever\b|\bdragged on\b", 2.5),
        (r"\bno communication\b|\bnever (called|got) back\b|\bghost\w*|\bunresponsive\b|\bradio silence\b", 3.0),
        (r"\bwaste of (money|time)\b", 3.0), (r"\bdisappoint\w*", 2.0), (r"\bregret\w*", 2.5),
        (r"\bunprofessional\b", 2.5), (r"\bhidden (fee|cost|charge)s?\b|\bupcharg\w*|\bmark-?ups?\b|\bchange orders?\b", 2.5),
        (r"\bmess\b|\bmessy\b|\bchaos\b", 1.5), (r"\bstress\w*", 2.0), (r"\boverwhelm\w*", 2.5),
        (r"\bexhaust\w*", 2.0), (r"\bugly\b|\bdoesn'?t match\b|\bclash\w*|\bmismatch\w*", 2.0),
        (r"\bhate\b|\bhated\b", 1.5), (r"\bpushy\b|\bupsell\w*", 2.0),
        (r"\bparalys\w*|\banalysis paralysis\b|\bcan'?t decide\b|\btoo many (options|choices)\b", 2.5),
        (r"\bcontractor\w* (flaked|disappeared|quit|bailed|never showed)\b|\bno-?shows?\b", 3.0),
        (r"\bexpensive\b|\boverpriced\b|\bpricey\b|\bcost(s)? a fortune\b", 1.5),
        (r"\bcheap (materials|finish|work)\b|\bpoor (quality|workmanship)\b|\bshoddy\b|\bsloppy\b", 2.5),
        (r"\bnot what (i|we) (asked|wanted)\b|\bignored (my|our)\b|\bdidn'?t listen\b", 3.0),
        (r"\bwasted\b|\bthrew away\b|\bhad to redo\b|\bredo\b", 2.0),
        (r"\bboring\b|\bgeneric\b|\bcookie[- ]cutter\b|\bbland\b|\bsterile\b|\bshowroom\b", 2.0),
        (r"\bdoesn'?t (feel|look) (like|right)\b|\bsomething'?s off\b|\bjust not working\b", 2.0),
        (r"\bpiecemeal\b|\bhodge-?podge\b|\brandom (stuff|furniture)\b|\bnothing goes together\b", 2.5),
        (r"\bdark\b|\bcramped\b|\bcluttered\b|\bdated\b|\boutdated\b|\btired\b", 1.5),
    ],
    "fears": [
        (r"\bafraid\b|\bscared\b|\bterrified\b", 3.0), (r"\bworr(y|ied|ies)\b|\bnervous\b|\banxious\b|\banxiety\b", 2.5),
        (r"\bwhat if\b", 2.0), (r"\brisk\w*", 1.5), (r"\brip(ped)?[- ]off\b|\bscam\w*|\bget burned\b|\btaken advantage\b", 3.0),
        (r"\bmistake\w*|\bwrong (choice|decision|color|colour)\b|\bmess (it )?up\b|\bscrew (it )?up\b", 2.5),
        (r"\bcan'?t afford\b|\bafford\w*|\bbreak the bank\b", 2.0),
        (r"\bhesitant\b|\bhesitat\w*|\bsecond[- ]guess\w*|\bnot sure\b|\bunsure\b|\bno idea\b|\bclueless\b", 2.0),
        (r"\btrust\w*", 1.5), (r"\bruin\w*", 2.5), (r"\bend up (with|hating|regretting)\b", 2.5),
        (r"\btoo expensive\b|\bsticker shock\b|\bhow much (does|do|should|will)\b", 1.5),
        (r"\bworth it\??|\bis it worth\b|\bwaste\b", 1.5),
        (r"\bpermanent\b|\bstuck with\b|\blive with\b|\bcan'?t undo\b", 2.5),
        (r"\bjudg\w*|\bembarrass\w*|\bwhat (will|would) (people|guests|family) think\b", 2.5),
        (r"\blose control\b|\btake over\b|\bimpose (their|his|her) (style|taste)\b|\bnot (my|our) style\b", 2.5),
        (r"\bresale\b|\bhurt (the )?value\b|\bdate(d)? quickly\b|\bgo out of style\b|\btrendy\b", 1.5),
        (r"\bdeposit\b|\bupfront\b|\bnon-?refundable\b", 1.5),
    ],
    "hopes": [
        (r"\bhop(e|ing|ed)\b", 2.5), (r"\bwant(ed|s)? to\b", 1.0), (r"\bwould love\b|\bi'?d love\b|\bwe'?d love\b", 2.5),
        (r"\bwish\w*", 2.0), (r"\blooking for\b|\bin search of\b|\bsearching for\b", 2.0),
        (r"\bideally\b", 1.5), (r"\btrying to\b", 1.5), (r"\bgoal\b|\bgoals\b", 1.5),
        (r"\bfinally\b", 1.5), (r"\bsomeday\b|\bone day\b|\beventually\b", 1.5),
        (r"\bplan(ning)? to\b|\babout to\b|\bgetting ready to\b", 1.5),
        (r"\bneed (some )?help\b|\badvice\b|\brecommendations?\b|\bsuggestions?\b|\btips\b", 2.0),
        (r"\bwithin (our|my|the) budget\b|\bon a budget\b|\baffordable\b|\breasonabl\w*", 1.5),
        (r"\bsimpl(e|er|ify)\b|\beasier\b|\bhassle[- ]free\b|\bstress[- ]free\b|\bturnkey\b|\bone[- ]stop\b", 2.0),
        (r"\bguidance\b|\bdirection\b|\bsecond opinion\b|\bsomeone (who|to)\b", 2.0),
        (r"\bpull (it )?together\b|\bcohesive\b|\bflow\b|\bmake (it )?work\b", 2.0),
        (r"\bfunctional\b|\bpractical\b|\bstorage\b|\bkid[- ]friendly\b|\bpet[- ]friendly\b", 1.5),
        (r"\btimeless\b|\bbuilt to last\b|\blasts? (for )?(years|decades|a lifetime)\b|\bage well\b|\bstand the test of time\b", 1.5),
    ],
    "dreams": [
        (r"\bdream (home|house|kitchen|bathroom|space|room|living room)\b", 3.5), (r"\bforever home\b", 3.0),
        (r"\balways wanted\b|\balways dreamed\b|\bever since\b", 3.0), (r"\bvision\b", 2.0),
        (r"\bmagazine\b|\binstagram[- ]worthy\b|\bout of a (magazine|catalog)\b|\bpicture[- ]perfect\b", 2.0),
        (r"\boasis\b|\bsanctuary\b|\bretreat\b|\bhaven\b|\bspa[- ]like\b|\bresort\b", 3.0),
        (r"\btransform\w*", 2.0), (r"\bentertain\w*|\bhost\w* (dinner|friends|family|holidays)\b|\bgather\w*", 2.0),
        (r"\bfeel(s)? like (home|us|me|a)\b|\bfeels like\b", 2.0), (r"\bwow\b|\bjaw[- ]dropp\w*|\bshow-?stopp\w*|\bshow-?piece\b", 2.5),
        (r"\bstunning\b|\bbreathtaking\b|\bgorgeous\b|\bbeautiful\b|\bluxur\w*|\belegant\b", 1.5),
        (r"\bproud\b|\bpride\b|\bcan'?t wait to show\b", 2.5),
        (r"\bcalm\b|\bpeaceful\b|\bserene\b|\bcozy\b|\bcosy\b|\bwarm and inviting\b|\binviting\b", 2.0),
        (r"\blight[- ]filled\b|\bbright and airy\b|\bopen (and )?airy\b|\bnatural light\b", 2.0),
        (r"\bmy (own )?style\b|\bour style\b|\breflects? (who we are|us|me|our personality)\b|\bpersonality\b", 2.5),
        (r"\bcoming home to\b|\bwalk(ing)? in(to)? (the door|the room)\b|\bevery (morning|day|evening)\b", 2.5),
        (r"\bfamily (gathers?|time|room)\b|\bgrow old\b|\bkids grow up\b|\bmemories\b", 2.5),
    ],
    "testimonials": [
        (r"\bhighly recommend\w*", 3.5), (r"\brecommend\w*", 1.5), (r"\bexceeded\b|\bbeyond (our|my) expectations\b", 3.0),
        (r"\babove and beyond\b", 3.0), (r"\bworth every (penny|dollar|cent)\b", 3.5), (r"\bbest (decision|money|investment)\b", 3.5),
        (r"\bthank you\b|\bthanks to\b|\bgrateful\b", 2.0), (r"\bamazing\b|\bincredible\b|\bphenomenal\b|\boutstanding\b|\bfantastic\b", 1.5),
        (r"\bprofessional\w*", 1.5), (r"\bon (time|schedule)\b|\bon budget\b|\bunder budget\b", 2.5),
        (r"\battention to detail\b|\bdetail[- ]oriented\b|\bmeticulous\b", 2.5), (r"\blistened\b|\bheard us\b|\bunderstood (us|me|what we)\b|\bgot (it|us|our vision)\b", 3.0),
        (r"\bresponsive\b|\bcommunicat\w*|\bkept us (informed|in the loop|updated)\b", 2.0),
        (r"\bcouldn'?t be happier\b|\bthrilled\b|\bover the moon\b|\bin love with\b|\blove (our|my|the) new\b", 3.0),
        (r"\bwould (hire|use|work with) (them )?again\b|\balready (booked|hired|recommended)\b", 3.0),
        (r"\bpatient\b|\bpatience\b|\bno pressure\b|\bnever (felt )?pushed\b", 2.0),
        (r"\bsaved (us|me) (money|time|from)\b|\bavoided (a )?(costly|expensive)\b|\bmistakes? (we|i) would have\b", 3.0),
        (r"\bseamless\b|\bsmooth\w*|\bpainless\b|\beffortless\b|\bstress[- ]free\b|\bhandled everything\b|\btook care of\b", 2.5),
        (r"\bbrought (our|my|the) vision to life\b|\bexactly what (we|i) (wanted|envisioned|pictured)\b|\bnailed it\b", 3.5),
        (r"\bcompliments?\b|\beveryone (asks|comments|loves)\b|\bguests? (love|rave|compliment)\w*", 2.5),
        (r"\btrustworthy\b|\bhonest\b|\btransparent\b|\bno surprises\b|\bupfront (about|with)\b", 2.5),
    ],
}

# Secondary lenses Suby asks for: what they've already tried / objections,
# and the life events that trigger a purchase.  Reported, not scored.
OBJECTIONS: List[Tuple[str, float]] = [
    (r"\bdiy\b|\bdo it (myself|ourselves)\b|\bon (my|our) own\b", 2.0),
    (r"\bhouzz\b|\bpinterest\b|\binstagram\b|\btiktok\b|\byoutube\b", 1.0),
    (r"\bcheaper\b|\bcheapest\b|\bsave money\b|\bbudget[- ]friendly\b", 1.5),
    (r"\bdesign(er)? fee\b|\bhourly\b|\bflat fee\b|\bpercentage\b|\bretainer\b|\bmarkup\b|\bcommission\b", 2.0),
    (r"\bworth (it|the (money|cost|fee))\b|\bjustify\b", 2.0),
    (r"\bikea\b|\bwayfair\b|\bwest elm\b|\bcrate\b|\brestoration hardware\b|\bcb2\b|\bpottery barn\b", 1.0),
    (r"\be-?design\b|\bonline design\b|\bvirtual design\b|\bhavenly\b|\bmodsy\b|\bdecorilla\b", 2.0),
    (r"\bquote\w*|\bestimate\w*|\bbids?\b|\bconsultation\b", 1.0),
    (r"\bfriend (who|that)\b|\bmy (sister|mom|aunt|cousin)\b|\bfamily member\b", 1.5),
]

TRIGGERS: List[Tuple[str, float]] = [
    (r"\bjust (bought|closed|moved)\b|\bnew (house|home|build|construction)\b|\bmoving in\b|\bclosing (on|in)\b", 3.0),
    (r"\bbaby\b|\bexpecting\b|\bnursery\b|\bkids?\b|\btoddler\w*|\bteenager\w*", 1.5),
    (r"\bretir\w*|\bempty[- ]nest\w*|\bdownsiz\w*", 2.5),
    (r"\brenovat\w*|\bremodel\w*|\bgut\w*|\baddition\b|\bextension\b", 2.0),
    (r"\bsell(ing)?\b|\blisting\b|\bstag(e|ing)\b|\bresale\b", 2.0),
    (r"\bwork(ing)? from home\b|\bhome office\b|\bwfh\b", 2.0),
    (r"\bmarried\b|\bwedding\b|\bengaged\b|\bmoving in together\b|\bmerg(e|ing) (our )?(stuff|furniture)\b", 2.0),
    (r"\bdivorc\w*|\bfresh start\b|\bstarting over\b", 2.5),
    (r"\binherit\w*|\bparents'? (house|home)\b|\baging parents?\b|\bin-?laws?\b", 2.0),
    (r"\bholiday\w*|\bthanksgiving\b|\bchristmas\b|\bbefore (the )?(holidays|guests|party)\b", 2.0),
]

# Topics: the *subject* a sentence is about, independent of emotional bucket.
TOPICS: Dict[str, str] = {
    "budget & pricing": r"\bbudget\w*|\bcost\w*|\bprice\w*|\bpricing\b|\bfee\w*|\bexpensive\b|\bafford\w*|\bmoney\b|\b\$\d|\bquote\w*|\bmarkup\w*|\binvoice\w*|\bcharg\w*",
    "communication & responsiveness": r"\bcommunicat\w*|\brespon\w*|\bcall\w*|\bemail\w*|\btext\w*|\bupdate\w*|\bghost\w*|\blisten\w*|\bheard\b|\bexplain\w*|\bin the loop\b",
    "timeline & delays": r"\btimeline\w*|\bschedul\w*|\bdelay\w*|\bweeks?\b|\bmonths?\b|\bdeadline\w*|\bon time\b|\blate\b|\btook forever\b|\bwait\w*",
    "quality & craftsmanship": r"\bquality\b|\bcraft\w*|\bworkmanship\b|\bfinish\w*|\bmaterials?\b|\binstall\w*|\bdetail\w*|\bsloppy\b|\bshoddy\b|\bwell[- ]made\b",
    "trust & honesty": r"\btrust\w*|\bhonest\w*|\btransparen\w*|\bscam\w*|\brip\w*|\bupfront\b|\bhidden\b|\bintegrity\b|\breliable\b|\bdependable\b",
    "style, taste & cohesion": r"\bstyle\w*|\btaste\w*|\baesthetic\w*|\bcolor\w*|\bcolour\w*|\bpalette\w*|\bcohesive\b|\bmodern\b|\btraditional\b|\bminimal\w*|\bmatch\w*|\bflow\b|\bvibe\b|\blook\b",
    "process & decision stress": r"\bprocess\b|\bdecision\w*|\bdecid\w*|\boverwhelm\w*|\boption\w*|\bchoic\w*|\bstress\w*|\bhassle\w*|\bmanage\w*|\bcoordinat\w*|\bjuggl\w*",
    "contractors & trades": r"\bcontractor\w*|\bbuilder\w*|\btrades?\b|\bplumber\w*|\belectrician\w*|\bpainter\w*|\bcabinet\w*|\binstaller\w*|\bsubs?\b|\bcrew\b",
    "function & livability": r"\bfunction\w*|\bpractical\w*|\bstorage\b|\bspace\b|\blayout\b|\bkids?\b|\bpets?\b|\bdog\w*|\bcat\w*|\bfamily\b|\bcomfort\w*|\bliv(e|ing|able)\b",
    "designer value & fit": r"\bdesigner\w*|\bdecorator\w*|\bworth it\b|\bvalue\b|\bexpertise\b|\bvision\b|\bideas?\b|\bcreativ\w*|\bconsult\w*|\bexperience\b",
}

INTENSIFIERS = re.compile(
    r"\b(so|very|extremely|absolutely|completely|totally|incredibly|truly|really|never|always|literally|honestly|seriously|utterly|beyond)\b|!{2,}|[A-Z]{4,}",
)
FIRST_PERSON = re.compile(r"\b(i|i'?m|i'?ve|we|we'?re|we'?ve|my|our|me|us)\b", re.IGNORECASE)

STOPWORDS = set(
    """a an the and or but if then so of to in on at for with from by as is are was were be been being am
    i me my we our us you your he she it its they them their this that these those there here what which who
    whom whose when where why how all any both each few more most other some such no nor not only own same than
    too very can will just don should now do does did doing have has had having would could about into over
    after before again further once up down out off above below between through during also like get got
    one two also really even still much many lot lots thing things way know think want wanted im ive dont didnt
    cant wasnt werent isnt arent doesnt wouldnt couldnt shouldnt were theyre youre hes shes weve theyve
    going went go gone make made say said see seen seem seemed need needed take took us ok okay yes well
    because while until since however though although already around actually basically pretty quite
    s t re ve ll d m""".split()
)


def compile_lexicon(extra: Dict[str, List[Tuple[str, float]]] | None = None) -> Dict[str, List[Tuple[Pattern[str], float]]]:
    """Return compiled patterns per category, merging user additions."""
    merged: Dict[str, List[Tuple[str, float]]] = {k: list(v) for k, v in _LEXICON.items()}
    for cat, entries in (extra or {}).items():
        merged.setdefault(cat, []).extend(entries)
    return {
        cat: [(re.compile(p, re.IGNORECASE), float(w)) for p, w in entries]
        for cat, entries in merged.items()
    }


def compile_simple(entries: List[Tuple[str, float]]) -> List[Tuple[Pattern[str], float]]:
    return [(re.compile(p, re.IGNORECASE), float(w)) for p, w in entries]


def compile_topics(extra: Dict[str, str] | None = None) -> Dict[str, Pattern[str]]:
    merged = dict(TOPICS)
    merged.update(extra or {})
    return {k: re.compile(v, re.IGNORECASE) for k, v in merged.items()}
