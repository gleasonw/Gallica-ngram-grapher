from unittest import TestCase
from date import Date


class TestDate(TestCase):

    def test_get_date(self):
        fullDate = Date("1800-04-02")
        anotherFullDate = Date("1800-04-02")
        yearMon = Date("1800-09")
        yearSingleDigitMon = Date("1888-1")
        year = Date("1912")
        nonsense = Date("12??")
        moreNonsense = Date("")
        self.assertEqual(
            fullDate.getDate(),
            ['1800', '04', '02']
        )
        self.assertEqual(
            anotherFullDate.getDate(),
            ['1800', '04', '02']
        )
        self.assertEqual(
            yearMon.getDate(),
            ['1800', '09', None]
        )
        self.assertEqual(
            yearSingleDigitMon.getDate(),
            ['1888', '1', None]
        )
        self.assertEqual(
            year.getDate(),
            ['1912', None, None]
        )
        self.assertEqual(
            nonsense.getDate(),
            [None, None, None]
        )
        self.assertEqual(
            moreNonsense.getDate(),
            [None, None, None]
        )