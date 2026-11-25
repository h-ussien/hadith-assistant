import unittest
from unittest.mock import patch

from app import shamela


class TestShamelaClient(unittest.TestCase):
    def test_keywords_strip_diacritics_and_split_long_queries(self):
        self.assertEqual(
            shamela.search_keywords("إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ"),
            ["إنما الأعمال بالنيات"],
        )
        parts = shamela.search_keywords("سؤال عن النية. وهل تُقبل الأعمال؟")
        self.assertEqual(parts, ["سؤال عن النية", "وهل تقبل الأعمال"])

    def test_search_maps_shamela_evidence_to_result_cards(self):
        payload = {"layers": [
            {"key": "main", "results": [{
                "book_id": 1681,
                "page_id": 10,
                "title": "صحيح البخاري",
                "author": "البخاري",
                "preview": "إنما الأعمال بالنيات",
                "citation": {"markdown": "[صحيح البخاري (١/٦)](https://shamela.ws/book/1681/10)"},
            }]},
            {"key": "secondary", "results": [{
                "book_id": 1681,
                "page_id": 10,
                "title": "صحيح البخاري",
                "preview": "duplicate",
            }]},
        ]}
        with patch.object(shamela, "_tool", return_value=payload) as tool:
            results = shamela.search("إنما الأعمال بالنيات")

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result["book"], "صحيح البخاري")
        self.assertEqual(result["passage"], "إنما الأعمال بالنيات")
        self.assertEqual(result["url"], "https://shamela.ws/book/1681/10")
        self.assertEqual(result["citation_text"], "صحيح البخاري (١/٦)")
        tool.assert_called_once()

    def test_search_uses_only_the_four_approved_hadith_books(self):
        with patch.object(shamela, "_tool", return_value={"results": []}) as tool:
            shamela.search("الدين النصيحة")
        name, arguments = tool.call_args.args[:2]
        self.assertEqual(name, "shamela_find_scoped")
        self.assertEqual(arguments["book_ids"], list(shamela.APPROVED_BOOK_IDS))
        self.assertNotIn("category_ids", arguments)

    def test_search_returns_four_results_one_per_approved_book(self):
        results = []
        for book_id in reversed(shamela.APPROVED_BOOK_IDS):
            results.append({
                "book_id": book_id, "page_id": book_id,
                "title": "كتاب", "preview": "نص الحديث",
            })
        results.append({
            "book_id": 13163, "page_id": 1,
            "title": "مسند الشهاب", "preview": "ليس من الكتب الأربعة",
        })
        results.append({
            "book_id": shamela.APPROVED_BOOK_IDS[0], "page_id": 99,
            "title": " duplicate", "preview": "تكرار",
        })
        with patch.object(shamela, "_tool", return_value={"results": results}):
            found = shamela.search("الدين النصيحة")

        self.assertEqual(len(found), 4)
        self.assertEqual(
            [item["book_id"] for item in found], list(shamela.APPROVED_BOOK_IDS)
        )

    def test_missing_preview_is_filled_from_open_tool(self):
        payload = {"results": [{
            "book_id": 1727,
            "page_id": 4862,
            "title": "صحيح مسلم - ت عبد الباقي",
            "author": "مسلم",
            "citation": {"markdown": "[صحيح مسلم](https://shamela.ws/book/1727/4862)"},
        }]}
        opened = {"sources": [{
            "book_id": 1727,
            "page_id": 4862,
            "text": "إنما الأعمال بالنيات",
        }]}
        with patch.object(shamela, "_tool", side_effect=[payload, opened]):
            results = shamela.search("إنما الأعمال بالنيات")
        self.assertEqual(results[0]["passage"], "إنما الأعمال بالنيات")


if __name__ == "__main__":
    unittest.main()
