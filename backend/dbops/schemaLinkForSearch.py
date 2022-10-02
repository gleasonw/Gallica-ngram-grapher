import io


class SchemaLinkForSearch:
    def __init__(self, conn, paperFetcher=None, requestID=None):
        self.conn = conn
        self.requestID = requestID
        self.fetchRecordsForTheseCodes = paperFetcher

    def insertRecordsIntoPapers(self, records):
        csvStream = self.buildCSVstream(records)
        with self.conn.cursor() as curs:
            curs.copy_from(
                csvStream,
                'papers',
                sep='|'
            )

    def insertRecordsIntoResults(self, props):
        stream, codes = self.buildCSVstreamAndGetCodes(props['records'])
        self.insertMissingPapersToDB(codes, props['onAddMissingPapers'])
        props['onAddResults']()
        with self.conn.cursor() as curs:
            curs.copy_from(
                stream,
                'results',
                sep='|',
                columns=(
                    'identifier',
                    'year',
                    'month',
                    'day',
                    'searchterm',
                    'ticketid',
                    'requestid',
                    'papercode',
                    'papertitle'
                )
            )
        props['onRemoveDuplicateRecords']()
        self.removeDuplicateRecordsInTicket(props['ticketID'])

    def insertMissingPapersToDB(self, codes, onAddMissingPapers):
        schemaMatches = self.getPaperCodesThatMatch(codes)
        setOfCodesInDB = set(match[0] for match in schemaMatches)
        missingCodes = codes - setOfCodesInDB
        if missingCodes:
            onAddMissingPapers()
            paperRecords = self.fetchRecordsForTheseCodes(list(missingCodes))
            self.insertRecordsIntoPapers(paperRecords)

    def getPaperCodesThatMatch(self, codes):
        with self.conn.cursor() as curs:
            curs.execute(
                'SELECT code FROM papers WHERE code IN %s',
                (tuple(codes),)
            )
            return curs.fetchall()

    def buildCSVstreamAndGetCodes(self, records):
        csvFileLikeObject = io.StringIO()
        codes = set()
        for record in records:
            codes.add(record.paperCode)
            self.writeToCSVstream(csvFileLikeObject, record)
        csvFileLikeObject.seek(0)
        return csvFileLikeObject, codes

    def buildCSVstream(self, records):
        csvFileLikeObject = io.StringIO()
        for record in records:
            self.writeToCSVstream(csvFileLikeObject, record)
        csvFileLikeObject.seek(0)
        return csvFileLikeObject

    def writeToCSVstream(self, stream, record):
        stream.write("|".join(map(
            self.cleanCSVrow,
            record.getRow()
        )) + '\n')

    def removeDuplicateRecordsInTicket(self, ticketID):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                WITH ticketRecords AS (
                    SELECT ctid, year, month, day, papertitle, searchterm, ticketid, requestid
                    FROM results
                    WHERE ticketid = %s
                    AND requestid = %s
                )
                DELETE FROM results a USING (
                    SELECT MIN(ctid) as ctid, year, month, day, papertitle, searchterm, ticketid, requestid
                    FROM ticketRecords
                    GROUP BY year, month, day, papertitle, searchterm, ticketid, requestid
                    HAVING COUNT(*) > 1
                ) b
                WHERE a.requestid = b.requestid
                AND a.ticketid = b.ticketid
                AND a.year = b.year
                AND (a.month = b.month OR (a.month IS NULL AND b.month IS NULL))
                AND (a.day = b.day OR (a.day IS NULL AND b.day IS NULL))
                AND a.papertitle = b.papertitle
                AND a.searchterm = b.searchterm
                AND a.ctid <> b.ctid;
                """,
                (ticketID, self.requestID,)
            )

    def cleanCSVrow(self, value):
        if value is None:
            return r'\N'
        return str(value).replace('|', '\\|')

    def getNumResultsForTicket(self, ticketID):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                SELECT COUNT(*) 
                FROM results 
                WHERE ticketid = %s
                AND requestid = %s
                """,
                (ticketID,self.requestID,)
            )
            return curs.fetchone()[0]

