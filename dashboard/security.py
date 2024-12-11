# SPDX-License-Identifier: Apache-2.0
from django.conf import settings


def confirm_keys_are_changed():
    if not settings.DEBUG and settings.SECRET_KEY == "_dzlo^9d#ox6!7c9rju@=u8+4^sprqocy3s*l*ejc2yr34@&98":  # nosec
        raise ValueError("SECRET_KEY contains a debugging value. Set a sane secret key.")

    if not settings.DEBUG and settings.FIELD_ENCRYPTION_KEY == b"JjvHNnFMfEaGd7Y0SAHBRNZYGGpNs7ydEp-ixmKSvkQ=":  # nosec
        raise ValueError(
            "FIELD_ENCRYPTION_KEY has to be configured on the OS level, and needs to be different than the "
            "default key provided. Please create a new key. Instructions are listed here:"
            "https://github.com/pyca/cryptography. In short, run: key = Fernet.generate_key()"
        )
