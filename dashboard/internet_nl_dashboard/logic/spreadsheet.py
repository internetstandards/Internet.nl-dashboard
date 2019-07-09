"""
Handles spreadsheet uploads.

About spreadsheet sizes:
10.000 urls in a test came down to 51 kilobytes (many of the same urls, is compressed).
10.000 unique urls is 80 kilobytes. We don't need to change the upload size to something larger than 2MB.

Types supported through pyexcel: xlsx, xls, ods.

DONE: handle file uploads
DONE: validation (as far as that goes)
DONE: support ods
DONE: support xls, xlsx
DONE: support CSV
Removed: support JSON.
DONE: give example files.
DONE: supply example download files.
"""

import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List

import magic
import pyexcel as p
import pytz
from django.db import transaction
from xlrd import XLRDError

from dashboard.internet_nl_dashboard.logic.domains import clean_urls, save_urllist_content_by_name
from dashboard.internet_nl_dashboard.models import Account, DashboardUser, UploadLog

log = logging.getLogger(__package__)


SPREADSHEET_MIME_TYPES: List[str] = [
    # XLSX
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',

    # XLS
    'application/vnd.ms-excel',

    # ODS
    'application/vnd.oasis.opendocument.spreadsheet',

    # magic thinks ms spreadsheets are application/octet-stream, which is basically everything...
    # XLSX / XLS
    'application/octet-stream',

    # csv
    # https://stackoverflow.com/questions/7076042/what-mime-type-should-i-use-for-csv
    'text/plain',
    'text/x-csv',
]

ALLOWED_SPREADSHEET_EXTENSIONS: List[str] = ['xlsx', 'xls', 'ods', 'csv']

# Anything more than this cannot be uploaded in a single spreadsheet. It can be in multiple.
# In normal usecases these limits will not be reached.
MAXIMUM_AMOUNT_OF_NEW_LISTS: int = 200
MAXIMUM_AMOUNT_OF_NEW_URLS: int = 10000


def is_file(file: str) -> bool:
    if not os.path.isfile(file):
        log.debug('Not a valid file path.')
        return False
    return True


# make sure the file is of a spreadsheet type
def is_valid_mimetype(file: str) -> bool:
    """
    Has system dependencies when not working under linux. Make sure those dependencies are installed.

    Read more:
    https://github.com/ahupp/python-magic

    :param file:
    :return:
    """
    mime = magic.Magic(mime=True)
    mimetype = mime.from_file(file)

    if mimetype in SPREADSHEET_MIME_TYPES:
        return True
    log.debug('Not a valid mime type.')
    return False


def is_valid_extension(file: str) -> bool:
    """
    Checks if the file has an extension that is allowed.

    :param file:
    :return:
    """

    if file.split(".")[-1] in ALLOWED_SPREADSHEET_EXTENSIONS:
        return True
    log.debug('Not a valid extension.')
    return False


def get_data(file: str) -> dict:
    """
    Will return a simple set of data, without too much validation. Deduplicates data per unique category.

    data{'category': set('url1, url2')}

    Compound records are decompounded and placed in the correct categories. Below might result in four additions:
    category, category - url, url

    :param file:
    :return:
    """

    data: Dict[str, set] = {}

    try:
        sheet = p.get_sheet(file_name=file, name_columns_by_row=0)
    except XLRDError:
        # xlrd.biffh.XLRDError: Unsupported format, or corrupt file: Expected BOF record; found b'thisfile'
        return data

    # Skips the first entry
    for row in sheet:
        # Do not handle CSV files that only contain urls on a newline. Return nothing.
        if len(row) < 2:
            continue

        # Data is parsed to python-like datatype. In this case we only expect strings and cast them as such.
        found_categories = str(row[0]).lower().strip().split(',')
        found_urls = str(row[1]).lower().strip().split(',')

        for found_category in found_categories:
            found_category = found_category.strip()

            for found_url in found_urls:
                found_url = found_url.strip()

                # create new category
                if found_category not in data:
                    data[found_category] = set()

                data[found_category].add(found_url)

    # During editing, it might happen there are some 'left over' cells that are also added.
    # These left overs contain no urls. If they do, and something has been attempted to be added to
    # 'empty', it is discarded. We require urls to be in a list / category.
    if '' in data:
        data.pop('')

    p.free_resources()

    return data


def get_upload_history(account: Account) -> List:

    uploads = UploadLog.objects.all().filter(user__account=account).order_by('-pk')[0:3]
    data = []

    for upload in uploads:
        data.append({
            'original_filename': upload.original_filename,
            'message': upload.message,
            'upload_date': upload.upload_date,
            'filesize': upload.filesize,
        })

    return data


