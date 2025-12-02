# SPDX-License-Identifier: Apache-2.0
from ninja import Schema


class ErrorResponseSchema(Schema):
    message: str


class SuccessResponseSchema(Schema):
    """Empty success envelope for cases where no payload is needed."""
