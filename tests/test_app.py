import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from app import data,domain,service
class TestResearchAssistant(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.patcher=patch.object(data,'DB',Path(self.temp.name)/'test.db');self.patcher.start();data.initialize();data.initialize_books()
    def tearDown(self):self.patcher.stop();self.temp.cleanup()
    def test_unified_search_includes_imported_full_text(self):
        data.add_book_passages([dict(kind='hadith',passage='هذا نص حديث كامل طويل للتجربة فقط وليس حديثا حقيقيا',book='كتاب اختبار',author='مؤلف تجريبي',chapter='',hadith_number='',volume='',page='',edition='',url='',note='')], 'test.csv')
        result=service.search_all('hadith','نص حديث كامل طويل')
        self.assertTrue(any(x['book']=='كتاب اختبار' and 'وليس حديثا حقيقيا' in x['passage'] for x in result))
    def test_catalog_stats(self):
        self.assertTrue(data.catalog_stats()['demonstration_and_manual'])
    def test_search_all_validates_kind(self):
        with self.assertRaises(ValueError):service.search_all('unknown','نص عربي كافي')
    def test_normalization(self):self.assertEqual(domain.normalize('إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ'),domain.normalize('انما الاعمال بالنيات'))
    def test_hadith_search(self):self.assertGreaterEqual(len(service.search('hadith','إنما الأعمال بالنيات')),2)
    def test_missing_quote(self):self.assertEqual(service.search('quote','نص غير موجود'),[])
    def test_quote_added(self):
        service.create_quote({'passage':'هذا نص تجريبي موثق','book':'كتاب تجريبي','author':'مؤلف','reference':'طبعة تجريبية','verified':True})
        self.assertEqual(len(service.search('quote','هذا نص تجريبي موثق')),1)
    def test_no_fake_pages(self):self.assertNotIn('ص ',service.search('hadith','إنما الأعمال بالنيات')[0]['footnote'])
    def test_unverified_quote_rejected(self):
        with self.assertRaises(ValueError):
            service.create_quote({'passage':'نص تجريبي','book':'كتاب','author':'مؤلف','reference':'طبعة'})
    def test_partial_match_label(self):
        result=service.search('hadith','الأعمال بالنيات')[0]
        self.assertEqual(result['match_type'],'excerpt')
    def test_edition_specific_footnote(self):
        service.create_quote({'passage':'نص اقتباس اختباري طويل','book':'كتاب تجريبي','author':'مؤلف','reference':'الطبعة الأولى','volume':'2','page':'45','verified':True})
        note=service.search('quote','نص اقتباس اختباري طويل')[0]['footnote']
        self.assertIn('ج 2',note)
        self.assertIn('ص 45',note)
        self.assertIn('الطبعة الأولى',note)
    def test_invalid_query(self):
        with self.assertRaises(ValueError):service.search('hadith','a')
if __name__=='__main__':unittest.main()
