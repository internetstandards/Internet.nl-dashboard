# SPDX-License-Identifier: Apache-2.0
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
from datetime import date, datetime, timedelta, timezone
from hashlib import sha1
from typing import Any, Dict

from actstream.models import Action
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Count, Min, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from ninja import Schema
from websecmap.organizations.models import Url
from websecmap.scanners.models import EndpointGenericScan

from dashboard.internet_nl_dashboard.models import AccountInternetNLScan, UrlList

# DASHBOARD_EPOCH = datetime(2019, 6, 1, tzinfo=timezone.utc)
DASHBOARD_EPOCH = datetime(2023, 1, 1, tzinfo=timezone.utc)
CACHE_TIMEOUT_ONE_DAY = 60 * 60 * 24
USAGE_CACHE_VERSION = "v2"
KNOWN_ACTION_VERBS = {
    "cancelled scan",
    "created list",
    "deleted list",
    "retrieved domain lists",
    "updated list",
    "uploaded spreadsheet",
    "viewed report",
}


class UsageMetricsSchema(Schema):
    users: Dict[str, int]
    scans: Dict[str, Any]
    lists: Dict[str, int]
    domains: Dict[str, Any]
    metrics: Dict[str, Any]
    actions: Dict[str, Any]


class ActionVerbStatisticsSchema(Schema):
    # Total number of action rows for this verb across all time in the table.
    total: int
    # Pivot by year for this verb: {"2024": 12, "2025": 40, ...}
    per_year: Dict[str, int]
    # Pivot by month inside each year for this verb:
    # {"2025": {"1": 2, "2": 0, ..., "12": 6}, "2026": {"1": 20, "2": 0, ...}}
    per_month: Dict[str, Dict[str, int]]


class ActionStatisticsSchema(Schema):
    # Years available in the result window (start year through current year).
    years: list[str]
    # All verbs included in the result (known verbs + verbs found in the activity stream table).
    verbs: list[str]
    # Multiple action groups keyed by verb name.
    # Example: actions["viewed report"].per_month["2026"]["1"] == 20
    actions: Dict[str, ActionVerbStatisticsSchema]


class UserStatisticsInputSchema(Schema):
    start_date: date | None = None
    end_date: date | None = None
    max_records: int = 10


class ActorVerbStatisticsSchema(Schema):
    actor_content_type_id: int
    actor_object_id: str
    actor: str
    total_actions: int
    total_distinct_verbs: int
    verbs: Dict[str, int]


class UserStatisticsSchema(Schema):
    start_date: str
    end_date: str
    max_records: int
    actors: list[ActorVerbStatisticsSchema]


def dashboard_years() -> range:
    # range is excluding the upper bound
    return range(DASHBOARD_EPOCH.year, datetime.now(timezone.utc).year + 1)


def dashboard_months(year) -> range:
    if year == DASHBOARD_EPOCH.year:
        return range(DASHBOARD_EPOCH.month, 13)

    if year == datetime.now(timezone.utc).year:
        return range(1, datetime.now(timezone.utc).month + 1)

    return range(1, 13)


