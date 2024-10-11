import unittest
from utils.date_utils import convert_to_db_date, is_valid_date, get_current_date

class TestDateUtils(unittest.TestCase):
    def test_convert_to_db_date(self):
        self.assertEqual(convert_to_db_date("01/12/2023"), "2023-12-01")
        self.assertEqual(convert_to_db_date("31/03/2022"), "2022-03-31")
        self.assertIsNone(convert_to_db_date("invalid_date"))

    def test_is_valid_date(self):
        self.assertTrue(is_valid_date("01/12/2023"))
        self.assertTrue(is_valid_date("31/03/2022"))
        self.assertFalse(is_valid_date("32/01/2023"))
        self.assertFalse(is_valid_date("invalid_date"))

    def test_get_current_date(self):
        import datetime
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        self.assertEqual(get_current_date(), current_date)

if __name__ == '__main__':
    unittest.main()