from django.http import JsonResponse
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic import mail


def unsubscribe_(request, feed, unsubscribe_code):
    """
    There is no authentication required to unsubscribe. Anyone can with the right code and feed.

    :param request:
    :param feed:
    :param unsubscribe_code:
    :return:
    """
    return JsonResponse(mail.unsubscribe(feed, unsubscribe_code), encoder=JSEncoder, safe=True)
