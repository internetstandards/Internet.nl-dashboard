# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any

from celery import group
from django.core.files.uploadedfile import UploadedFile

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.logic.spreadsheet import (
    UploadHistoryItemSchema,
    get_upload_history,
    import_step_2,
    log_spreadsheet_upload,
    save_file,
)
from dashboard.internet_nl_dashboard.models import Account, DashboardUser

log = logging.getLogger(__name__)


def start_spreadsheet_upload(user: DashboardUser, file: UploadedFile) -> OperationResponseSchema:
    """
    Save the uploaded file and enqueue parsing/import. Returns an operation response with the upload log id.
    """
    try:
        saved_file = save_file(file)
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("Failed to save uploaded spreadsheet", exc_info=exc)
        return operation_response(error=True, message="upload_save_failed")

    upload_data: dict[str, Any] = log_spreadsheet_upload(
        user=user,
        file=saved_file,
        status="[1/3] Initializing",
        message="[1/3] Initializing upload...",
    )
    uploadlog_id = upload_data.get("id")

    group(import_step_2.si(user.id, saved_file, uploadlog_id)).apply_async()

    return operation_response(
        success=True,
        message="upload_started",
        data={"uploadlog_id": uploadlog_id},
    )


def upload_history_for_account(account: Account) -> list[UploadHistoryItemSchema]:
    return get_upload_history(account)
