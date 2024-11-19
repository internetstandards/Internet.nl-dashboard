# SPDX-License-Identifier: Apache-2.0
"""
These testcases help to validate the working of the listmanagement API.

Run these tests with tox -e test -- -k test_urllist_management
"""
import timeit

import pytest
import responses
from constance.test import override_config
from websecmap.organizations.models import Url

from dashboard.internet_nl_dashboard.logic.domains import (ServerError, add_domains_from_raw_user_data, clean_urls,
                                                           delete_list, delete_url_from_urllist,
                                                           get_or_create_list_by_name, get_urllist_content,
                                                           get_urllists_from_account, keys_are_present_in_object,
                                                           rename_list, retrieve_possible_urls_from_unfiltered_input,
                                                           save_urllist_content_by_name, suggest_subdomains)
from dashboard.internet_nl_dashboard.models import Account


@responses.activate
def test_suggest_subdomains(db, caplog):
    responses.add(responses.GET, 'http://localhost:8001/?domain=test&suffix=nl&period=370', json=["test"], status=200)
    responses.add(responses.GET, 'http://localhost:8001/?domain=notexisting&suffix=nl&period=370', json=[], status=404)
    responses.add(responses.GET, 'http://localhost:8001/?domain=broken&suffix=nl&period=370', json=[], status=500)

    assert suggest_subdomains("test.nl", 370) == ["test"]
    assert suggest_subdomains("notexisting.nl") == []

    # incomplete requests:
    with pytest.raises(ValueError):
        assert suggest_subdomains("192.168.1.1") == []
    with pytest.raises(ValueError):
        suggest_subdomains("a")
    with pytest.raises(ServerError):
        suggest_subdomains("broken.nl")


@override_config(DASHBOARD_MAXIMUM_DOMAINS_PER_LIST=5000)
def test_add_domains_from_raw_user_data(db, current_path, redis_server):
    """
    Add 1000 domains, which should be very fast.

    Should give a warning after the limit of N domains is crossed, should add to this limit.
    """

    file = f'{current_path}/test_domain_management/top_10000_nl_domains.txt'
    with open(file, 'rt') as f:
        domains = f.read()

    domains = domains.split("\n")

    account, created = Account.objects.all().get_or_create(name="test")

    list_1 = get_or_create_list_by_name(account, "test list 1")

    # you can't go past the DASHBOARD_MAXIMUM_DOMAINS_PER_LIST
    response = add_domains_from_raw_user_data(account, {
        'list_id': list_1.id,
        'urls': ", ".join(domains[:6000])
    })

    assert response['error'] is True
    assert response['message'] == "too_many_domains"

    # add an existing url, this should be one query check:
    new_url = Url.objects.all().create(url='nu.nl')
    list_1.urls.add(new_url)

    response = add_domains_from_raw_user_data(account, {
        'list_id': list_1.id,
        'urls': ", ".join(domains[:100])
    })

    assert response['success'] is True
    assert response['data'] == {
        'incorrect_urls': [],
        'added_to_list': 99,
        'already_in_list': 1,
        'duplicates_removed': 0
    }


def test_keys_match():
    # a, b, c in any object
    assert keys_are_present_in_object(expected_keys=['a', 'b', 'c'], any_object={
        'a': 1, 'b': 2, 'c': 3, 'd': 4}) is True

    # Missing b
    assert keys_are_present_in_object(expected_keys=['a', 'b', 'c'], any_object={'a': 1, 'c': 3, 'd': 4}) is False

    # No expectation should always match
    assert keys_are_present_in_object(expected_keys=[], any_object={'a': 1, 'b': 2, 'c': 3, 'd': 4}) is True


