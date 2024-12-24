from typing import Generator

from transformers import AutoTokenizer

def split_user_full_name(user: str | None) -> tuple[str, str]:
    if user is None:
        raise Exception("User name is empty")

    name_tokens = user.split(" ")
    if len(name_tokens) == 0:
        raise Exception("User name is empty")
    elif len(name_tokens) == 1:
        first_name, last_name = name_tokens[0], name_tokens[0]
    else:
        first_name, last_name = " ".join(name_tokens[:-1]), name_tokens[-1]

    return first_name, last_name

def flatten(nested_list: list) -> list:
    """Flatten a list of lists into a single list."""

    return [item for sublist in nested_list for item in sublist]


def batch(list_: list, size: int) -> Generator[list, None, None]:
    yield from (list_[i : i + size] for i in range(0, len(list_), size))