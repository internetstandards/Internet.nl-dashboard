# SPDX-License-Identifier: Apache-2.0
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
import zipfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

import magic
import pyexcel as p
from actstream import action
from constance import config
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from xlrd import XLRDError

from dashboard.internet_nl_dashboard.logic.domains import (_add_to_urls_to_urllist, clean_urls,
                                                           retrieve_possible_urls_from_unfiltered_input,
                                                           save_urllist_content_by_name)
from dashboard.internet_nl_dashboard.models import Account, DashboardUser, UploadLog, UrlList

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
    'text/csv',
]

ALLOWED_SPREADSHEET_EXTENSIONS: List[str] = ['xlsx', 'xls', 'ods', 'csv']


def is_file(file: str) -> bool:
    if not os.path.isfile(file):
        log.debug('Not a valid file path.')
        return False
    return True


def save_file(myfile) -> str:
    # todo: filesystem might be full.
    # https://docs.djangoproject.com/en/2.1/ref/files/storage/
    file_system_storage = FileSystemStorage(location=settings.MEDIA_ROOT)
    filename = file_system_storage.save(myfile.name, myfile)
    file = settings.MEDIA_ROOT + '/' + filename
    return file


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
    log.debug(f'{mimetype} is not a valid mime type.')
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


def get_data(file: str) -> Dict[str, Dict[str, Dict[str, list]]]:
    """
    Will return a simple set of data, without too much validation. Deduplicates data per unique category.

    data{'category': set('url1, url2')}

    Compound records are decompounded and placed in the correct categories. Below might result in four additions:
    category, category - url, url

    Example:
    data["mylistname"]["mydomain.com"]["tags"] = {"tag1", "tag2"}

    :param file:
    :return:
    """

    data: Dict[str, Any] = {}

    try:
        sheet = p.get_sheet(file_name=file, name_columns_by_row=0)
    except XLRDError:
        # xlrd.biffh.XLRDError: Unsupported format, or corrupt file: Expected BOF record; found b'thisfile'
        return data
    except zipfile.BadZipFile:
        # the corrupted file in the unit tests
        return data
    except Exception as exc:  # pylint: disable=broad-except
        log.exception(exc)
        return data

    # Skips the first entry
    for row in sheet:
        # Do not handle CSV files that only contain urls on a newline. Return nothing.
        if len(row) < 2:
            continue

        # Data is parsed to python-like datatype. In this case we only expect strings and cast them as such.
        found_categories = str(row[0]).lower().strip().split(',')
        found_urls = str(row[1]).lower().strip().split(',')
        found_tags = []
        # if there is no tag column:
        if len(row) > 2:
            found_tags = str(row[2]).lower().strip().split(',')

        for found_category in found_categories:
            found_category = found_category.strip()

            for found_url in found_urls:
                found_url = found_url.strip()

                # create new category
                if found_category not in data:
                    data[found_category] = {}

                # use a list because a set is not json serializable:
                if found_url not in data[found_category]:
                    data[found_category][found_url] = {'tags': []}

                for tag in found_tags:
                    # not use a set here, while that would save a line of code to support serialization
                    if tag not in data[found_category][found_url]['tags']:
                        data[found_category][found_url]['tags'].append(tag)

    # During editing, it might happen there are some 'left over' cells that are also added.
    # These left overs contain no urls. If they do, and something has been attempted to be added to
    # 'empty', it is discarded. We require urls to be in a list / category.
    if '' in data:
        data.pop('')

    p.free_resources()

    return data


def get_upload_history(account: Account) -> List:
    uploads = UploadLog.objects.all().filter(user__account=account).order_by('-pk')
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
              'upload_date': datetime.now(timezone.utc),
              'filesize': os.path.getsize(file)}

    uploadlog = UploadLog(**upload)
    uploadlog.save()

    # Sprinkling an activity stream action.
    action.send(user, verb='uploaded spreadsheet', target=uploadlog, public=False)

    return upload


# Do not accept partial imports. Or all, or nothing in a single transaction.
# Depending on the speed this needs to become a task, as the wait will be too long.
@transaction.atomic
def save_data(account: Account, data: Dict[str, Dict[str, Dict[str, set]]]):
    return {
        urllist: save_urllist_content_by_name(account, urllist, data[urllist])
        for urllist in data
    }


def upload_error(message, user, file) -> Dict[str, Any]:
    response: Dict[str, Any] = {'error': True, 'success': False, 'message': message, 'details': {}, 'status': 'error'}
    log_spreadsheet_upload(user=user, file=file, status=response['status'], message=response['message'])
    return response


def inspect_upload_file(user: DashboardUser, file: str) -> Optional[Dict[str, Any]]:
    # use more verbose validation, to give better feedback.
    if not is_file(file):
        return upload_error("Uploaded file was not found. I might be not stored due to a full disk or or has been "
                            "stored in the wrong location, or has been deleted automatically by a background "
                            "process like a virus scanner.", user, file)

    if not is_valid_extension(file):
        return upload_error("File does not have a valid extension. "
                            f"Allowed extensions are: {','.join(ALLOWED_SPREADSHEET_EXTENSIONS)}.", user, file)

    if not is_valid_mimetype(file):
        return upload_error("The content of the file could not be established. It might not be a spreadsheet file.",
                            user, file)

    return None


