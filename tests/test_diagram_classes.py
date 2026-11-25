import unittest
from unittest.mock import patch
from app.diagram_classes import UI, User, Search, TextCleaner, QueryGen, HadithVi, Getresult, Citation, Takhrij, DB

class DiagramTests(unittest.TestCase):
    def test_ten_classes(self):
        self.assertEqual(len([UI,User,Search,TextCleaner,QueryGen,HadithVi,Getresult,Citation,Takhrij,DB]),10)
    def test_clean_and_query(self):
        self.assertEqual(QueryGen().generatQuery('  hello   world  '),'hello world')
    def test_search_and_ui(self):
        row={'id':1,'passage':'إنما الأعمال بالنيات','book':'صحيح البخاري','author':'البخاري','reference':'1'}
        with patch('app.diagram_classes.data.get_all',return_value=[row]), patch('app.diagram_classes.data.get_book_passages',return_value=[]):
            result=UI().sendText('الأعمال بالنيات')
            self.assertEqual(result[0]['id'],1)
            self.assertTrue(result[0]['source_metadata_present'])
            self.assertEqual(Takhrij().names('الأعمال بالنيات'),['صحيح البخاري'])
    def test_invalid_input(self):
        with self.assertRaises(ValueError): UI().sendText('a')
if __name__ == '__main__': unittest.main()
