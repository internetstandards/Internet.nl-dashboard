# SPDX-License-Identifier: Apache-2.0
import logging

from django.contrib.auth.decorators import login_required
from ninja import Router

from dashboard.internet_nl_dashboard.scanners.subdomains import request_scan, scan_status
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account

log = logging.getLogger(__package__)

# Ninja router for subdomain discovery operations
router = Router(tags=["Url Lists / Discover Subdomains"])


@router.post("/{urllist_id}")
@login_required(login_url=LOGIN_URL)
def request_subdomain_discovery_scan_api(request, urllist_id: int):
    """Request a subdomain discovery scan for a given URL list."""
    return request_scan(get_account(request), urllist_id)


@router.get("/status/{urllist_id}")
@login_required(login_url=LOGIN_URL)
def subdomain_discovery_scan_status_api(request, urllist_id: int):
    """Get the status of the latest subdomain discovery scan for a given URL list."""
    return scan_status(get_account(request), urllist_id)
