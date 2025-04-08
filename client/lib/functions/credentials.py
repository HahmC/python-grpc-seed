import os
from typing import AnyStr


def _load_credential_from_file(filepath: str) -> AnyStr:
    """
    Load credentials from the given filepath

    :param filepath: filepath of credential
    :return: credential
    """
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, "rb") as f:
        return f.read()