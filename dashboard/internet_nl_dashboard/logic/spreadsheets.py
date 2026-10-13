# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any

from celery import group
from django.core.files.uploadedfile import UploadedFile
from kombu.exceptions import OperationalError

from dashboard.internet_nl_dashboard.logic.spreadsheet import (
    SpreadsheetStorageUnavailable,
    UploadHistoryItemSchema,
    get_upload_history,
    import_step_2,
    log_spreadsheet_upload,
    save_file,
    update_spreadsheet_upload,
)
from dashboard.internet_nl_dashboard.models import Account, DashboardUser
from dashboard.internet_nl_dashboard.problems import DocumentedApiError, ProblemType, raises

log = logging.getLogger(__name__)


class SpreadsheetQueueUnavailable(DocumentedApiError):
    status = 503
    detail = "The spreadsheet import queue is temporarily unavailable. Please try again later."
    problem_type = ProblemType.SPREADSHEET_QUEUE_UNAVAILABLE


@raises(SpreadsheetStorageUnavailable, SpreadsheetQueueUnavailable)
def start_spreadsheet_upload(user: DashboardUser, file: UploadedFile) -> dict:
    """
    Save the uploaded file and enqueue parsing/import. Returns the upload log id.
    """
    saved_file = save_file(file)

    upload_data: dict[str, Any] = log_spreadsheet_upload(
        user=user,
        file=saved_file,
        status="[1/3] Initializing",
        message="[1/3] Initializing upload...",
    )
    uploadlog_id = upload_data.get("id")

    try:
        group(import_step_2.si(user.id, saved_file, uploadlog_id)).apply_async()
    except OperationalError as exc:
        log.exception("The spreadsheet import queue is temporarily unavailable")
        update_spreadsheet_upload(uploadlog_id, status="error", message=SpreadsheetQueueUnavailable.detail)
        raise SpreadsheetQueueUnavailable() from exc

    return {"uploadlog_id": uploadlog_id}


def upload_history_for_account(account: Account) -> list[UploadHistoryItemSchema]:
    return get_upload_history(account)