def test_retrieve_urls_from_unfiltered_input() -> None:
    output, duplicates_removed = retrieve_possible_urls_from_unfiltered_input(
        "https://www.apple.com:443/nl/iphone-11/, bing.com, http://nu.nl, nu.nl")
    assert output == ['bing.com', 'nu.nl', 'www.apple.com']
    # one nu.nl removed
    assert duplicates_removed == 1

    # input contains multiple lines, whitespaces before and after the domains and some tabs mixed in.

    # \s in regex only filters out: \t\n\r\f\v not all whitespace characters in unicode.
    # All examples for https://qwerty.dev/whitespace/ are in the below input, which is invisible to the naked eye :)
    unsanitized_input = """
    ,  
     stichtingmediawijzer.nl	  ​ 
            , , ,   ⠀ 
     	   
    eskillsplatform.nl  ,
    """  # noqa violates python coding standard on points E101 and W191. Needed for this test :)

    output, duplicates_removed = retrieve_possible_urls_from_unfiltered_input(unsanitized_input)
    # Zero width space is also seen as a string, and filtered out as a possible domain. See test_clean_urls.
    # ' ', ' ⠀ ',  '\u200b '
    assert output == ['eskillsplatform.nl', 'stichtingmediawijzer.nl']

    # test #410
    unsanitized_input = "home­lan­der.nl"
    output, duplicates_removed = retrieve_possible_urls_from_unfiltered_input(unsanitized_input)
    assert output == ['homelander.nl']


def test_retrieve_urls_from_unfiltered_input_email() -> None:
    # fix 246 and 316
    # note that 'info' is seen as a possible url. That will be removed when cleaning the urls.
    output, duplicates_removed = retrieve_possible_urls_from_unfiltered_input(
        "example.com/something, example2.com/something., info@example3.com, info@example4.com")
    #  'info'
    assert output == ['example.com', 'example2.com', 'example3.com', 'example4.com']


