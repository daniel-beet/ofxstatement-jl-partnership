import os

from ofxstatement.ui import UI

from ofxstatement.plugins.jlpartnership import JLPartnershipPlugin


def test_sample() -> None:
    plugin = JLPartnershipPlugin(UI(), {})
    here = os.path.dirname(__file__)
    sample_filename = os.path.join(here, "sample-statement.csv")

    parser = plugin.get_parser(sample_filename)
    statement = parser.parse()

    assert statement is not None
