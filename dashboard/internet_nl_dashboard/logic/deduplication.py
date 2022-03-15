# SPDX-License-Identifier: Apache-2.0
from typing import List

from django.db import connection, transaction
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, EndpointGenericScan

from dashboard.internet_nl_dashboard.models import UrlList


@transaction.atomic
def dedupe_urls():
    # our goal is to save each url once, everyone shares the same url in their lists.
    urls_by_name = get_duplicate_urls_by_name()
    print(f"Going to deduplicate {len(urls_by_name)} domains.")
    for target_url_name in urls_by_name:
        print(f"Going to deduplicate stuff for domain: {target_url_name}")
        # Move everything to the oldest url.
        target_url = Url.objects.all().filter(url=target_url_name).order_by('created_on').first()
        duplicate_urls = list(Url.objects.all().filter(url=target_url.url).exclude(id=target_url.id))
        if not duplicate_urls:
            print("Could not find duplicates...")
            continue

        print(f'Found {len(duplicate_urls)} for target url: {target_url}.')
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
                    print(f'A similar endpoint has been created at the target url. {duplicate_endpoint}')
                else:
                    print('A similar endpoint already exists in the target url.')
                # duplicate scans in a day is not a problem, those are filtered out and only the latest one is used
                # so the data is consistent.
                EndpointGenericScan.objects.all().filter(endpoint=duplicate_endpoint).update(endpoint=endpoint_target)
                print(f'Moved all the scans from endpoint {duplicate_endpoint} to {endpoint_target}.')
                duplicate_endpoint.delete()

            # replace the duplicate_url with the original url in urllists.
            urllist_with_duplicate_urls = UrlList.objects.all().filter(urls__id=duplicate_url.id)
            print(f'The duplicate url is being used in {len(urllist_with_duplicate_urls)} lists. It will be '
                  f'replaced with the target url {target_url}.')
            for urllist_with_duplicate_url in urllist_with_duplicate_urls:
                urllist_with_duplicate_url.urls.remove(duplicate_url)
                urllist_with_duplicate_url.urls.add(target_url)
                urllist_with_duplicate_url.save()
            # many other models like urlip, urlreport, rescanrequest,  and such are cascade-deleted.
            duplicate_url.delete()


def get_duplicate_urls_by_name() -> List[str]:
    # Django just can not do this...
    query = """SELECT url, count(*) FROM url GROUP BY url HAVING COUNT(*) > 1;"""
    urls = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            urls.append(row[0])
    return urls