def get_data_from_spreadsheet(
        user: DashboardUser, file: str
) -> Union[Tuple[Dict[str, Dict[str, Dict[str, list]]], int], Tuple[Dict[str, Any], str]]:
    has_errors = inspect_upload_file(user, file)
    if has_errors:
        return has_errors, "error"

    # urllist: urls
    domain_lists: Dict[str, Dict[str, Dict[str, list]]] = get_data(file)
    if not domain_lists:
        return upload_error("The uploaded file contained no data. This might happen when the file is not in the "
                            "correct format. Are you sure it is a correct spreadsheet file?", user, file), "error"

    # sanity check on data length and number of lists (this does not prevent anyone from trying to upload the same
    # file over and over again), it's just a usability feature against mistakes.
    number_of_urls = sum(len(urls) for _, urls in domain_lists.items())

    if len(domain_lists) > config.DASHBOARD_MAXIMUM_LISTS_PER_SPREADSHEET:
        return upload_error(f"The maximum number of new lists is {config.DASHBOARD_MAXIMUM_LISTS_PER_SPREADSHEET}. "
                            "The uploaded spreadsheet contains more than this limit. Try again in smaller batches.",
                            user, file), "error"

    if number_of_urls > config.DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET:
        return upload_error(f"The maximum number of new urls is {config.DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET}."
                            "The uploaded spreadsheet contains more than this limit. Try again in smaller batches.",
                            user, file), "error"

    for urllist, urls in domain_lists.items():
        possible_urls, _ = retrieve_possible_urls_from_unfiltered_input(", ".join(urls))
        url_check = clean_urls(possible_urls)

        if url_check['incorrect']:
            return upload_error("This spreadsheet contains urls that are not in the correct format. Please correct "
                                "them and try again. The first list that contains an error is "
                                f"{urllist} with the url(s) {', '.join(url_check['incorrect'])}",
                                user, file), "error"

    return domain_lists, number_of_urls


def complete_import(user: DashboardUser, file: str) -> Dict[str, Any]:
    domain_lists, number_of_urls = get_data_from_spreadsheet(user, file)
    if number_of_urls == "error":
        return domain_lists

    # File system full, database full.
    details = save_data(user.account, domain_lists)

    # Make the details a little bit easier for humans to understand:
    details_str = ""
    for urllist, detail in details.items():
        details_str += f"{urllist}: new: {detail['added_to_list']}, existing: {detail['already_in_list']}; "

    message = "Spreadsheet uploaded successfully. " \
              f"Added {len(domain_lists)} lists and {number_of_urls} urls. Details: {details_str}"
    response = {'error': False, 'success': True, 'message': message, 'details': details, 'status': 'success'}
    log_spreadsheet_upload(user=user, file=file, status='success', message=message)
    return response


def upload_domain_spreadsheet_to_list(account: Account, user: DashboardUser, urllist_id: int, file: str):

    file = save_file(file)

    domain_lists, number_of_urls = get_data_from_spreadsheet(user, file)
    if number_of_urls == "error":
        return domain_lists

    urllist = UrlList.objects.all().filter(id=urllist_id, account=account).first()
    if not urllist:
        return {'error': True, 'success': False, 'message': 'list_does_not_exist', 'details': '', 'status': 'error'}

    # the spreadsheet content is leading, this means that anything in the current list, including tags, will
    # be removed. There is no smart merging strategy here. This might be added in the future: where we look
    # at what is already in the list and only add changes.
    # this will also remove the tags on this list automatically, without touching other lists that have the same
    # url and different tags.
    urllist.urls.clear()

    # we don't care about the list name, we'll just add anything that is given as input...
    result = {'incorrect_urls': [],
              'added_to_list': 0,
              'already_in_list': 0}
    for _, domain_data in domain_lists.items():
        log.debug(domain_data)
        # todo: when a tag has a domain, it might be added as a domain, which is wrong. Only use the first
        #  column of uploaded data.
        extracted_urls, _ = retrieve_possible_urls_from_unfiltered_input(", ".join(domain_data))
        cleaned_urls = clean_urls(extracted_urls)

        if cleaned_urls['correct']:
            counters = _add_to_urls_to_urllist(account, urllist, urls=cleaned_urls['correct'],
                                               urls_with_tags_mapping=domain_data)
        else:
            counters = {'added_to_list': 0, 'already_in_list': 0}

        result['added_to_list'] += counters['added_to_list']
        result['already_in_list'] += counters['already_in_list']
        result['incorrect_urls'] += cleaned_urls['incorrect']

    details_str = f"{urllist.name}: new: {result['added_to_list']}, existing: {result['already_in_list']}; "
    message = "Spreadsheet uploaded successfully. " \
              f"Added {len(domain_lists)} lists and {number_of_urls} urls. Details: {details_str}"
    log_spreadsheet_upload(user=user, file=file, status='success', message=message)
    return {'error': False, 'success': True, 'message': message, 'details': details_str, 'status': 'success'}
