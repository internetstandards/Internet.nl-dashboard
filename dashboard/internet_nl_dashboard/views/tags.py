# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.decorators import login_required
from ninja import Router, Schema

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.logic.tags import add_tag, remove_tag, tags_in_urllist
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account

router = Router(tags=["Url Lists / Tags"])


class TagChangeInputSchema(Schema):
    urllist_id: int
    url_ids: list[int]
    tag: str


@router.post("/add", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def add_tag_api(request, data: TagChangeInputSchema):
    add_tag(
        account=get_account(request),
        urllist_id=data.urllist_id,
        url_ids=data.url_ids,
        tag=data.tag,
    )
    return operation_response(success=True)


@router.post("/remove", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def remove_tag_api(request, data: TagChangeInputSchema):
    remove_tag(
        account=get_account(request),
        urllist_id=data.urllist_id,
        url_ids=data.url_ids,
        tag=data.tag,
    )
    return operation_response(success=True)


@router.get("/list/{urllist_id}", response={200: list[str]})
@login_required(login_url=LOGIN_URL)
def tags_in_urllist_api(request, urllist_id: int):
    return tags_in_urllist(account=get_account(request), urllist_id=urllist_id)
