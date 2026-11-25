import json
import unittest
from unittest.mock import patch

from app import dorar


def _block(number, source, page, grade="صحيح", narrator="عمر بن الخطاب"):
    return f"""
<div class="hadith" style="text-align:justify;">{number} -   <span class="search-keys">إنما</span> الأعمال بالنيات . .</div>
<div class="hadith-info">
    <span class="info-subtitle">الراوي:</span> {narrator}</span>
    <span class="info-subtitle">المحدث:</span> البخاري
    <span class="info-subtitle">المصدر:</span>  {source}
    <span class="info-subtitle">الصفحة أو الرقم:</span>  {page}
    <span class="info-subtitle">خلاصة حكم المحدث:</span>  <span >{grade}</span>
</div>
--------------
<br/>
"""


class TestDorarClient(unittest.TestCase):
    def test_decode_handles_both_arabic_encodings(self):
        payload = json.dumps(
            {"ahadith": {"result": "إنما الأعمال بالنيات"}}, ensure_ascii=False
        )
        self.assertIn("إنما الأعمال بالنيات", dorar._decode(payload.encode("cp1256")))
        self.assertIn("إنما الأعمال بالنيات", dorar._decode(payload.encode("utf-8")))

    def test_search_maps_dorar_html_to_result_cards(self):
        with patch.object(dorar, "_fetch", return_value=_block(1, "صحيح البخاري", "1")) as fetch:
            results = dorar.search("إنما الأعمال بالنيات")

        fetch.assert_called_once_with("إنما الأعمال بالنيات")
        self.assertEqual(len(results), 1)
        card = results[0]
        self.assertEqual(card["kind"], "dorar")
        self.assertEqual(card["book"], "صحيح البخاري")
        self.assertEqual(card["author"], "البخاري")
        self.assertEqual(card["passage"], "إنما الأعمال بالنيات")
        self.assertEqual(card["reference"], "الصفحة أو الرقم: 1")
        self.assertEqual(card["note"], "صحيح")
        self.assertIn("المصدر: صحيح البخاري", card["citation_text"])
        self.assertIn("خلاصة حكم المحدث: صحيح", card["footnote"])
        self.assertIn("dorar.net/hadith/search", card["url"])

    def test_search_caps_results_and_skips_duplicates(self):
        html = "".join([
            _block(1, "صحيح البخاري", "1"),
            _block(2, "صحيح مسلم", "2"),
            _block(3, "سنن أبي داود", "3"),
            _block(4, "جامع الترمذي", "4"),
            _block(5, "صحيح البخاري", "1"),  # duplicate of the first
            _block(6, "مسند أحمد", "5"),
        ])
        with patch.object(dorar, "_fetch", return_value=html):
            results = dorar.search("إنما الأعمال بالنيات")

        self.assertEqual(len(results), 4)
        self.assertEqual(
            [card["book"] for card in results],
            ["صحيح البخاري", "صحيح مسلم", "سنن أبي داود", "جامع الترمذي"],
        )

    def test_empty_query_is_rejected(self):
        with self.assertRaises(dorar.DorarError):
            dorar.search("   ")

    def test_empty_response_returns_no_cards(self):
        with patch.object(dorar, "_fetch", return_value="<head></head>"):
            self.assertEqual(dorar.search("اختبار"), [])


if __name__ == "__main__":
    unittest.main()
