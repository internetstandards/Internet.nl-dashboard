import logging

from django.db import transaction
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, EndpointGenericScan

from dashboard.internet_nl_dashboard.models import UrlList

log = logging.getLogger(__package__)


@transaction.atomic
def dedupe_urls():
    """
    Duplicate urls should not occur in the database. That leads to more data, but also duplicate endpoints and
    issues on what endpoint to save scanresults to. Some bug caused to create many duplicate urls on
    2019-07-11, at what seems to be a bulk import. The exact cause has not yet been determined, but might be
    a transaction issue (where there is no transaction).

    It seems the hall of fame was imported that day, a few times. And in the import routine (probably from spreadsheet)
    there is an error. If you upload a list multiple times, it makes double urls. But not always. So it's
    interesting to investigate why this happens. It only happened on that day, and with nothing else.

    This will deduplicate urls to a single one, making sure everyone is working with the same url.

    The database is missing a unicity constraint on url. Or did we design layering of urls with is dead?

    Side effects:
    This might revive some dead urls.

    :return:
    """
    urls = Url.objects.all().filter().order_by('created_on')
    # prevent going over the same url twice, as that is a waste of time, and increases complexity.
    # our goal is to save each url once, and which one gets removed is not really relevant, as everyone shares
    # the same url in their lists.
    all_different_urls = []
    all_different_url_addresses = []
    for target_url in urls:
        if target_url.url not in all_different_url_addresses:
            all_different_url_addresses.append(target_url.url)
            all_different_urls.append(target_url)

    log.info(f'Going to inspect {len(all_different_url_addresses)} urls.')
    for target_url in all_different_urls:
        duplicate_urls = list(Url.objects.all().filter(url=target_url.url).exclude(id=target_url.id))
        if not duplicate_urls:
            continue

        log.info(f'Found {len(duplicate_urls)} for target url: {target_url}.')
        for duplicate_url in duplicate_urls:

            # transfer all endpoints and endpoints scans
            duplicate_endpoints = Endpoint.objects.all().filter(url=duplicate_url)
            for duplicate_endpoint in duplicate_endpoints:
                endpoint_target, created = Endpoint.objects.all().get_or_create(
                    url=target_url,
                    protocol=duplicate_endpoint.protocol,
                    port=duplicate_endpoint.port,
                    ip_version=duplicate_endpoint.ip_version,
                    is_dead=duplicate_endpoint.is_dead)
                if created:
                    log.info(f'A similar endpoint has been created at the target url. {duplicate_endpoint}')
                else:
                    log.info(f'A similar endpoint already exists in the target url.')

                # duplicate scans in a day is not a problem, those are filtered out and only the latest one is used
                # so the data is consistent.
                EndpointGenericScan.objects.all().filter(endpoint=duplicate_endpoint).update(endpoint=endpoint_target)
                log.debug(f'Moved all the scans from endpoint {duplicate_endpoint} to {endpoint_target}.')
                duplicate_endpoint.delete()

            # replace the duplicate_url with the original url in urllists.
            urllist_with_duplicate_urls = UrlList.objects.all().filter(urls__id=duplicate_url.id)
            log.info(f'The duplicate url is being used in {len(urllist_with_duplicate_urls)} lists. It will be '
                     f'replaced with the target url {target_url}.')
            for urllist_with_duplicate_url in urllist_with_duplicate_urls:
                urllist_with_duplicate_url.urls.remove(duplicate_url)
                urllist_with_duplicate_url.urls.add(target_url)
                urllist_with_duplicate_url.save()

            # many other models like urlip, urlreport, rescanrequest,  and such are cascade-deleted.
            duplicate_url.delete()