def usage_metrics():
    now = datetime.now(timezone.utc)
    login_windows = [1, 7, 14, 30, 90, 180, 365]
    users_aggregate_kwargs = {
        "total": Count("id"),
    }
    for days in login_windows:
        users_aggregate_kwargs[f"logged_in_the_past_{days}_days"] = Count(
            "id",
            filter=Q(last_login__gt=now - timedelta(days=days)),
        )
    users = User.objects.aggregate(**users_aggregate_kwargs)

    return {
        "users": {
            "total": users["total"],
            "logged_in_the_past_1_days": users["logged_in_the_past_1_days"],
            "logged_in_the_past_7_days": users["logged_in_the_past_7_days"],
            "logged_in_the_past_14_days": users["logged_in_the_past_14_days"],
            "logged_in_the_past_30_days": users["logged_in_the_past_30_days"],
            "logged_in_the_past_90_days": users["logged_in_the_past_90_days"],
            "logged_in_the_past_180_days": users["logged_in_the_past_180_days"],
            "logged_in_the_past_365_days": users["logged_in_the_past_365_days"],
        },
        "scans": {
            "total": AccountInternetNLScan.objects.all().count(),
            "per_year": abstract_per_year(AccountInternetNLScan.objects.all(), "started_on"),
            "per_month": abstract_per_month(AccountInternetNLScan.objects.all(), "started_on"),
        },
        "lists": {
            "total": UrlList.objects.all().count(),
        },
        "domains": {
            "total": Url.objects.all().count(),
            # Expect this to lower over time, as these are only new unique domains.
            "per_year": abstract_per_year(Url.objects.all(), "created_on"),
            "per_month": abstract_per_month(Url.objects.all(), "created_on"),
        },
        "metrics": {
            "total": EndpointGenericScan.objects.all().count(),
            # Expect this to lower over time too, as the first time new metrics are measured, then only updates
            # "last_scan_moment": {
            #     "per_year": abstract_per_year(EndpointGenericScan.objects.all(), "last_scan_moment"),
            #     "per_month": abstract_per_month(EndpointGenericScan.objects.all(), "last_scan_moment"),
            # },
            # "rating_determined_on": {
            #     "per_year": abstract_per_year(EndpointGenericScan.objects.all(), "rating_determined_on"),
            #     "per_month": abstract_per_month(EndpointGenericScan.objects.all(), "rating_determined_on"),
            # },
        },
        "actions": abstract_action_total(),
    }


def user_logged_in_past_n_days(days=30):
    n_days_ago = datetime.now(timezone.utc) - timedelta(days=days)
    return User.objects.all().filter(last_login__gt=n_days_ago).count()


