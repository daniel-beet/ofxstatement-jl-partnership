from typing import Dict, Optional, Any, Iterable, List, TextIO, TypeVar, Generic
import csv
import re
from datetime import datetime
from typing import Iterable
from hashlib import sha256

from ofxstatement import statement
from ofxstatement.exceptions import ParseError
from ofxstatement.parser import CsvStatementParser, StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine


class JLPartnershipPlugin(Plugin):
    """John Lewis Partnership Credit Card Plugin"""

    def get_parser(self, filename: str) -> "JLPartnershipParser":
        return JLPartnershipParser(
            filename,
            self.settings.get("charset", "utf-8-sig"),
            self.settings.get("currency", "GBP"),
            self.settings.get("bank", "John Lewis Finance"),
            self.settings.get("account", ""),
        )


class JLPartnershipParser(CsvStatementParser):
    statement_year = datetime.now().year
    date_pattern = re.compile(r"(?i)^(\d{2})-([A-Z]+)-(\d{4})$")
    url_domain_pattern = re.compile(r"(?:https?://)?(?:www\.)?(?:\w+\.)+\w{2,}")
    date_format = "%d-%b-%Y"  # example 22 Apr 2018
    mappings = {"date": 0, "payee": 1, "amount": 2, "memo": 1}

    def __init__(
        self, filename: str, encoding: str, currency: str, bank_id: str, account_id: str
    ) -> None:
        super().__init__(
            open(
                filename,
                "rt",
                encoding=encoding,
                newline="",  # As recommended in doc of csv module
            )
        )
        self.statement.currency = currency
        self.statement.bank_id = bank_id
        self.statement.account_id = account_id
        statement_date = datetime.now()
        self.statement_year = statement_date.year

    def parse(self) -> Statement:
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        stmt = super(JLPartnershipParser, self).parse()
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self) -> Iterable[List[str]]:
        """Return iterable object consisting of a line per transaction"""

        try:
            header_line = self.fin.readline()
            header_reader = csv.reader([header_line])
            csv_headers = next(header_reader, None)
            if not csv_headers == ["Date Processed", "Description", "Amount", ""]:
                raise ParseError(3, "Invalid CSV file, missing expected headers")
            reader = csv.reader(self.fin)
            yield from reader
        finally:
            self.fin.close()

    def parse_record(self, line: List[str]) -> Optional[StatementLine]:
        """Parse given transaction line and return StatementLine object"""

        # ignore blank dates (for pending transactions line)
        if line[0] == "":
            return None

        if line[0] == "Pending":
            line[0] = datetime.now().strftime(self.date_format)
        # append the statement year for the times only the day and month are in csv
        if self.date_pattern.match(line[0]) == None:
            line[0] += " " + str(self.statement_year)
        # Convert case of description to something more pleasent for use as memo and payee
        description = line[1].title()
        # Correct the amount
        line[2] = line[2].replace("£", "").replace(",", "").replace(" ", "")
        if line[2][0] == "+":
            line[2] = line[2][1:]  # skip leading "+"
        else:
            line[2] = "-" + line[2]

        record = super(JLPartnershipParser, self).parse_record(line)
        if not record:
            return None
        record.trntype = "DEBIT" if record.amount < 0 else "CREDIT"
        # Convert URLs to lowercase
        description = self.url_domain_pattern.sub(
            lambda m: m.group().lower(), description
        )

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
        elif canonicalPayee.startswith("waitrose"):
            record.memo = record.payee + " " + record.memo
            record.payee = "Waitrose"
        elif (
            canonicalPayee.startswith("amzn")
            or canonicalPayee.startswith("amazon")
            or canonicalPayee.startswith("kindle svcs")
        ):
            record.memo = record.payee + " " + record.memo
            record.payee = "Amazon"
        
        if (record.payee == record.memo):
            record.memo = ""

        hash = sha256()
        hash.update(str(record.date).encode("utf-8"))
        hash.update(record.payee.encode("utf-8"))
        hash.update(record.memo.encode("utf-8"))
        hash.update(str(record.amount).encode("utf-8"))

        # Shorten the hash to the first 16 digits just to make it more
        # manageable. It should still be enough.
        record.id = str(abs(int(hash.hexdigest(), 16)))[:16]

        return record

    def collapse_whitespace(self, value):
        return " ".join(value.split())