def test_retrieve_possible_urls_from_unfiltered_input_speed() -> None:
    # Fake data was 3.4 seconds
    # data = "https://SUB.EXAMPLE.com/something/#, " * 25

    # real data it takes 6.1 seconds, so it's better to use real data in this case
    data = """google.com, a-msedge.net, facebook.com, amazonaws.com, microsoft.com, apple.com, googleapis.com,
    youtube.com, akamaiedge.net, akamai.net, azure.com, twitter.com, instagram.com, googlevideo.com, gstatic.com,
    cloudflare.com, live.com, office.com, linkedin.com, doubleclick.net, tiktokcdn.com, googletagmanager.com,
    akadns.net, apple-dns.net, amazon.com, fbcdn.net, windowsupdate.com, trafficmanager.net, googleusercontent.com,
    microsoftonline.com, netflix.com, icloud.com, wikipedia.org, fastly.net, root-servers.net, l-msedge.net, bing.com,
    domaincontrol.com, wordpress.org, gtld-servers.net, youtu.be, digicert.com, ui.com, github.com, aaplimg.com,
    yahoo.com, mail.ru, pinterest.com, tiktokv.com, zoom.us, t-msedge.net, sharepoint.com, adobe.com, goo.gl,
    cloudfront.net, nflxso.net, spotify.com, windows.net, google-analytics.com, googlesyndication.com, vimeo.com,
    s-msedge.net, shipt.com, gvt2.com, office.net, gandi.net, bit.ly, msn.com, wordpress.com, office365.com,
    edgekey.net, skype.com, intuit.com, whatsapp.net, bytefcdn-oversea.com, whatsapp.com, yandex.net, wac-msedge.net,
    ntp.org, cloudflare.net, cloudflare-dns.com, gvt1.com, app-measurement.com, qq.com, mozilla.org, blogspot.com,
    ytimg.com, outlook.com, opera.com, reddit.com, tiktok.com, cdn77.org, googledomains.com, snapchat.com,
    trbcdn.net, roblox.com, comcast.net, yandex.ru, europa.eu, baidu.com, amazon-adsystem.com, macromedia.com,
    dropbox.com, unity3d.com, googleadservices.com, nih.gov, tumblr.com, pki.goog, nic.ru, b-msedge.net,
    ttlivecdn.com, a2z.com, adnxs.com, epicgames.com, one.one, gravatar.com, msedge.net, spo-msedge.net,
    msftncsi.com, sberdevices.ru, windows.com, github.io, nytimes.com, tiktokcdn-us.com, t.me, sentry.io, netflix.net,
    webex.com, wa.me, criteo.com, flickr.com, akamaized.net, samsung.com, cloudapp.net, cdninstagram.com,
    bytefcdn-ttpeu.com, edgesuite.net, health.mil, forms.gle, registrar-servers.com, vk.com, ggpht.com, archive.org,
    apache.org, appsflyersdk.com, paypal.com, zemanta.com, aiv-cdn.net, rubiconproject.com, 2mdn.net, tds.net,
    omtrdc.net, amazonvideo.com, salesforce.com, o365filtering.com, meraki.com, rbxcdn.com, t.co, cnn.com, medium.com,
    miit.gov.cn, soundcloud.com, casalemedia.com, azureedge.net, mangosip.ru, applovin.com, theguardian.com, w3.org,
    gmail.com, ebay.com, dns.google, forbes.com, demdex.net, appsflyer.com, wsdvs.com, adobe.io, worldfcdn2.com,
    azurewebsites.net, e2ro.com, taboola.com, mzstatic.com, googleblog.com, bbc.co.uk, pubmatic.com,
    facebook-hardware.com, myfritz.net, lencr.org, dnsowl.com, cdn-apple.com, salesforceliveagent.com, slack.com,
    example.com, akamaihd.net, xiaomi.com, mcafee.com, nr-data.net, creativecommons.org, kaspersky.com, rambler.ru,
    bbc.com, att.com, hp.com, sourceforge.net, discord.com, nginx.org, doubleverify.com, imdb.com, mit.edu,
    rocket-cdn.com, cisco.com, comcast.com, roku.com, abusix.zone, nginx.com, edgecdn.ru, twitch.tv, telefonica.de,
    t-mobile.com, shifen.com, playstation.net, miui.com, sciencedirect.com, smartadserver.com, who.int,
    msftconnecttest.com, ubuntu.com, telecid.ru, scorecardresearch.com, mtgglobals.com, b-cdn.net, userapi.com,
    wixsite.com, jomodns.com, researchgate.net, facebook.net, youtube-nocookie.com, amazon.co.uk, ampproject.org,
    issuu.com, launchdarkly.com, hubspot.com, aliyuncs.com, android.com, cmediahub.ru, cedexis.net, wikimedia.org,
    ibm.com, tinyurl.com, amazon.dev, cdc.gov, openx.net, grammarly.com, hipages.com.au, oracle.com, atomile.com,
    comfortel.pro, adsafeprotected.com, weebly.com, washingtonpost.com, mozilla.com, wp.com, canva.com, reuters.com,
    doi.org, trendmicro.com, dns.cn, shopify.com, harvard.edu, booking.com, dailymail.co.uk, att.net,
    dual-s-msedge.net, go.com, 3lift.com, slideshare.net, rlcdn.com, sharethrough.com, avast.com, adsrvr.org,
    google.com.br, dnsmadeeasy.com, weibo.com, www.gov.uk, opendns.com, force.com, media-amazon.com, teamviewer.com,
    bidswitch.net, linktr.ee, espn.com, drom.ru, nist.gov, reg.ru, media.net, wiley.com, samsungcloud.com, moatads.com,
    appcenter.ms, vungle.com, bloomberg.com, ttdns2.com, etsy.com, google.co.uk, wildberries.ru, googletagservices.com,
    wsj.com, samsungqbe.com, steampowered.com, jsdelivr.net, nature.com, wbx2.com, stripe.com, elasticbeanstalk.com,
    branch.io, quantserve.com, php.net, businessinsider.com, msidentity.com, eset.com, adriver.ru,
    samsungcloudsolution.com, indeed.com, crashlytics.com, alibabadns.com, criteo.net, checkpoint.com, un.org,
    twimg.com, weather.com, unsplash.com, google.de, godaddy.com, lijit.com, yahoo.co.jp, dotomi.com, springer.com,
    dailymotion.com, list-manage.com, sc-cdn.net, imrworldwide.com, azurefd.net, stanford.edu, id5-sync.com,
    quora.com, adobedtm.com, nasa.gov, dell.com, adform.net, discord.gg, cdngslb.com, outbrain.com, name-services.com,
    360yield.com, ring.com, gnu.org, ksyuncdn.com, cnbc.com, liadm.com, bamgrid.com, dzeninfra.ru, ea.com,
    stackoverflow.com, creativecdn.com, mi.com, netangels.ru, openai.com, eventbrite.com, cpanel.net, sophos.com,
    xcal.tv, amazonalexa.com, 3gppnetwork.org, foxnews.com, teads.tv, clarity.ms, azure-dns.com, ozon.ru,
    tripadvisor.com, mynetname.net, 1c.ru, go-mpulse.net, ibyteimg.com, inner-active.mobi, nease.net, globo.com,
    scdn.co, npr.org, wix.com, aliexpress.com, xboxlive.com, tp-link.com, giphy.com, sohu.com, rzone.de, time.com,
    usatoday.com, forter.com, walmart.com, telegraph.co.uk, pv-cdn.net, avcdn.net, elisa.fi, goodreads.com,
    taobao.com, statista.com, cdek.ru, myshopify.com, g.page, tradingview.com, hichina.com, robinhood.com,
    blogger.com, hicloud.com, amazon.de, arubanetworks.com, alicdn.com, addtoany.com, debian.org, trustpilot.com,
    surveymonkey.com, hostgator.com, pixabay.com, sc-gw.com, autodesk.com, pangle.io, duckdns.org, cnet.com,
    bilibili.com, online-metrix.net, amzn.to, icloud-content.com, ups.com, aol.com, firetvcaptiveportal.com,
    scribd.com, healthline.com, byteoversea.net, herokudns.com, gamepass.com, nflximg.com, sfx.ms, sentinelone.net,
    nvidia.com, bitrix24.ru, beian.gov.cn, dzen.ru, speedtest.net, kwai.net, zendesk.com, inmobi.com, naver.com,
    wired.com, ai-lawandorder.com, ngenix.net, alibaba.com, chinamobile.com, kaspersky-labs.com, ok.ru,
    mayoclinic.org, ted.com, behance.net, safebrowsing.apple, mikrotik.com, ft.com, yahoodns.net, webrootcloudav.com,
    telegram.me, indiatimes.com, verisign.com, cloudflareclient.com, viber.com, ttvnw.net, gosuslugi.ru,
    deepintent.com, digitalocean.com, amazontrust.com, wal-mart.com, imgsmail.ru, imgur.com, galleryvalery.com,
    hotjar.com, mysql.com, disqus.com, worldnic.com, newrelic.com, pandora.com, buzzfeed.com, independent.co.uk,
    deviantart.com, google.ca, consultant.ru, webmd.com, google.fr, squarespace.com, stbid.ru, amazon.co.jp, line.me,
    marriott.com, entrust.net, atlassian.com, berkeley.edu, ca.gov, loc.gov, mediatek.com, google.es, visa.com,
    cdn20.com, goskope.com, cbsnews.com, sapo.pt, mailchimp.com, nypost.com, datadoghq.com, aboutads.info,
    google.co.jp, launchpad.net, yelp.com, jquery.com, google.it, mncdn.com, intel.com, paloaltonetworks.com,
    shutterstock.com, grammarly.io, 163.com, airbnb.com, onetrust.com, duckduckgo.com, ovscdns.com, dnspod.net,
    huawei.com, sorbs.net, playstation.com, tandfonline.com, rakuten.co.jp, oup.com, nflxvideo.net, free.fr,
    duolingo.com, braze.com, fast.com, conviva.com, myspace.com, xhamster.com, nest.com, rackspace.net, ivi.ru,
    fb.com, uol.com.br, steamcommunity.com, sina.com.cn, techcrunch.com, patreon.com, ezvizlife.com, theverge.com,
    nintendo.net, hugedomains.com, visualstudio.com, calendly.com, netease.com, amplitude.com, nike.com, ietf.org,
    timeweb.ru, licdn.com, freepik.com, cornell.edu, ys7.com, byteglb.com, herokuapp.com, noaa.gov, yandex.com,
    merriam-webster.com, ikea.com, shalltry.com, accuweather.com, smaato.net, latimes.com, adobe.net, cookielaw.org,
    qlivecdn.com, nelreports.net, google.co.in, fontawesome.com, incapdns.net, statuspage.io, dns.ne.jp,
    qualtrics.com, akam.net, pinimg.com, wattpad.com, google.com.hk, nstld.com, mts.ru, crwdcntrl.net,
    warnerbros.com, agkn.com, yieldmo.com, huffingtonpost.com, mozgcp.net, rt.ru, livejournal.com, yahoo.net,
    aws.dev, omnitagjs.com, life360.com, prnewswire.com, typekit.net, virtualearth.net, bidr.io, dns-parking.com,
    igamecj.com, britannica.com, box.com, target.com, appspot.com, mega.co.nz, e-msedge.net, intercom.io, bestbuy.com,
    allawnos.com, addthis.com, livechatinc.com, live.net, okta.com, optimizely.com, nbcnews.com, elpais.com,
    impervadns.net, bugsnag.com, beeline.ru, contentsquare.net, washington.edu, tapad.com, stackadapt.com,
    aliyun.com, mega.nz, ieee.org, grabpay.com, fandom.com, riotgames.com, google.pl, spov-msedge.net,
    w3schools.com, dbankcloud.cn, fda.gov, coinmarketcap.com, uber.com, ovscdns.net, badoo.com, thesun.co.uk,
    samsungapps.com, amazon.fr, spaceweb.pro, footprintdns.com, contextweb.com, mediafire.com, investopedia.com,
    temu.com, 33across.com, flashtalking.com, klaviyo.com, sagepub.com, amazon.ca, kaspi.kz, everesttech.net,
    cdnbuild.net, bluekai.com, dbankcloud.com, hostgator.com.br, theatlantic.com, themeforest.net, hbr.org, hulu.com,
    udemy.com, google.com.mx, rocket-cdnbp.com, shein.com, service.gov.uk, yimg.com, pornhub.com, douyincdn.com,
    google.com.tr, attn.tv, pccc.com, allaboutcookies.org, samsungacr.com, gumgum.com, telegram.org, homedepot.com,
    docker.com, unesco.org, gihc.net, bandcamp.com, ioam.de, ttoverseaus.net, xvideos.com, nationalgeographic.com,
    usgovcloudapi.net, maricopa.gov, cambridge.org, jotform.com, tencent-cloud.net, xiaomi.net, bytetcdn.com,
    ecdns.net, mixpanel.com, dns-shop.ru, name.com, w55c.net, datto.com, tremorhub.com, usda.gov, ign.com, youku.com,
    telekom.de, schwab.com, lenovo.com, lemonde.fr, 1rx.io, fiverr.com, clever.com, me.com, mailchi.mp, zillow.com,
    steamstatic.com, yximgs.com, rfihub.com, people.com, rackspace.com, kickstarter.com, networkadvertising.org,
    pbs.org, online.net, usps.com, notion.so, svc.ms, cloudns.net, a-mo.net, swrve.com, bankofamerica.com, rncdn7.com,
    apigee.net, chaturbate.com, bitdefender.com, bluehost.com, rbc.ru, supersonicads.com, huffpost.com, rspamd.com,
    business.site, oath.cloud, sitescout.com, awsglobalaccelerator.com, dns.com, princeton.edu, swiftkey.com,
    apple.news, amazon.es, pluto.tv, aniview.com, kargo.com, x.com, nordvpn.com, stickyadstv.com, google.cn,
    t-online.de, onlinepbx.ru, xfinity.com, chartboost.com, churnzero.net, mgid.com, upwork.com, namebrightdns.com,
    bootstrapcdn.com, news.com.au, ebay.co.uk, hm.com, iso.org, intentiq.com, ipredictive.com, xnxx.com,
    dreamhost.com, fb.me, lefigaro.fr, heytapdl.com, change.org, redhat.com, turn.com, gandi-ns.fr, amazon.it,
    mirtesen.ru, sweetxladies.com, cdnvideo.ru, samsungosp.com, whitehouse.gov, brave.com, unrulymedia.com, allegro.pl,
    spbycdn.com, ssl-images-amazon.com, indexww.com, connatix.com, norton.com, rings.solutions, fedex.com,
    epa.gov, cookiedatabase.org, disneyplus.com, onlyfans.com, markmonitor.com, miwifi.com, krxd.net, shopee.com.br,
    1drv.com, cdnhwc1.com, onetag-sys.com, discordapp.com, vedcdnlb.com, firebaseio.com, adjust.com,
    browser-intake-datadoghq.com, fbsbx.com, bild.de, ameblo.jp, academia.edu, primevideo.com, ertelecom.ru,
    service-now.com, statcounter.com, mwbsys.com, heytapmobile.com, seznam.cz, zoho.com, amazon.in, mozilla.net,
    unpkg.com, isnssdk.com, gitlab.com, worldbank.org, myqcloud.com, githubusercontent.com, phicdn.net,
    atlassian.net, ks-cdn.com, erome.com, appier.net, instructure.com, spamhaus.org, adrta.com, firefox.com,
    canonical.com, azure-devices.net, chartbeat.net, sonobi.com, 360safe.com, exelator.com, 360.cn,
    cloudflareinsights.com, state.gov, netgear.com, pendo.io, deloitte.com, arcgis.com, llnwi.net, vmware.com,
    splashtop.com, yellowblue.io, genius.com, pusher.com, shopee.co.id, globalsign.com, daum.net, tribalfusion.com,
    btloader.com, economist.com, heylink.me, bdydns.com, hilton.com, mgts.ru, umich.edu, repubblica.it, tesla.com,
    mob.com, springserve.com, lowes.com, biblegateway.com, classlink.com, usnews.com, ad.gt, wikihow.com,
    amazon.com.br, columbia.edu, ssacdn.com, segment.io, rapid7.com, dnsv1.com, spotifycdn.com, ya.ru, discogs.com,
    vivoglobal.com, jimdo.com, akamaitech.net, mckinsey.com, ebay.de, onet.pl, adroll.com, avito.ru, hotmail.com,
    cedexis-test.com, sharethis.com, businesswire.com, synology.com, typeform.com, kohls.com, wp.pl, plesk.com,
    samsungcloudsolution.net, redd.it, akismet.com, my.com, innovid.com, freefiremobile.com, aiv-delivery.net,
    immunet.com, vkontakte.ru, onesignal.com, cbc.ca, quizlet.com, corriere.it, elmundo.es, smartthings.com,
    ancestry.com, weforum.org, rayjump.com, mediavine.com, nba.com, xerox.com, arxiv.org, binance.com, ip-api.com,
    bytefcdn.com, character.ai, grserver.gr, immedia-semi.com, utorrent.com, ubnt.com, skyhigh.cloud,
    redditstatic.com, tiqcdn.com, asos.com, mongodb.com, realtor.com, flurry.com, wshareit.com, vkuser.net,
    mdpi.com, va.gov, costco.com, macys.com, apnews.com, adgrx.com, adtelligent.com, plex.tv, interia.pl,
    mercadolibre.com.ar, pixiv.net, pexels.com, skroutz.gr, otto.de, 4dex.io, abovedomains.com, ohthree.com,
    eepurl.com, agoda.com, tokopedia.com, xserver.jp, flipkart.com, francetvinfo.fr, expedia.com, bol.com, si.com,
    eporner.com, chartbeat.com, youronlinechoices.com, psychologytoday.com, openstreetmap.org, ubi.com, adobedc.net,
    chess.com, quickconnect.to, split.io, constantcontact.com, msecnd.net, nic.do, creditkarma.com, sportskeeda.com,
    www.gov.br, spankbang.com, withgoogle.com """

    time = timeit.timeit(
        lambda: retrieve_possible_urls_from_unfiltered_input(data),
        number=25
    )
    # some slower machines... It's < 0.1 on a dev machine
    assert time < 0.5

    domains, _ = retrieve_possible_urls_from_unfiltered_input(data)
    assert len(domains) == 1000
    time = timeit.timeit(
        lambda: clean_urls(domains),
        number=25
    )
    assert time < 1.5  # it's 0.102 on a dev machine for 25k


