# SPDX-License-Identifier: Apache-2.0
"""
These testcases make sure we can create scans.

Run these tests with make testcase case=test_deduplication
"""
import logging
from datetime import datetime, timezone

from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, EndpointGenericScan

from dashboard.internet_nl_dashboard.logic.deduplication import dedupe_urls
from dashboard.internet_nl_dashboard.models import Account, UrlList

log = logging.getLogger('test')


def test_per_acount_scanner(db) -> None:
    account, _ = Account.objects.all().get_or_create(name="test",
                                                     internet_nl_api_username='test',
                                                     internet_nl_api_password=Account.encrypt_password('test'),)

    # add duplicate (named) urls, the name is the same, the id is different.
    url1, _ = Url.objects.get_or_create(url='www.internet.nl', is_dead=False, not_resolvable=False,
                                        internal_notes='different data, is different id 1')
    url2, _ = Url.objects.get_or_create(url='www.internet.nl', is_dead=False, not_resolvable=False,
                                        internal_notes='different data, is different id 2')
    url3, _ = Url.objects.get_or_create(url='www.internet.nl', is_dead=False, not_resolvable=False,
                                        internal_notes='different data, is different id 3')
    url4, _ = Url.objects.get_or_create(url='www.unaffected_url.nl', is_dead=False, not_resolvable=False,
                                        internal_notes='different data, is different id 3')

    # make sure that these three urls actually exist
    assert Url.objects.all().count() == 4

    # with duplicate endpoints, where the endpoints themselves are unique for the url.
    ep1, _ = Endpoint.objects.get_or_create(url=url1, protocol='dns_a_aaaa', port=0, ip_version=0, is_dead=False)
    ep2, _ = Endpoint.objects.get_or_create(url=url2, protocol='dns_a_aaaa', port=0, ip_version=0, is_dead=False)
    ep3, _ = Endpoint.objects.get_or_create(url=url3, protocol='dns_a_aaaa', port=0, ip_version=0, is_dead=False)
    ep4, _ = Endpoint.objects.get_or_create(url=url1, protocol='dns_soa', port=0, ip_version=0, is_dead=False)
    ep5, _ = Endpoint.objects.get_or_create(url=url2, protocol='dns_soa', port=0, ip_version=0, is_dead=False)
    ep6, _ = Endpoint.objects.get_or_create(url=url4, protocol='unaffected', port=0, ip_version=0, is_dead=False)

    # make sure there are five endpoints:
    assert Endpoint.objects.all().count() == 6

    # and duplicate scan results
    egs1, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep1, type='testscan 1', rating='1',
                                                        rating_determined_on=datetime.now(timezone.utc))
    egs2, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep1, type='testscan 2', rating='2',
                                                        rating_determined_on=datetime.now(timezone.utc))
    egs3, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep1, type='testscan 3', rating='3',
                                                        rating_determined_on=datetime.now(timezone.utc))

    egs4, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep2, type='testscan 4', rating='4',
                                                        rating_determined_on=datetime.now(timezone.utc))
    egs5, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep2, type='testscan 5', rating='5',
                                                        rating_determined_on=datetime.now(timezone.utc))

    egs6, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep3, type='testscan 6', rating='6',
                                                        rating_determined_on=datetime.now(timezone.utc))

    # some with the same data:
    egs7, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep4, type='testscan 1', rating='1',
                                                        rating_determined_on=datetime.now(timezone.utc))
    egs8, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep4, type='testscan 2', rating='2',
                                                        rating_determined_on=datetime.now(timezone.utc))
    egs9, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep4, type='testscan 3', rating='3',
                                                        rating_determined_on=datetime.now(timezone.utc))

    egs10, _ = EndpointGenericScan.objects.get_or_create(endpoint=ep6, type='unaffected', rating='3',
                                                         rating_determined_on=datetime.now(timezone.utc))

    assert EndpointGenericScan.objects.all().count() == 10

    # ep5 has no scans.

    # These urls, with their endpoints and scans are in three different lists. At the end of the test
    # all different lists should contain the same url, all other urls should be removed from the database.
    # the endpoints are merged into one set of unique endpoints. The scans are just attached to their respective
    # unique endpoint.

    urllist, _ = UrlList.objects.all().get_or_create(name='test 1', account=account, scan_type='web')
    urllist.urls.add(url1)
    urllist.save()

    urllist, _ = UrlList.objects.all().get_or_create(name='test 2', account=account, scan_type='web')
    urllist.urls.add(url2)
    urllist.save()

    urllist, _ = UrlList.objects.all().get_or_create(name='test 3', account=account, scan_type='web')
    urllist.urls.add(url3)
    urllist.save()

    urllist, _ = UrlList.objects.all().get_or_create(name='unaffected', account=account, scan_type='web')
    urllist.urls.add(url4)
    urllist.save()

    # now we're going to dedupe this whole thing.
    dedupe_urls()

    # assert all urls in the urllists are the same.
    list_1 = UrlList.objects.all().filter(name='test 1').first()
    list_2 = UrlList.objects.all().filter(name='test 2').first()
    list_3 = UrlList.objects.all().filter(name='test 3').first()
    assert list_1.urls.count() == list_2.urls.count() == list_3.urls.count()
    assert list_1.urls.first().id == list_2.urls.last().id == list_3.urls.first().id

    # verify that the unaffected list has a different url than the affected list
    list_4 = UrlList.objects.all().filter(name='unaffected').first()
    assert list_1.urls.first().id != list_4.urls.last().id

    # assert that there is only one url in each of these lists
    assert list_1.urls.count() == 1
    assert list_2.urls.count() == 1
    assert list_3.urls.count() == 1
    assert list_4.urls.count() == 1

    # assert there should only be one url left + the unaffected url, as the rest where identical
    assert Url.objects.all().filter(url='www.internet.nl').count() == 1

    # the total number of urls should be two now, including one unaffected:
    assert Url.objects.all().count() == 1 + 1

    # assert there should only be two different endpoints now, instead of 5, as they are deduped too + one unaffected
    assert Endpoint.objects.all().count() == 2 + 1

    # assert all scan results are still saved
    assert EndpointGenericScan.objects.all().count() == 9 + 1
