# SPDX-License-Identifier: Apache-2.0
from django.core.files.uploadedfile import UploadedFile

from dashboard.internet_nl_dashboard.logic.domain_batches import BatchQueueUnavailable, start_batch
from dashboard.internet_nl_dashboard.logic.spreadsheet import (
    SpreadsheetStorageUnavailable,
    UploadHistoryItemSchema,
    get_upload_history,
)
from dashboard.internet_nl_dashboard.models import Account, DashboardUser
from dashboard.internet_nl_dashboard.problems import raises


@raises(SpreadsheetStorageUnavailable, BatchQueueUnavailable)
def start_spreadsheet_upload(user: DashboardUser, file: UploadedFile) -> dict:
    return start_batch(user, file=file)


def upload_history_for_account(account: Account) -> list[UploadHistoryItemSchema]:
    return get_upload_history(account)
