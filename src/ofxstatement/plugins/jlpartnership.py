import csv
import re
from datetime import datetime

from ofxstatement import statement
from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.parser import StatementParser
from ofxstatement.statement import StatementLine


class JLPartnershipPlugin(Plugin):
    """John Lewis Partnership Credit Card Plugin
    """

    def get_parser(self, filename):
        f = open(filename, 'r', encoding=self.settings.get(
            "charset", "ISO-8859-1"))
        parser = JLPartnershipParser(f)
        return parser


class JLPartnershipParser(CsvStatementParser):
    statement_year = datetime.now().year
    date_pattern = re.compile(r'(?i)^(\d{2}) ([A-Z]+) (\d{4})$')
    url_domain_pattern = re.compile(
        r'(?:https?://)?(?:www\.)?(?:\w+\.)+\w{2,}')
    date_format = "%d %b %Y"
    mappings = {
        'date': 0,
        'payee': 1,
        'amount': 2,
        'memo': 1
    }

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """

        self.statement.currency = "GBP"

        stmt = super(JLPartnershipParser, self).parse()
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """

        reader = csv.reader(self.fin)
        next(reader, None)  # skip title line
        statement_date = next(reader, None)[1]  # skip statement date
        self.statement_year = datetime.strptime(
            statement_date, "%d %B %Y").year
        next(reader, None)  # skip cvs header row
        next(reader, None)
        return reader

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """

        # append the statement year for the times only the day and month are in csv
        if (self.date_pattern.match(line[0]) == None):
            line[0] += " " + str(self.statement_year)
        # Convert case of description to something more pleasent for use as memo and payee
        description = line[1].title()
        # Correct the amount
        if(line[3] == "CR"):
            line[2] = line[2][1:]
        else:
            line[2] = "-" + line[2][1:]

        stmtline = super(JLPartnershipParser, self).parse_record(line)
        stmtline.trntype = 'DEBIT' if stmtline.amount < 0 else 'CREDIT'
        # Convert URLs to lowercase
        description = self.url_domain_pattern.sub(
            lambda m: m.group().lower(), description)

        if(len(description) == 40):
            # Take the first 22 chars as the Payee
            stmtline.payee = self.collapse_whitespace(
                description[0:22].strip())
            # rest is the memo
            stmtline.memo = self.collapse_whitespace(description[23:].strip())

        return stmtline

    def collapse_whitespace(self, value):
        return ' '.join(value.split())
