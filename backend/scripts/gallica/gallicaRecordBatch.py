from lxml import etree
from record import KeywordRecord
from record import PaperRecord
from scripts.utils.gallicaSession import GallicaSession

#Refactor so this is a driver passed around, rather
#than newly instantiated with each request
class GallicaRecordBatch:
    def __init__(self,
                 query,
                 session,
                 startRecord=1,
                 numRecords=50,
                 collapsing=False
                 ):
        self.batch = []
        self.query = query
        self.queryHitNumber = 0
        self.numPurgedResults = 0
        self.session = session
        self.xmlRoot = None
        self.elapsedTime = None
        self.params = {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": startRecord,
            "maximumRecords": numRecords,
            "collapsing": collapsing,
            "query": self.query,
        }
        self.fetchXML()

    def getNumResults(self):
        numResults = self.xmlRoot.find(
            "{http://www.loc.gov/zing/srw/}numberOfRecords")
        if numResults is not None:
            numResults = numResults.text
            numResults = int(numResults)
        return numResults

    def getRecords(self):
        self.parseRecordsFromXML()
        return self.batch

    # TODO: Investigate requests toolbelt threading module
    # TODO: Move to a new class focused solely on concurrent requests
    def fetchXML(self):
        response = self.session.get(
            "",
            params=self.params,
            timeout=(30, 240))
        self.xmlRoot = etree.fromstring(response.content)
        self.elapsedTime = response.elapsed.total_seconds()

    def parseRecordsFromXML(self):
        pass

    def getRandomPaper(self):
        lastPaper = self.batch[-1]
        lastPaper.parseTitleFromXML()
        lastPaperTitle = lastPaper.getPaperTitle()
        return lastPaperTitle


class GallicaKeywordRecordBatch(GallicaRecordBatch):

    def __init__(self,
                 query,
                 ticketid,
                 keyword,
                 session,
                 startRecord=1,
                 numRecords=50):
        super().__init__(
            query,
            session,
            startRecord=startRecord,
            numRecords=numRecords
        )
        self.ticketid = ticketid
        self.keyword = keyword

    def parseRecordsFromXML(self):
        for result in self.xmlRoot.iter("{http://www.loc.gov/zing/srw/}record"):
            record = KeywordRecord(
                result,
                self.ticketid,
                self.keyword
            )
            if record.isValid():
                self.batch.append(record)
            else:
                self.numPurgedResults += 1

    def recordIsUnique(self, record):
        if self.batch:
            if self.currentResultEqualsPrior(record):
                return False
        return True

    # TODO: What if the duplicate is not directly before?
    def currentResultEqualsPrior(self, record):
        priorRecord = self.batch[-1]
        if record.getDate() == priorRecord.getDate() and record.getPaperCode() == priorRecord.getPaperCode():
            return True
        else:
            return False


class GallicaPaperRecordBatch(GallicaRecordBatch):

    def __init__(
            self,
            query,
            session,
            startRecord=1,
            numRecords=50):

        super().__init__(
            query,
            session,
            startRecord=startRecord,
            numRecords=numRecords,
            collapsing=True)

    # TODO: at the end of bulk queries, run date queries for each code, so leave date unset here. One session = better, and we can better employ concurrency (get more batches of date information per request?).
    def parseRecordsFromXML(self):
        gallicaSessionForPaperYears = GallicaSession(
            "https://gallica.bnf.fr/services/Issues").getSession()
        for result in self.xmlRoot.iter(
                "{http://www.loc.gov/zing/srw/}record"):
            record = PaperRecord(
                result,
                gallicaSessionForPaperYears)
            if record.isValid():
                self.batch.append(record)
            else:
                self.numPurgedResults += 1

