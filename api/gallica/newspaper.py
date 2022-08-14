import concurrent.futures
import io

from requests_toolbelt import sessions
from gallica.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from gallica.db import DB

from gallica.gallicaRecordBatch import GallicaPaperRecordBatch


class Newspaper:

    #TODO: split into multiple classes
    def __init__(self, gallicaSession=None):
        self.query = ''
        self.papersSimilarToKeyword = []
        self.paperRecords = []
        self.dbConnection = DB().getConn()
        if not gallicaSession:
            self.initGallicaSession()
        else:
            self.session = gallicaSession

    def sendTheseGallicaPapersToDB(self, paperCodes):
        with self.session:
            self.fetchPapersDataInBatches(paperCodes)
        self.copyPapersToDB()

    def fetchPapersDataInBatches(self, paperCodes):
        for i in range(0, len(paperCodes), 20):
            batchOf20 = self.fetchTheseMax20PaperRecords(paperCodes[i:i + 20])
            self.paperRecords.extend(batchOf20)

    def fetchTheseMax20PaperRecords(self, paperCodes):
        formattedPaperCodes = [f"{paperCode[0]}_date" for paperCode in paperCodes]
        self.query = 'arkPress all "' + '" or arkPress all "'.join(formattedPaperCodes) + '"'
        batch = GallicaPaperRecordBatch(
            self.query,
            self.session,
            numRecords=20)
        return batch.getRecords()

    def sendAllGallicaPapersToDB(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        self.fetchAllPapersFromGallica()
        self.copyPapersToDB()
        self.dbConnection.close()

    def fetchAllPapersFromGallica(self):
        with self.session:
            numPapers = self.getNumPapersOnGallica()
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                for batch in executor.map(
                        self.fetchBatchPapersAtIndex,
                        range(1, numPapers, 50)):
                    self.paperRecords.extend(batch)

    def fetchBatchPapersAtIndex(self, index):
        batch = GallicaPaperRecordBatch(
            self.query,
            self.session,
            startRecord=index)
        records = batch.getRecords()
        return records

    def getNumPapersOnGallica(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        tempBatch = GallicaPaperRecordBatch(
            self.query,
            self.session,
            numRecords=1)
        numResults = tempBatch.getNumResults()
        return numResults

    def copyPapersToDB(self):
        with self.dbConnection.cursor() as curs:
            csvStream = self.generateCSVstream()
            curs.copy_from(csvStream, 'papers', sep='|')

    def generateCSVstream(self):

        def cleanCSVvalue(value):
            if value is None:
                return r'\N'
            return str(value).replace('|', '\\|')

        csvFileLikeObject = io.StringIO()
        for paperRecord in self.paperRecords:
            dateRange = paperRecord.getDate()
            lowYear = dateRange[0]
            highYear = dateRange[1]
            csvFileLikeObject.write('|'.join(map(cleanCSVvalue, (
                paperRecord.getPaperTitle(),
                lowYear,
                highYear,
                paperRecord.isContinuous(),
                paperRecord.getPaperCode()
            ))) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject
#TODO: return the paper's publishing years alongside the title
    def getPapersSimilarToKeyword(self, keyword):
        with self.dbConnection.cursor() as curs:
            keyword = keyword.lower()
            curs.execute("""
                SELECT title, code
                    FROM papers 
                    WHERE LOWER(title) LIKE %(paperNameSearchString)s
                    ORDER BY title LIMIT 20;
            """, {'paperNameSearchString': '%' + keyword + '%'})
            self.papersSimilarToKeyword = curs.fetchall()
            return self.nameCodeDataToJSON()

    def nameCodeDataToJSON(self):
        namedPaperCodes = []
        for paperTuple in self.papersSimilarToKeyword:
            paper = paperTuple[0]
            code = paperTuple[1]
            namedPair = {'paper': paper, 'code': code}
            namedPaperCodes.append(namedPair)
        return {'paperNameCodes': namedPaperCodes}

    def initGallicaSession(self):
        self.session = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter()
        self.session.mount("https://", adapter)


if __name__ == '__main__':
    newspaper = Newspaper()
    newspaper.sendAllGallicaPapersToDB()
