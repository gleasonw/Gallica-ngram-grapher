import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from arkRecord import ArkRecord
from groupedCountRecord import GroupedCountRecord
from occurrenceRecord import OccurrenceRecord
from paperRecord import PaperRecord
from parseRecord import ParseArkRecord, ParseOccurrenceRecords, ParsePaperRecords


class TestParseRecord(TestCase):
    pass


class TestParseArkRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseArkRecord()

    def test_parseResponsesToRecords(self):
        testResultGenerator = self.testParse.parseResponsesToRecords(
            [
                MagicMock(),
                MagicMock(),
            ]
        )
        for testResult in testResultGenerator:
            self.assertIsInstance(testResult, ArkRecord)


class TestParseGroupedRecordCounts(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseGroupedRecordCounts(
            parser=MagicMock(),
            ticketID='test',
            requestID='test'
        )

    def test_parse(self):
        test = self.testParse.parseResponsesToRecords(
            [
                MagicMock(),
                MagicMock(),
            ]
        )
        for testResult in test:
            self.assertIsInstance(testResult, GroupedCountRecord)


class TestParseOccurrenceRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseOccurrenceRecords(
            parser=MagicMock(),
            requestID=1,
            ticketID=1
        )

    def test_parseResponsesToRecords(self):
        testResponses = [
            MagicMock(),
            MagicMock(),
        ]
        self.testParse.parser.return_value = ['test1', 'test2']
        testResults = self.testParse.parseResponsesToRecords(testResponses)
        for result in testResults:
            self.assertIsInstance(result, OccurrenceRecord)


class TestParsePaperRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParsePaperRecords(
            parser=MagicMock()
        )

    def test_parseResponsesToRecords(self):
        responses = [
            MagicMock(),
            MagicMock(),
        ]
        self.testParse.parser.getRecordsFromXML.return_value = [
            'record1',
            'record2',
        ]

        test = self.testParse.parseResponsesToRecords(responses)

        for testResult in test:
            self.assertIsInstance(testResult, PaperRecord)