def abstract_per_year(query, datetime_field):
    query_hash = sha1(str(query.query).encode("utf-8")).hexdigest()  # nosec (hashing, not security)
    cache_key = (
        f"usage:{USAGE_CACHE_VERSION}:per_year:{query.model._meta.label_lower}:{datetime_field}:{DASHBOARD_EPOCH.year}"
        f":{query_hash}"
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    years = list(dashboard_years())
    stats = {str(year): 0 for year in years}
    valid_years = set(years)

    rows = (
        query.exclude(**{f"{datetime_field}__isnull": True})
        .annotate(_year=ExtractYear(datetime_field))
        .values("_year")
        .annotate(total=Count("id"))
    )
    for row in rows:
        year = row.get("_year")
        if year in valid_years:
            stats[str(year)] = row["total"]

    cache.set(cache_key, stats, timeout=CACHE_TIMEOUT_ONE_DAY)
    return stats


def abstract_per_month(query, datetime_field):
    query_hash = sha1(str(query.query).encode("utf-8")).hexdigest()  # nosec (hashing, not security)
    cache_key = (
        f"usage:{USAGE_CACHE_VERSION}:per_month:{query.model._meta.label_lower}:{datetime_field}:{DASHBOARD_EPOCH.year}"
        f":{query_hash}"
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    years = list(dashboard_years())
    valid_months_per_year = {year: set(dashboard_months(year)) for year in years}
    stats: Dict[Any, Any] = {str(year): {str(month): 0 for month in dashboard_months(year)} for year in years}

    rows = (
        query.exclude(**{f"{datetime_field}__isnull": True})
        .annotate(_year=ExtractYear(datetime_field), _month=ExtractMonth(datetime_field))
        .values("_year", "_month")
        .annotate(total=Count("id"))
    )
    for row in rows:
        year = row.get("_year")
        month = row.get("_month")
        if year in valid_months_per_year and month in valid_months_per_year[year]:
            stats[str(year)][str(month)] = row["total"]

    cache.set(cache_key, stats, timeout=CACHE_TIMEOUT_ONE_DAY)
    return stats


def abstract_action_total():
    cache_key = f"usage:{USAGE_CACHE_VERSION}:actions:{DASHBOARD_EPOCH.year}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    years = list(dashboard_years())
    valid_years = set(years)
    valid_months_per_year = {year: set(dashboard_months(year)) for year in years}
    empty_per_year = {str(year): 0 for year in years}
    empty_per_month = {str(year): {str(month): 0 for month in dashboard_months(year)} for year in years}

    totals = Action.objects.all().values("verb").annotate(total=Count("id")).order_by("verb")
    stats: Dict[Any, Any] = {}
    for row in totals:
        verb = row["verb"]
        stats[verb] = {
            "total": row["total"],
            "per_year": dict(empty_per_year),
            "per_month": {year: dict(months) for year, months in empty_per_month.items()},
        }

    per_year_rows = (
        Action.objects.exclude(timestamp__isnull=True)
        .annotate(_year=ExtractYear("timestamp"))
        .values("verb", "_year")
        .annotate(total=Count("id"))
    )
    for row in per_year_rows:
        verb = row["verb"]
        year = row.get("_year")
        if verb in stats and year in valid_years:
            stats[verb]["per_year"][str(year)] = row["total"]

    per_month_rows = (
        Action.objects.exclude(timestamp__isnull=True)
        .annotate(_year=ExtractYear("timestamp"), _month=ExtractMonth("timestamp"))
        .values("verb", "_year", "_month")
        .annotate(total=Count("id"))
    )
    for row in per_month_rows:
        verb = row["verb"]
        year = row.get("_year")
        month = row.get("_month")
        if verb in stats and year in valid_months_per_year and month in valid_months_per_year[year]:
            stats[verb]["per_month"][str(year)][str(month)] = row["total"]

    cache.set(cache_key, stats, timeout=CACHE_TIMEOUT_ONE_DAY)
    return stats


def usage_action_metrics():
    now = datetime.now(timezone.utc)
    first_action_timestamp = Action.objects.exclude(timestamp__isnull=True).aggregate(first=Min("timestamp"))["first"]
    start_year = first_action_timestamp.year if first_action_timestamp else now.year
    years = list(range(start_year, now.year + 1))
    valid_years = set(years)
    months_for_year = {year: range(1, now.month + 1) if year == now.year else range(1, 13) for year in years}
    valid_months_per_year = {year: set(months_for_year[year]) for year in years}

    cache_key = f"usage:{USAGE_CACHE_VERSION}:action_statistics:{start_year}:{now.year}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    total_rows = list(Action.objects.all().values("verb").annotate(total=Count("id")))
    verbs = sorted(KNOWN_ACTION_VERBS.union({row["verb"] for row in total_rows if row["verb"]}))

    actions = {
        verb: {
            "total": 0,
            "per_year": {str(year): 0 for year in years},
            "per_month": {str(year): {str(month): 0 for month in months_for_year[year]} for year in years},
        }
        for verb in verbs
    }

    for row in total_rows:
        verb = row["verb"]
        if verb in actions:
            actions[verb]["total"] = row["total"]

    per_year_rows = (
        Action.objects.exclude(timestamp__isnull=True)
        .annotate(_year=ExtractYear("timestamp"))
        .values("verb", "_year")
        .annotate(total=Count("id"))
    )
    for row in per_year_rows:
        verb = row["verb"]
        year = row.get("_year")
        if verb in actions and year in valid_years:
            actions[verb]["per_year"][str(year)] = row["total"]

    per_month_rows = (
        Action.objects.exclude(timestamp__isnull=True)
        .annotate(_year=ExtractYear("timestamp"), _month=ExtractMonth("timestamp"))
        .values("verb", "_year", "_month")
        .annotate(total=Count("id"))
    )
    for row in per_month_rows:
        verb = row["verb"]
        year = row.get("_year")
        month = row.get("_month")
        if verb in actions and year in valid_months_per_year and month in valid_months_per_year[year]:
            actions[verb]["per_month"][str(year)][str(month)] = row["total"]

    result = {
        "years": [str(year) for year in years],
        "verbs": verbs,
        "actions": actions,
    }
    cache.set(cache_key, result, timeout=CACHE_TIMEOUT_ONE_DAY)
    return result


def _default_previous_calendar_month() -> tuple[date, date]:
    today = datetime.now(timezone.utc).date()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    return first_day_of_previous_month, last_day_of_previous_month


def _resolve_user_statistics_window(start_date: date | None, end_date: date | None) -> tuple[date, date]:
    default_start, default_end = _default_previous_calendar_month()
    resolved_start = start_date or default_start
    resolved_end = end_date or default_end
    if resolved_start > resolved_end:
        return resolved_end, resolved_start
    return resolved_start, resolved_end


def _actor_pairs_filter(actor_rows: list[dict[str, Any]]) -> Q:
    actor_filter = Q()
    for row in actor_rows:
        actor_filter |= Q(
            actor_content_type_id=row["actor_content_type_id"],
            actor_object_id=row["actor_object_id"],
        )
    return actor_filter


def _actor_label(content_type: ContentType | None, object_id: str) -> str:
    if not content_type:
        return f"unknown:{object_id}"

    default_label = f"{content_type.app_label}.{content_type.model}:{object_id}"
    model_class = content_type.model_class()
    if not model_class:
        return default_label

    try:
        obj = model_class._default_manager.filter(pk=object_id).first()
        if obj is not None:
            return f"{content_type.app_label}.{content_type.model}: {obj}"
    except BaseException:  # pylint: disable=broad-except
        return default_label

    return default_label


def user_statistics(start_date: date | None = None, end_date: date | None = None, max_records: int = 10):
    start_date, end_date = _resolve_user_statistics_window(start_date, end_date)
    max_records = max(1, int(max_records or 10))

    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
    end_dt_exclusive = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)

    total_rows = list(
        Action.objects.filter(timestamp__gte=start_dt, timestamp__lt=end_dt_exclusive)
        .values("actor_content_type_id", "actor_object_id")
        .annotate(
            total_actions=Count("id"),
            total_distinct_verbs=Count("verb", distinct=True),
        )
        .order_by("-total_actions", "actor_content_type_id", "actor_object_id")[:max_records]
    )

    if not total_rows:
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "max_records": max_records,
            "actors": [],
        }

    actor_filter = _actor_pairs_filter(total_rows)
    verb_rows = (
        Action.objects.filter(timestamp__gte=start_dt, timestamp__lt=end_dt_exclusive)
        .filter(actor_filter)
        .values("actor_content_type_id", "actor_object_id", "verb")
        .annotate(total=Count("id"))
    )

    verbs_by_actor: dict[tuple[int, str], dict[str, int]] = {}
    for row in verb_rows:
        actor_key = (row["actor_content_type_id"], row["actor_object_id"])
        verbs_by_actor.setdefault(actor_key, {})
        verbs_by_actor[actor_key][row["verb"]] = row["total"]

    content_types = ContentType.objects.in_bulk({row["actor_content_type_id"] for row in total_rows})

    actors = []
    for row in total_rows:
        actor_key = (row["actor_content_type_id"], row["actor_object_id"])
        content_type = content_types.get(row["actor_content_type_id"])
        actors.append(
            {
                "actor_content_type_id": row["actor_content_type_id"],
                "actor_object_id": str(row["actor_object_id"]),
                "actor": _actor_label(content_type, str(row["actor_object_id"])),
                "total_actions": row["total_actions"],
                "total_distinct_verbs": row["total_distinct_verbs"],
                "verbs": verbs_by_actor.get(actor_key, {}),
            }
        )

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "max_records": max_records,
        "actors": actors,
    }
