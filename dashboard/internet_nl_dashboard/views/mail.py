# SPDX-License-Identifier: Apache-2.0

from dashboard.internet_nl_dashboard.logic import mail
from dashboard.internet_nl_dashboard.views import json_response


def unsubscribe_(request, feed, unsubscribe_code):
    """
    There is no authentication required to unsubscribe. Anyone can with the right code and feed.

    :param request:
    :param feed:
    :param unsubscribe_code:
    :return:
    """
    return json_response(mail.unsubscribe(feed, unsubscribe_code))
