"""
Creates a number of usage metrics for the dashboard. These metrics are visible on the dashboard and create
transparency on the usage of the dashboard.

The following statistics are created:

- 55 gebruikers (totaal)
- 53 accounts (totaal)
- 816 dashboard scans uitgevoerd (2020)
- 1196 dashboard scans uitgevoerd (totaal)
- 408 lijsten met domeinen (totaal)
- 35.508 unieke domeinen (totaal)
- 1.836.648 meetpunten verzameld (totaal)
- 1.662.846 meetpunten dit jaar voor het laatst gescand en bijgewerkt (2020)

Details obv action metingen gestart eind januari 2020 (er mist bijna een maand dus):
- 534 handmatige scans
- 226 ingeplande scans
- 304 logins
- 1595 keer een rapport bekeken


"""
from collections import defaultdict
from datetime import datetime, timedelta

import pytz
from actstream.models import Action
from django.contrib.auth.models import User
from websecmap.organizations.models import Url
from websecmap.scanners.models import EndpointGenericScan

from dashboard.internet_nl_dashboard.models import AccountInternetNLScan, UrlList

DASHBOARD_EPOCH = datetime(2019, 6, 1, tzinfo=pytz.utc)


def dashboard_years() -> range:
    # range is excluding the upper bound
    return range(DASHBOARD_EPOCH.year, datetime.now(pytz.utc).year + 1)


def dashboard_months(year) -> range:
    if year == DASHBOARD_EPOCH.year:
        return range(DASHBOARD_EPOCH.month, 13)

    if year == datetime.now(pytz.utc).year:
        return range(1, datetime.now(pytz.utc).month + 1)

    return range(1, 13)


def usage_metrics():
    return {
        'users': {
            'total': User.objects.all().count(),
            'logged_in_the_past_30_days': user_logged_in_past_n_days(30),
            'logged_in_the_past_60_days': user_logged_in_past_n_days(60),
            'logged_in_the_past_90_days': user_logged_in_past_n_days(90),
            'logged_in_the_past_120_days': user_logged_in_past_n_days(120),
            'logged_in_the_past_150_days': user_logged_in_past_n_days(150),
            'logged_in_the_past_180_days': user_logged_in_past_n_days(180),
            'logged_in_the_past_210_days': user_logged_in_past_n_days(210),
            'logged_in_the_past_240_days': user_logged_in_past_n_days(240),
            'logged_in_the_past_270_days': user_logged_in_past_n_days(270),
            'logged_in_the_past_300_days': user_logged_in_past_n_days(300),
        },
        'scans': {
            'total': AccountInternetNLScan.objects.all().count(),
            'per_year': abstract_per_year(AccountInternetNLScan.objects.all(), 'started_on'),
            'per_month': abstract_per_month(AccountInternetNLScan.objects.all(), 'started_on'),
        },
        'lists': {
            'total': UrlList.objects.all().count(),
        },
        'domains': {
            'total': Url.objects.all().count(),
            # Expect this to lower over time, as these are only new unique domains.
            'per_year': abstract_per_year(Url.objects.all(), 'created_on'),
            'per_month': abstract_per_month(Url.objects.all(), 'created_on'),
        },
        'metrics': {
            'total': EndpointGenericScan.objects.all().count(),
            # Expect this to lower over time too, as the first time new metrics are measured, then only updates
            'last_scan_moment': {
                'per_year': abstract_per_year(EndpointGenericScan.objects.all(), 'last_scan_moment'),
                'per_month': abstract_per_month(EndpointGenericScan.objects.all(), 'last_scan_moment'),
            },
            'rating_determined_on': {
                'per_year': abstract_per_year(EndpointGenericScan.objects.all(), 'rating_determined_on'),
                'per_month': abstract_per_month(EndpointGenericScan.objects.all(), 'rating_determined_on'),
            }
        },
        'actions': abstract_action_total()
    }


def user_logged_in_past_n_days(days=30):
    n_days_ago = datetime.now(pytz.utc) - timedelta(days=days)
    return User.objects.all().filter(last_login__gt=n_days_ago).count()


def abstract_per_year(query, datetime_field):
    stats = {}
    for year in dashboard_years():
        kwargs = {
            f"{datetime_field}__year": year,
        }
        stats[year] = query.filter(**kwargs).count()
    return stats


def abstract_per_month(query, datetime_field):
    stats = defaultdict(dict)
    for year in dashboard_years():
        for month in dashboard_months(year):
            kwargs = {
                f"{datetime_field}__year": year,
                f"{datetime_field}__month": month,
            }
            stats[year][month] = query.filter(**kwargs).count()
    return stats


def abstract_action_total():
    verbs = list(set(Action.objects.all().values_list('verb', flat=True).order_by('verb')))
    stats = defaultdict(dict)
    for verb in verbs:
        stats[verb] = {
            'total': Action.objects.all().filter(verb=verb).count(),
            'per_year': abstract_per_year(Action.objects.all().filter(verb=verb), 'timestamp'),
            'per_month': abstract_per_month(Action.objects.all().filter(verb=verb), 'timestamp')
        }
    return stats
