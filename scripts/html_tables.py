"""Small, offline HTML table reader; math annotations are duplicate renderings."""
from html.parser import HTMLParser


class Tables(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None
        self.skip = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "annotation":
            self.skip += 1
        if tag == "table":
            self.table = []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = []

    def handle_data(self, text):
        if self.cell is not None and not self.skip:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if tag == "annotation":
            self.skip -= 1
        if tag in ("td", "th") and self.cell is not None:
            if self.row is not None:
                self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.table is not None:
                self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None
