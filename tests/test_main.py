from decimal import Decimal
from argparse import Namespace

import pytest
import hashlib
from bittytax.audit import AuditRecords
from bittytax.report import ReportLog
from bittytax.main import do_each_tax_year, do_tax, do_import


class TestMain:

    @staticmethod
    def args(filename, taxyear=None, summary=None, tax_rules='UK_INDIVIDUAL'):
        return Namespace(filename=filename, taxyear=taxyear, summary=summary, tax_rules=tax_rules)

    @pytest.mark.parametrize("filename, tax_rules, expected_cost, hexdigest",
                             [("resources/example.csv", "UK_INDIVIDUAL", "126527.46",
                              "eacfd6760f27f81397f7e3cd63469b68b72d1a401a3be19b4cd731da1b88b5bf"),
                              ("resources/example.xlsx", "UK_INDIVIDUAL", "126527.46",
                              "ac7d17588d8d9876dfd9a9fa980118fec7573a65fc1fc5cd90fd2a735639f41d")
                              ])
    def test_do_import(self, filename, tax_rules, expected_cost, hexdigest):
        """ I am only checking that transaction records' hash and cost have the expected values.
        I reckon this is not ideal but being at the early staging of testing that at least proves that nothing is broken
         """
        m = hashlib.sha256()
        transaction_records = do_import(filename)

        assert len(transaction_records) == 60

        for transaction in transaction_records:
            m.update(transaction.__str__().encode('utf-8'))
        assert m.hexdigest() == hexdigest

        audit = AuditRecords(transaction_records)
        tax, value_asset = do_tax(transaction_records, tax_rules, True)
        do_each_tax_year(tax, False, None, value_asset)
        log = ReportLog(audit,
                        tax.tax_report,
                        value_asset.price_report,
                        tax.holdings_report,
                        TestMain.args(filename, tax_rules=tax_rules))
        assert log.holdings_report.get("totals").get("cost") == Decimal(expected_cost)