def test_urllists(db, redis_server) -> None:
    account, created = Account.objects.all().get_or_create(name="test")

    list_1 = get_or_create_list_by_name(account, "test list 1")
    list_1_remake = get_or_create_list_by_name(account, "test list 1")
    assert list_1 == list_1_remake

    list_2 = get_or_create_list_by_name(account, "test list 2")
    assert list_1 != list_2

    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 0

    """ We made two lists, so we expect to see two lists returned """
    lists = get_urllists_from_account(account=account)
    assert len(lists) == 2

    """ Should be no problem to add the same urls, it just has not so much effect. """
    added = save_urllist_content_by_name(
        account, "test list 1", {
            'test.nl': {'tags': []}, 'internet.nl': {'tags': []}, 'internetcleanup.foundation': {'tags': []}})
    assert added['added_to_list'] == 3 and added['already_in_list'] == 0 and len(added['incorrect_urls']) == 0

    already = save_urllist_content_by_name(
        account, "test list 1", {
            'test.nl': {'tags': []}, 'internet.nl': {'tags': []}, 'internetcleanup.foundation': {'tags': []}})
    assert already['added_to_list'] == 0 and already['already_in_list'] == 3 and len(already['incorrect_urls']) == 0

    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 3

    """ Garbage urls should be filtered out and can be displayed as erroneous """
    # Impossible to filter out garbage domains, as the tld and domain is checked along the way... and some parts
    # of the domain like 'info' might be seen as a domain while it isn't
    already = save_urllist_content_by_name(account, "test list 1", {
        'test.nonse^': {'tags': []}, 'NONSENSE': {'tags': []}, '127.0.0.1': {'tags': []}})
    assert already['added_to_list'] == 0 and already['already_in_list'] == 0 and len(already['incorrect_urls']) == 0

    """ Check if really nothing was added """
    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 3

    # make sure the url gets deleted from the urllist and not from the database
    urls_in_database = Url.objects.all().count()
    assert urls_in_database == 3

    """ Delete a a urls from the list: """
    url_got_removed_from_list = delete_url_from_urllist(account, list_1.id,
                                                        Url.objects.all().filter(url='test.nl').first().id)

    assert urls_in_database == Url.objects.all().count()

    assert url_got_removed_from_list is True
    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)
    assert len(list_content['urls']) == 2

    """ Delete the entire list, we'll get nothing back, only an empty response. """
    operation_response = delete_list(account=account, user_input={'id': list_1.id})

    # it deletes two urls and the list itself, makes 3
    assert operation_response['success'] is True
    list_content = get_urllist_content(account=account, urllist_id=list_1.pk)

    # deletion is administrative, so the urls are still connected.
    assert len(list_content['urls']) == 2

    account2, created = Account.objects.all().get_or_create(name="test 2")
    """ You cannot delete things from another account """
    operation_response = delete_list(account=account2, user_input={'id': list_1.id})
    assert operation_response['success'] is False

    """ A new list will not be created if there are no urls for it..."""
    added = save_urllist_content_by_name(account, "should be empty", {})
    assert added['added_to_list'] == 0 and added['already_in_list'] == 0 and len(added['incorrect_urls']) == 0

    """ A new list will not be created if there are only nonsensical urls (non valid) for it """
    added = save_urllist_content_by_name(account, "should be empty", {'iuygvb.uighblkj': {'tags': []}})

    list_content = get_urllist_content(account=account, urllist_id=9001)
    assert len(list_content['urls']) == 0

    # list can be renamed
    renamed = rename_list(account=account, list_id=list_2.pk, new_name="A new name")
    assert renamed is True

    # lists can have the same name (does not work with list_1... why not?)
    renamed = rename_list(account=account, list_id=list_2.pk, new_name="A new name")
    assert renamed is True

    # lists can have an awfully long name and that will not be a problem, as it is truncated
    renamed = rename_list(account=account, list_id=list_2.pk, new_name="alksdnalksdnlaksdnlasdknasldknaldnalskndnlaksn"
                                                                       "asdnlkansdlknansldknasldnalkndwlkawdnlkdwanlkn"
                                                                       "aksjdnaksjdndaslkdnlaklwkndlkawndwlakdnwlakkln"
                                                                       "ansdknlaslkdnlaknwdlknkldawnldkwanlkadwnlkdawn"
                                                                       "awdnawklnldndawlkndwalkndaklndwaklnwalkdnwakln"
                                                                       "adlkwndlknawkdlnawldknawlkdnawklndklawnwkalnkn"
                                                                       "awdlknawlkdnawlkdnalwdnawlkdnawkldnalkwndaklwn")
    assert renamed is True


