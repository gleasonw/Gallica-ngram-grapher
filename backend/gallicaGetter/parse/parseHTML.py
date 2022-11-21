from bs4 import BeautifulSoup


def parse_html(htmlData):
    return ParsedGallicaHTML(htmlData)


class ParsedGallicaHTML:

    def __init__(self, htmlData):
        self.html = htmlData
        self.soup = BeautifulSoup(htmlData, 'html.parser')
        self.text = ''
        self.ocrQuality = None

    def __repr__(self):
        return f'ParsedGallicaHTML({self.soup.title.string})'

    def get_text(self) -> str:
        if not self.text:
            hr_break_before_paras = self.soup.find('hr')
            if hr_break_before_paras:
                item_paras = hr_break_before_paras.find_next_siblings('p')
                self.text = '\n'.join([para.text for para in item_paras])
        return self.text

    def get_ocr_quality(self) -> int:
        if self.ocrQuality is None:
            ocrPara = self.soup.find('hr').find_previous_sibling('p').text
            if ocrPara[-6:-3].isdigit():
                self.ocrQuality = int(ocrPara[-6:-3])
            elif ocrPara[-5:-3].isdigit():
                self.ocrQuality = int(ocrPara[-5:-3])
            elif ocrPara[-4:-3].isdigit():
                self.ocrQuality = int(ocrPara[-4:-3])
            else:
                self.ocrQuality = 0
        return self.ocrQuality
