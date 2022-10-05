from abstractFactory import AbstractFactory
import time
import psutil
from papersearchrunner import PaperSearchRunner
from parseFactory import buildParser
from fetchComponents.concurrentfetch import ConcurrentFetch
from schemaLinkForSearch import SchemaLinkForSearch
from utils.psqlconn import PSQLconn
from paperQueryFactory import PaperQueryFactory


def runTests():
    ticket = getSearchOneTermInOnePaperOverRange()

    try:
        doTest(ticket)
    except Exception as e:
        print("Test failure.")
        raise


def doTest(ticket):
    testRequestFactory = AbstractFactory(ticket, '45')
    testRequest = testRequestFactory.buildRequest()
    testRequest.start()
    while not testRequest.state == 'COMPLETED':
        print(psutil.Process().memory_info().rss / 1024 / 1024)
        print(testRequest.ticketProgressStats)
        print(testRequest.state)
        time.sleep(1)


def getSearchOneTermInOnePaperOverRange():
    testTicket = {
        0: {
            'terms': ['brazza'],
            'codes': ['cb328066631'],
            'dateRange': ['',''],
            'linkTerm': None,
            'linkDistance': None
        }
    }
    return testTicket


def getAllPapers():
    parse = buildParser()
    sruFetcher = ConcurrentFetch('https://gallica.bnf.fr/SRU')
    dbLink = SchemaLinkForSearch(
        requestID='',
        conn=PSQLconn().getConn()
    )
    paperSearch = PaperSearchRunner(
        parse=parse,
        paperQueryFactory=PaperQueryFactory(),
        sruFetch=sruFetcher,
        arkFetch=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
        addPapersToDB=dbLink.insertRecordsIntoPapers
    )
    paperSearch.addAllFetchableRecordsToDB()


if __name__ == '__main__':
    runTests()
