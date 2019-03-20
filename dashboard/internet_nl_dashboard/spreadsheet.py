import logging
import os
import re
from datetime import datetime

import magic
import pyexcel as p
import pytz
from django.db import transaction
from xlrd import XLRDError

from dashboard.internet_nl_dashboard.models import UploadLog
from dashboard.internet_nl_dashboard.urllist_management import save_urllist_content

log = logging.getLogger(__package__)


SPREADSHEET_MIME_TYPES = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'application/vnd.oasis.opendocument.spreadsheet',

    # magic thinks ms spreadsheets are application/octet-stream, which is basically everything...
    'application/octet-stream']

ALLOWED_SPREADSHEET_EXTENSIONS = ['xlsx', 'xls', 'ods']


def is_file(file):
    if not os.path.isfile(file):
        log.debug('Not a valid file path.')
        return False
    return True


# make sure the file is of a spreadsheet type
def is_valid_mimetype(file):
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


def is_valid_extension(file):
    """
    Checks if the file has an extension that is allowed.

    :param file:
    :return:
    """

    if file.split(".")[-1] in ALLOWED_SPREADSHEET_EXTENSIONS:
        return True
    log.debug('Not a valid extension.')
    return False


def validate(file):
    # ordered from cheap to expensive checks
    if is_file(file) and is_valid_extension(file) and is_valid_mimetype(file):
        return True
    return False


def get_data(file):
    """
    Will return a simple set of data, without too much validation. Deduplicates data per unique category.

    data{'category': set('url1, url2')}

    Compound records are decompounded and placed in the correct categories. Below might result in four additions:
    category, category - url, url

    :param file:
    :return:
    """

    data = {}

    try:
        sheet = p.get_sheet(file_name=file, name_columns_by_row=0)
    except XLRDError:
        # xlrd.biffh.XLRDError: Unsupported format, or corrupt file: Expected BOF record; found b'thisfile'
        return data

    # Skips the first entry
    for row in sheet:
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

    # todo: test, if there is only a category, but no urls, do not add the category.
    # for example: mixed datatypes has no urls, ... it contains something but it's not valid...
    # ... perhaps that test has to be done elsewhere ... in the save_urllist_content i guess.
    # todo: get todo log from pycharm.

    # usually comes with some empty records as well. Destroy those:
    if '' in data:
        data.pop('')

    p.free_resources()

    return data


def get_upload_history(account):

    uploads = UploadLog.objects.all().filter(user__account=account).order_by('-pk')[0:3]
    data = []

    for upload in uploads:
        data.append({
            'original_filename': upload.original_filename,
            'message': upload.message,
            'upload_date': upload.upload_date,
            'filesize': upload.filesize
        })

    return data


def log_spreadsheet_upload(user, file: str, message: str = ""):
    """
    This helps content editors to see and verify what spreadsheets they have uploaded. Especially for bulk updates
    this can be very useful. Especially the filesize.

    :return:
    """

    # waterschappen_gucvVcD.xlsx or waterschappen.xlsx
    # https://regex101.com/, regex = "_[a-zA-Z0-9]{7,7}\."
    internal_filename = file.split('/')[-1]

    # the 8 random letters and numbers + possible file extension
    regex = r"_[a-zA-Z0-9]{7,7}\.[xlsod]{3,4}"

    if re.findall(regex, internal_filename):
        original_filename = re.sub(regex, "", internal_filename) + '.' + file.split('.')[-1]
    else:
        original_filename = internal_filename

    upload = {'user': user,
              'original_filename': original_filename,
              'internal_filename': internal_filename,
              'message': message,
              'upload_date': datetime.now(pytz.utc),
              'filesize': os.path.getsize(file)}

    uploadlog = UploadLog(**upload)
    uploadlog.save()

    return upload

# Do not accept partial imports. Or all, or nothing in a single transaction.
@transaction.atomic
def save_data(account, data):

    results = {}
    for urllist in data.keys():
        results[urllist] = save_urllist_content(account, urllist, data[urllist])

    return results