def log_spreadsheet_upload(user: DashboardUser, file: str, status: str = "", message: str = "") -> dict:
    """
    This helps content editors to see and verify what spreadsheets they have uploaded. Especially for bulk updates
    this can be very useful. Especially the filesize.

    :return:
    """

    # waterschappen_gucvVcD.xlsx or waterschappen.xlsx
    # https://regex101.com/, regex = "_[a-zA-Z0-9]{7,7}\."
    internal_filename = file.split('/')[-1]

    # the 8 random letters and numbers + possible file extension
    regex = r"_[a-zA-Z0-9]{7,7}\.[xlsodcsv]{3,4}"

    if re.findall(regex, internal_filename):
        original_filename = re.sub(regex, "", internal_filename) + '.' + file.split('.')[-1]
    else:
        original_filename = internal_filename

    upload = {'user': user,
              'original_filename': original_filename[0:250],
              'internal_filename': internal_filename[0:250],
              'status': status[0:250],
              'message': message[0:250],
              'upload_date': datetime.now(pytz.utc),
              'filesize': os.path.getsize(file)}

    uploadlog = UploadLog(**upload)
    uploadlog.save()

    return upload


# Do not accept partial imports. Or all, or nothing in a single transaction.
# Depending on the speed this needs to become a task, as the wait will be too long.
@transaction.atomic
def save_data(account: Account, data: dict):

    results = {}
    for urllist in data.keys():
        results[urllist] = save_urllist_content_by_name(account, urllist, data[urllist])

    return results


def complete_import(user: DashboardUser, file: str):

    response: Dict[str, Any] = {'error': False, 'success': False, 'message': '', 'details': {}}

    # use more verbose validation, to give better feedback.
    if not is_file(file):
        response['error'] = True
        response['status'] = 'error'
        response['message'] = "Uploaded file was not found. I might be not stored due to a full disk or or has been " \
                              "stored in the wrong location, or has been deleted automatically by a background " \
                              "process like a virus scanner."
        log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
        return response

    if not is_valid_extension(file):
        response['error'] = True
        response['status'] = 'error'
        response['message'] = "File does not have a valid extension. Allowed extensions are: %s." % (
            ' '.join(ALLOWED_SPREADSHEET_EXTENSIONS))
        log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
        return response

    if not is_valid_mimetype(file):
        response['error'] = True
        response['status'] = 'error'
        response['message'] = "The content of the file could not be established. It might not be a spreadsheet file."
        log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
        return response

    data = get_data(file)
    if not data:
        response['error'] = True
        response['status'] = 'error'
        response['message'] = "The uploaded file contained no data. This might happen when the file is not in the " \
                              "correct format. Are you sure it is a correct spreadsheet file?"
        log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
        return response

    # sanity check on data length and number of lists (this does not prevent anyone from trying to upload the same
    # file over and over again), it's just a usability feature against mistakes.
    number_of_lists = len(data.keys())
    number_of_urls = 0
    for urllist in data.keys():
        number_of_urls += len(data[urllist])

    if number_of_lists > MAXIMUM_AMOUNT_OF_NEW_LISTS:
        response['error'] = True
        response['status'] = 'error'
        response['message'] = "The maximum number of new lists is %s. The uploaded spreadsheet contains more than " \
                              "this limit. Try again in smaller batches."
        log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
        return response

    if number_of_lists > MAXIMUM_AMOUNT_OF_NEW_URLS:
        response['error'] = True
        response['status'] = 'error'
        response['message'] = "The maximum number of new urls is %s. The uploaded spreadsheet contains more than " \
                              "this limit. Try again in smaller batches."
        log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
        return response

    # Here is your standard XSS issue :)
    for urllist in data.keys():
        url_check = clean_urls(list(data[urllist]))

        if url_check['incorrect']:
            response['error'] = True
            response['status'] = 'error'
            response['message'] = "This spreadsheet contains urls that are not in the correct format. Please correct " \
                                  "them and try again. " \
                                  "The fist list that contains an error is %s with the url(s) %s" % (
                urllist, ', '.join(url_check['incorrect']))
            log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
            return response

    # File system full, database full.
    details = save_data(user.account, data)

    response['success'] = True
    response['status'] = 'success'
    response['details'] = details

    # Make the details a little bit easier for humans to understand:
    details_str = ""
    for urllist in details.keys():
        details_str += "%s: new: %s, existing: %s; " % (urllist, details[urllist]['added_to_list'],
                                                        details[urllist]['already_in_list'])

    response['message'] = "Spreadsheet uploaded successfully. Added %s lists and %s urls. Details: %s" % (
        number_of_lists, number_of_urls, details_str)
    log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
    return response
