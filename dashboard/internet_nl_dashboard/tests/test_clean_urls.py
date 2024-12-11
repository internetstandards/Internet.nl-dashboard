# SPDX-License-Identifier: Apache-2.0
"""
These testcases help to validate the working of the listmanagement API.

Run these tests with tox -e test -- -k test_clean_urls
"""
from dashboard.internet_nl_dashboard.logic.domains import clean_urls


def test_clean_urls() -> None:

    # domains can't contain spaces...
    result = clean_urls(["kalsndlkas.asdakj .com"])
    assert len(result["incorrect"]) == 1 and len(result["correct"]) == 0

    result = clean_urls(["apple.com"])
    assert len(result["incorrect"]) == 0 and len(result["correct"]) == 1

    result = clean_urls(["vintage.museum"])
    assert len(result["incorrect"]) == 0 and len(result["correct"]) == 1

    result = clean_urls(["subsub.sub.sub.com"])
    assert len(result["incorrect"]) == 0 and len(result["correct"]) == 1

    # warning: i don't know what the below words mean or what connotations they have.
    # probably rent.org in russian / .xn--c1avg
    # both urlparse and validators say 'no' to this.
    # should we convert to punycode?
    # todo: it's not really clear in python how to convert unicode to punycode. Searching for it does not yield results.
    result = clean_urls(["аренда.орг"])
    assert len(result["incorrect"]) == 0 and len(result["correct"]) == 1

    # = xn--o1b5efa8g5c.xn--i1b6b1a6a2e
    result = clean_urls(["मुम्बई.संगठन"])
    assert len(result["incorrect"]) == 0 and len(result["correct"]) == 1

    result = clean_urls([" ", " ⠀ ", "eskillsplatform.nl", "stichtingmediawijzer.nl", "\u200b "])
    assert len(result["incorrect"]) == 3 and len(result["correct"]) == 2
    assert result["correct"] == ["eskillsplatform.nl", "stichtingmediawijzer.nl"]
