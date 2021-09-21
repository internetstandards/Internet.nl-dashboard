# SPDX-License-Identifier: Apache-2.0
from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import \
    sum_internet_nl_scores_over_rating


def test_sum_internet_nl_scores_over_rating():
    # a normal calculation:
    calculation = {
        "urls": [
            {"url": "acc.dashboard.internet.nl", "endpoints": [
                {"id": 4959,
                 "ratings": [
                     {"type": "internet_nl_web_overall_score",
                      "explanation": "80 https://batch.internet.nl/site/acc.dashboard.internet.nl/200719/"}]
                 }
            ]
            },
            {"url": "acc.dashboard.internet.nl", "endpoints": [
                {"id": 4959,
                 "ratings": [
                     {"type": "internet_nl_web_overall_score",
                      "explanation": "20 https://batch.internet.nl/site/acc.dashboard.internet.nl/200719/"}]
                 }
            ]
            }]}

    assert sum_internet_nl_scores_over_rating(calculation) == 50

    # a calculation with error:
    # a normal calculation:
    calculation = {
        "urls": [
            {"url": "acc.dashboard.internet.nl", "endpoints": [
                {"id": 4959,
                 "ratings": [
                     {"type": "internet_nl_web_overall_score",
                      "explanation": "error https://batch.internet.nl/site/acc.dashboard.internet.nl/200719/"}]
                 }
            ]
            },
            {"url": "acc.dashboard.internet.nl", "endpoints": [
                {"id": 4959,
                 "ratings": [
                     {"type": "internet_nl_web_overall_score",
                      "explanation": "20 https://batch.internet.nl/site/acc.dashboard.internet.nl/200719/"}]
                 }
            ]
            }]}

    assert sum_internet_nl_scores_over_rating(calculation) == 20

    # and no value at all:
    assert sum_internet_nl_scores_over_rating({'urls': []}) == 0
    assert sum_internet_nl_scores_over_rating({}) == 0
