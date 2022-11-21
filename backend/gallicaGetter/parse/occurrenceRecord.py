class OccurrenceRecord:

    def __init__(
            self,
            paperTitle,
            paperCode,
            url,
            date,
            term,
            ticketID,
            requestID
    ):
        self.url = url
        self.date = date
        self.paperTitle = paperTitle
        self.paperCode = paperCode
        self.term = term
        self.ticketID = ticketID
        self.requestID = requestID

    def get_date(self):
        return self.date

    def get_paper_code(self):
        return self.paperCode

    def get_volume_code(self):
        return self.url.split('/')[-1]

    def __repr__(self):
        return f'OccurrenceRecord({self.term}, {self.paperTitle}, {self.url}, {self.date})'

    def getRow(self):
        row = [
            self.url,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.term,
        ]
        self.ticketID and row.append(self.ticketID)
        self.requestID and row.append(self.requestID)
        row.append(self.paperCode)
        row.append(self.paperTitle)
        return tuple(row)

    def getDisplayRow(self):
        return (
            self.term,
            self.paperTitle,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.url
        )
