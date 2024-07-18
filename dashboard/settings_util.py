import os

from cryptography.fernet import Fernet
from django.core.management.utils import get_random_secret_key

# These secret keys are defaults and will not work as confirm_keys_are_changed will check if these are changed.
DEFAULT_SECRET_KEY = '_dzlo^9d#ox6!7c9rju@=u8+4^sprqocy3s*l*ejc2yr34@&98'  # nosec
DEFAULT_FIELD_ENCRYPTION_KEY = "JjvHNnFMfEaGd7Y0SAHBRNZYGGpNs7ydEp-ixmKSvkQ="  # nosec


def get_secret_key_from_file_or_env() -> str:
    """Will read secret key from file is SECRET_KEY_FILE env var is provided,
    creating a keyfile is one is not present yet. Otherwise will read from
    SECRET_KEY env or fallback to default key."""

    if secret_key_file := os.environ.get('SECRET_KEY_FILE', None):
        if not os.path.exists(secret_key_file):
            secret_key = get_random_secret_key()
            with open(secret_key_file, 'w+', encoding="UTF-8") as f:
                f.write(secret_key)

        with open(secret_key_file, 'r', encoding="UTF-8") as f:
            secret_key = f.readline().strip()
    else:
        # SECURITY WARNING: keep the secret key used in production secret!
        # The routine confirm_keys_are_changed is run in production and will prevent the default keys to be used.
        secret_key: str = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)

    return secret_key


def get_field_encryption_key_from_file_or_env() -> bytes:
    """Will read field encryption key from file is FIELD_ENCRYPTION_KEY_FILE env var is provided,
    creating a keyfile is one is not present yet. Otherwise will read from
    FIELD_ENCRYPTION_KEY env or fallback to default key."""

    if field_encryption_key_file := os.environ.get('FIELD_ENCRYPTION_KEY_FILE', None):
        if not os.path.exists(field_encryption_key_file):
            field_encryption_key: bytes = Fernet.generate_key()
            # Binary mode doesn't take an encoding argument
            with open(field_encryption_key_file, 'wb+') as f:
                f.write(field_encryption_key)

        with open(field_encryption_key_file, 'rb') as f:
            field_encryption_key: bytes = f.readline().strip()
    else:
        # Note that this key is not stored in the database, that would be a security risk.
        # The key can be generated with the following routine:
        # https://cryptography.io/en/latest/fernet/
        # from cryptography.fernet import Fernet
        # Fernet.generate_key()
        # Make sure you remove the b' and ' from the string, so you're working with a string.
        # For example: b'JjvHNnFMfEaGd7Y0SAHBRNZYGGpNs7ydEp-ixmKSvkQ=' becomes
        # JjvHNnFMfEaGd7Y0SAHBRNZYGGpNs7ydEp-ixmKSvkQ=
        # Also note that on the production server a different key is required, otherwise the server will not start.
        # See dashboard_prdserver for more details.
        # The routine confirm_keys_are_changed is run in production and will prevent the default keys to be used.
        field_encryption_key: bytes = os.environ.get('FIELD_ENCRYPTION_KEY', DEFAULT_FIELD_ENCRYPTION_KEY).encode()

    return field_encryption_key
