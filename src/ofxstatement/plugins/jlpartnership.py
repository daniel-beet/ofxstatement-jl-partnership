import csv
import re
from datetime import datetime

from ofxstatement import statement
from ofxstatement.exceptions import ParseError
from ofxstatement.parser import CsvStatementParser, StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import StatementLine


class JLPartnershipPlugin(Plugin):
    """John Lewis Partnership Credit Card Plugin
    """
    def get_parser(self, filename):
        f = open(filename,
                 'r',
                 encoding=self.settings.get("charset", "utf-8-sig"))
        parser = JLPartnershipParser(f)

        parser.statement.currency = self.settings.get('currency', 'GBP')
        parser.statement.bank_id = self.settings.get('bank',
                                                     'John Lewis Finance')
        parser.statement.account_id = self.settings.get('account', '')

        return parser


class JLPartnershipParser(CsvStatementParser):
    statement_year = datetime.now().year
    date_pattern = re.compile(r'(?i)^(\d{2})-([A-Z]+)-(\d{4})$')
    url_domain_pattern = re.compile(
        r'(?:https?://)?(?:www\.)?(?:\w+\.)+\w{2,}')
    date_format = "%d-%b-%Y"  # example 22 Apr 2018
    mappings = {'date': 0, 'payee': 1, 'amount': 2, 'memo': 1}

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """

        stmt = super(JLPartnershipParser, self).parse()
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """

        reader = csv.reader(self.fin)
        statement_date = datetime.now()
        self.statement_year = statement_date.year
        csv_headers = next(reader, None)
        print(csv_headers)
        if not csv_headers == ["Date", "Description", "Amount"]:
            raise ParseError(3, "Invalid CSV file, missing expected headers")

        return reader

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """

        # ignore blank dates (for pending transactions line)
        if line[0] == "":
            return None

        # append the statement year for the times only the day and month are in csv
        if self.date_pattern.match(line[0]) == None:
            line[0] += " " + str(self.statement_year)
        # Convert case of description to something more pleasent for use as memo and payee
        description = line[1].title()
        # Correct the amount
        line[2] = line[2].replace('£', '').replace(',', '').replace(' ', '')
        if line[2][0] == "+":
            line[2] = line[2][1:]  # skip leading "+"
        else:
            line[2] = "-" + line[2]

        record = super(JLPartnershipParser, self).parse_record(line)
        record.trntype = 'DEBIT' if record.amount < 0 else 'CREDIT'
        # Convert URLs to lowercase
        description = self.url_domain_pattern.sub(lambda m: m.group().lower(),
                                                  description)

        if len(description) == 40:
            # Take the first 22 chars as the Payee
            record.payee = self.collapse_whitespace(description[0:22].strip())
            # rest is the memo
            record.memo = self.collapse_whitespace(description[23:].strip())
        # Handle the direct debit credit payment
        if line[1] == "DIRECT DEBIT TRANSACTION":
            record.payee = self.statement.bank_id
            record.memo = description.strip().lower().capitalize()

        # Special handling for John Lewis, Waitrose and johnlewis.com
        # which you will probably shop at if you have this card
        # Amazon as well, as why not?
        canonicalPayee = record.payee.strip().lower()
        if canonicalPayee == "www.johnlewis.com":
            record.memo = record.payee + " " + record.memo
            record.payee = "John Lewis"
        elif canonicalPayee.startswith("waitrose "):
            record.memo = record.payee + " " + record.memo
            record.payee = "Waitrose"
        elif (canonicalPayee.startswith("amzn ")
              or canonicalPayee.startswith("amazon")
              or canonicalPayee.startswith("kindle svcs")):
            record.memo = record.payee + " " + record.memo
            record.payee = "Amazon"

        return record

    def collapse_whitespace(self, value):
        return ' '.join(value.split())
