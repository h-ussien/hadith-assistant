"""Read-only client for Shamela's official MCP search service.

The app's own catalog stays untouched; this module only forwards text queries to
https://mcp.shamela.ws and shapes the evidence into the cards used by the UI.
"""
from __future__ import annotations

import html
import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

MCP_URL = "https://mcp.shamela.ws/"
CA_FILE = Path(__file__).with_name("cacert.pem")
TIMEOUT = 30
MAX_RESULTS = 4

# Shamela book IDs for the four collections the search UI is allowed to show.
# One edition per collection keeps the result list to four distinct hadith books.
APPROVED_BOOKS = (
    (1681, "Sahih al-Bukhari"),
    (1727, "Sahih Muslim"),
    (1726, "Sunan Abi Dawud"),
    (1363, "Jami' at-Tirmidhi"),
)
APPROVED_BOOK_IDS = tuple(book_id for book_id, _ in APPROVED_BOOKS)

_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0640]")
_SPLITTER = re.compile(r"[.؟!،;\n]+")
_LINK = re.compile(r"\[([^\]]+)\]\((https://shamela\.ws/[^)]+)\)")


class ShamelaError(Exception):
    """Raised when the Shamela service cannot answer a query."""


_context = None


def _ssl_context():
    global _context
    if _context is None:
        if CA_FILE.exists():
            _context = ssl.create_default_context(cafile=str(CA_FILE))
        else:
            _context = ssl.create_default_context()
    return _context


def _rpc(method, params, request_id=1):
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }).encode("utf-8")
    request = urllib.request.Request(
        MCP_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "HadithResearchAssistant/1.0 (local educational app)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=_ssl_context()) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise ShamelaError("تعذّر الاتصال بالمكتبة الشاملة") from exc

    # The endpoint currently answers plain JSON; accept SSE as well for safety.
    if raw.lstrip().startswith("data:"):
        chunks = [line[5:].strip() for line in raw.splitlines() if line.startswith("data:")]
        raw = next((chunk for chunk in reversed(chunks) if chunk), raw)
    try:
        message = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ShamelaError("استجابة غير مفهومة من المكتبة الشاملة") from exc
    if message.get("error"):
        raise ShamelaError(message["error"].get("message", "خطأ من خدمة الشاملة"))
    return message.get("result", {})


def _tool(name, arguments, request_id=1):
    result = _rpc("tools/call", {"name": name, "arguments": arguments}, request_id)
    if result.get("isError"):
        detail = ""
        for part in result.get("content", []):
            if part.get("type") == "text":
                detail = part.get("text", "")
                break
        raise ShamelaError(detail[:200] or "خطأ من خدمة الشاملة")
    payload = result.get("structuredContent")
    if payload is None:
        for part in result.get("content", []):
            if part.get("type") == "text":
                payload = json.loads(part.get("text", "{}"))
                break
    return payload or {}


def search_keywords(query):
    """Turn a user query into intact Arabic phrases suitable for the MCP tool."""
    cleaned = _DIACRITICS.sub("", str(query or ""))
    cleaned = re.sub(r"[«\"'()\[\]<>]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()[:1000]
    parts = [part.strip() for part in _SPLITTER.split(cleaned) if len(part.strip()) >= 6]
    return (parts or [cleaned])[:3]


def _text(value):
    """Remove highlight tags from MCP previews without changing their wording."""
    return html.unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


def _citation(markdown, book_id, page_id):
    text = _LINK.sub(r"\1", markdown or "").strip()
    url = f"https://shamela.ws/book/{book_id}/{page_id}"
    match = _LINK.search(markdown or "")
    if match:
        url = match.group(2)
    return text, url


def _card(item):
    book_id = item.get("book_id") or 0
    page_id = item.get("page_id") or 0
    citation, url = _citation(
        (item.get("citation") or {}).get("markdown", ""), book_id, page_id
    )
    return {
        "kind": "shamela",
        "book": item.get("title") or "كتاب من المكتبة الشاملة",
        "author": item.get("author") or "",
        "passage": _text(item.get("preview")),
        "match_label": "مطابقة من المكتبة الشاملة",
        "provenance": "مقتطف من المكتبة الشاملة — راجع الصفحة قبل الاقتباس",
        "footnote": citation,
        "citation_text": citation,
        "url": url,
        "book_id": book_id,
        "page_id": page_id,
    }


def _fill_missing_previews(cards):
    """Use the read tool for top hits the search tool auto-opened without preview."""
    missing = [card for card in cards[:6] if not card["passage"]][:4]
    if not missing:
        return
    try:
        payload = _tool("shamela_open_many", {
            "pages": [
                {"book_id": card["book_id"], "page_id": card["page_id"], "max_chars": 1600}
                for card in missing
            ],
            "context": 0,
            "max_total_chars": 10000,
        }, request_id=2)
    except ShamelaError:
        return
    opened = {
        (source.get("book_id"), source.get("page_id")): source
        for source in payload.get("sources", [])
    }
    for card in missing:
        source = opened.get((card["book_id"], card["page_id"]), {})
        text = _text(source.get("text"))
        if text:
            card["passage"] = text[:900]
        markdown = (source.get("citation") or {}).get("markdown", "")
        if markdown:
            citation, url = _citation(markdown, card["book_id"], card["page_id"])
            card["citation_text"] = citation
            card["footnote"] = citation
            if citation:
                card["url"] = url


def search(query, kind="all", limit=MAX_RESULTS):
    """Search only the four approved hadith collections and return up to four cards.

    ``kind`` is kept for API compatibility; the Shamela UI always uses this
    hadith-only, strictly scoped search.
    """
    keywords = search_keywords(query)
    if not keywords:
        raise ShamelaError("اكتب نصًا للبحث أولًا")

    payload = _tool("shamela_find_scoped", {
        "query": keywords[0],
        "difficulty": "easy",
        "field": "body",
        "book_ids": list(APPROVED_BOOK_IDS),
        "limit": 20,
    })

    items = list(payload.get("results") or [])
    if not items:  # tolerate the ranked shape used by shamela_find
        for layer in payload.get("layers", []):
            items.extend(layer.get("results", []))

    cards = []
    seen = set()
    first_by_book = {}
    for item in items:
        book_id = item.get("book_id")
        if book_id not in APPROVED_BOOK_IDS:
            continue
        key = (book_id, item.get("page_id"))
        if key in seen:
            continue
        seen.add(key)
        card = _card(item)
        cards.append(card)
        first_by_book.setdefault(book_id, card)

    # Show one match per collection in the user's order, then fill any gaps.
    picked = []
    picked_keys = set()
    for book_id in APPROVED_BOOK_IDS:
        card = first_by_book.get(book_id)
        if card:
            picked.append(card)
            picked_keys.add((card["book_id"], card["page_id"]))
    for card in cards:
        key = (card["book_id"], card["page_id"])
        if key not in picked_keys:
            picked.append(card)
            picked_keys.add(key)

    selected = picked[:max(0, min(int(limit), MAX_RESULTS))]
    _fill_missing_previews(selected)
    return selected
