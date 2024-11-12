import requests
import tldextract
from constance import config

from dashboard.internet_nl_dashboard.logic.domains import log


def suggest_subdomains(domain: str, period: int = 370):
    extract = tldextract.extract(domain)

    # ip address or garbage
    if not extract.domain or not extract.suffix:
        return []

    # call SUBDOMAIN_SUGGESTION_SERVER_ADDRESS
    response = requests.get(
        config.SUBDOMAIN_SUGGESTION_SERVER_ADDRESS,
        params={"domain": extract.domain, "suffix": extract.suffix, "period": period},
        timeout=10,
    )

    if response.status_code != 200:
        log.error("Failed to retrieve subdomain suggestions from  %s.", config.SUBDOMAIN_SUGGESTION_SERVER_ADDRESS)
        return []

    return response.json()
