"""Read-only client for Dorar.net's public hadith search endpoint.

The app keeps Dorar as a separate search scope; it does not copy Dorar's
encyclopedia into this project and never changes the local catalogs.
"""
from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://dorar.net"
SEARCH_URL = BASE_URL + "/dorar_api.json"
TIMEOUT = 20
MAX_RESULTS = 4
USER_AGENT = "HadithResearchAssistant/1.0 (local educational app)"

_HADITH_BLOCK = re.compile(
    r'<div class="hadith"[^>]*>(.*?)</div>\s*<div class="hadith-info">(.*?)</div>',
    re.IGNORECASE | re.DOTALL,
)
_INFO_SPAN = re.compile(
    r'<span class="info-subtitle"[^>]*>(.*?):?</span>(.*?)(?=<span class="info-subtitle"|$)',
    re.IGNORECASE | re.DOTALL,
)
_INDEX = re.compile(r"^\s*\d+\s*-\s*")

# Dorar has served this endpoint as both UTF-8 and Windows-1256. Mojibake from
# reading UTF-8 as Windows-1256 is full of these letters; real Arabic is not.
_BAD_MOJIBAKE = set("طظژچگپ¢¬±÷×‘’")
_GOOD_ARABIC = set("النميتواحدسبعفقكلرهىةءؤئإآأ")

_LABELS = {
    "الراوي": "narrator",
    "المحدث": "muhaddith",
    "المصدر": "source",
    "الصفحة أو الرقم": "page_or_number",
    "خلاصة حكم المحدث": "grade",
}


class DorarError(Exception):
    """Raised when the Dorar service cannot answer a query."""


def _decode(raw):
    """Decode Dorar's undeclared encoding, which has varied by response."""
    candidates = []
    for encoding in ("utf-8", "cp1256"):
        try:
            candidates.append(raw.decode(encoding))
        except UnicodeDecodeError:
            continue
    if not candidates:
        return raw.decode("utf-8", "replace")

    def arabic_score(value):
        arabic = [char for char in value if "\u0600" <= char <= "\u06ff"]
        if not arabic:
            return -10 ** 6
        good = sum(char in _GOOD_ARABIC for char in arabic)
        bad = sum(char in _BAD_MOJIBAKE for char in arabic)
        return good - 3 * bad + len(arabic) / 10

    return max(candidates, key=arabic_score)


def _fetch(query):
    url = SEARCH_URL + "?" + urllib.parse.urlencode({"skey": query})
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json,text/plain,*/*",
    })
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise DorarError("تجاوزت حد الطلبات في موقع الدرر السنية. حاول لاحقًا") from exc
        raise DorarError("تعذّر الوصول إلى موقع الدرر السنية") from exc
    except urllib.error.URLError as exc:
        raise DorarError("تعذّر الاتصال بموقع الدرر السنية") from exc

    try:
        payload = json.loads(_decode(raw))
    except (json.JSONDecodeError, TypeError) as exc:
        raise DorarError("استجابة غير مفهومة من الدرر السنية") from exc
    result = (payload.get("ahadith") or {}).get("result", "")
    if not isinstance(result, str):
        raise DorarError("استجابة غير مفهومة من الدرر السنية")
    return result


def search_keywords(query):
    """Normalize whitespace while keeping the wording the user searched for."""
    cleaned = re.sub(r"\s+", " ", str(query or "")).strip()
    return cleaned[:200]


def _text(value):
    """Strip Dorar's highlight markup without changing the wording."""
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return re.sub(r"(?:\s*\.\s*)+$", "", value)


def _info_fields(info_html):
    fields = {}
    for match in _INFO_SPAN.finditer(info_html or ""):
        label = _text(match.group(1)).rstrip(":")
        fields[label] = _text(match.group(2))
    return {
        target: fields.get(label, "")
        for label, target in _LABELS.items()
    }


def _card(passage_html, info_html, query):
    passage = _INDEX.sub("", _text(passage_html)).strip()
    fields = _info_fields(info_html)
    source = fields["source"] or "الموسوعة الحديثية — الدرر السنية"
    narrator = fields["narrator"]
    muhaddith = fields["muhaddith"]
    page = fields["page_or_number"]
    grade = fields["grade"]

    citation_parts = [f"المصدر: {source}"]
    if page:
        citation_parts.append(f"الصفحة أو الرقم: {page}")
    if muhaddith:
        citation_parts.append(f"المحدث: {muhaddith}")
    if narrator and narrator != "-":
        citation_parts.append(f"الراوي: {narrator}")
    if grade:
        citation_parts.append(f"خلاصة حكم المحدث: {grade}")
    citation = " | ".join(citation_parts)

    return {
        "kind": "dorar",
        "book": source,
        "author": muhaddith or "",
        "passage": passage,
        "match_label": "مطابقة من الدرر السنية",
        "provenance": "مقتطف من الدرر السنية — راجع الصفحة قبل الاقتباس",
        "footnote": citation,
        "citation_text": citation,
        "url": BASE_URL + "/hadith/search?" + urllib.parse.urlencode({"q": query}),
        "reference": f"الصفحة أو الرقم: {page}" if page else "",
        "note": grade,
    }


def search(query, limit=MAX_RESULTS):
    """Search Dorar.net and return normalized cards for the chat UI."""
    keywords = search_keywords(query)
    if len(keywords) < 2:
        raise DorarError("اكتب نصًا للبحث أولًا")

    html_result = _fetch(keywords)
    cards = []
    seen = set()
    cap = max(0, min(int(limit), MAX_RESULTS))
    for match in _HADITH_BLOCK.finditer(html_result):
        card = _card(match.group(1), match.group(2), keywords)
        if not card["passage"]:
            continue
        key = (card["book"], card["reference"], card["passage"][:120])
        if key in seen:
            continue
        seen.add(key)
        cards.append(card)
        if len(cards) >= cap:
            break
    return cards
