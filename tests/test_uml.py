import unittest
from unittest.mock import patch
from app.uml import User,Admin,Hadith,Quotation,Database,Search,Citation,UI
class UMLTests(unittest.TestCase):
    def test_user_and_admin(self):
        self.assertEqual(User('A').getRole(),'student')
        self.assertEqual(Admin('B').getRole(),'administrator')
    def test_hadith_accessors(self):
        h=Hadith('إنما الأعمال بالنيات',{'author':'البخاري','book':'صحيح البخاري'})
        self.assertEqual(h.getText(),'إنما الأعمال بالنيات')
        self.assertEqual(h.getSource()['book'],'صحيح البخاري')
    def test_citation(self):
        h=Hadith('نص',{'author':'البخاري','book':'صحيح البخاري','page':'10'})
        result=Citation().generateFootnote(h)
        self.assertIn('البخاري',result)
        self.assertIn('ص 10',result)
    def test_missing_source(self):
        self.assertIn('unavailable',Citation().generateFootnote(Hadith('نص')).lower())
    def test_search_sequence(self):
        fake=[{'id':1,'passage':'إنما الأعمال بالنيات','book':'صحيح البخاري','author':'البخاري'}]
        with patch('app.uml.data.get_all',return_value=fake),patch('app.uml.data.get_book_passages',return_value=[]):
            found=UI().search('الأعمال بالنيات')
            self.assertTrue(found)
            self.assertIsInstance(found[0],Hadith)
            self.assertEqual(UI().displayResults(found)[0]['id'],1)
    def test_quote_search(self):
        fake=[{'id':2,'passage':'العلم نور','book':'كتاب','author':'مؤلف'}]
        with patch('app.uml.data.get_all',return_value=fake),patch('app.uml.data.get_book_passages',return_value=[]):
            self.assertIsInstance(Search().searchQuotation('العلم نور')[0],Quotation)
    def test_admin_authorization(self):
        with self.assertRaises(PermissionError):Admin().addHadith({'passage':'x'})
        with self.assertRaises(PermissionError):Admin().importRecords('a.csv','data')
    def test_admin_add(self):
        with patch('app.uml.service.create_hadith',return_value={'message':'ok'}) as fn:
            self.assertEqual(Admin().addHadith({'passage':'x'},authorized=True)['message'],'ok')
            fn.assert_called_once()
    def test_admin_import(self):
        with patch('app.uml.service.import_catalog',return_value={'count':1}):
            self.assertEqual(Admin().importRecords('a.csv','data',authorized=True)['count'],1)
if __name__=='__main__':unittest.main()