def u(url: str) -> int:
    return Url.objects.all().filter(url=url).first().id


def test_delete_url_from_urllist(db, redis_server):
    a1, _ = Account.objects.all().get_or_create(name="a1")
    a2, _ = Account.objects.all().get_or_create(name="a2")
    l1 = get_or_create_list_by_name(a1, "l1")
    l2 = get_or_create_list_by_name(a2, "l2")
    save_urllist_content_by_name(a1, "l1", {
        'test.nl': {'tags': []}, 'internet.nl': {'tags': []}, 'internetcleanup.foundation': {'tags': []}})
    save_urllist_content_by_name(a2, "l2", {
        'nu.nl': {'tags': []}, 'nos.nl': {'tags': []}, 'tweakers.net': {'tags': []}})

    assert l1 != l2
    assert a1 != a2

    assert Url.objects.all().count() == 6

    assert True is delete_url_from_urllist(a1, l1.id, u('test.nl'))
    # double delete results into nothing
    assert False is delete_url_from_urllist(a1, l1.id, u('test.nl'))
    # a2 cannot delete something from the lists of a1, even if the url exist in the list from l1
    assert False is delete_url_from_urllist(a2, l1.id, u('test.nl'))
    # no crash on non-existing id's:
    assert False is delete_url_from_urllist(a1, 990000, u('test.nl'))
    assert False is delete_url_from_urllist(a1, l1.id, 9990000)

    assert Url.objects.all().count() == 6
