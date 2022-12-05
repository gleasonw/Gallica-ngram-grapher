from unittest.mock import MagicMock
import unittest
from gallicaGetter.parse.periodRecords import PeriodOccurrenceRecord


class TestGroupedCountRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.testRecord = PeriodOccurrenceRecord(
            date=MagicMock(
                getYear=MagicMock(return_value=2020),
                getMonth=MagicMock(return_value=1),
                getDay=MagicMock(return_value=1)
            ),
            count=1,
            term='test',
            ticketID='testticketid',
            requestID='testrequestid'
        )

    def test_getRow(self):
        row = self.testRecord.get_row()
        self.assertEqual(
            row,
            (2020, 1, 1, 'test', 'testticketid', 'testrequestid', 1)
        )


if __name__ == '__main__':
    unittest.main()
