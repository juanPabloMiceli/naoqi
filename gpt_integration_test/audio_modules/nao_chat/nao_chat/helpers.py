import json
from typing import Dict, List, Union

import requests
import tiktoken
import logging
import re
import datetime as dt


def get_json(string: str) -> Dict[str, str]:
    """
    Gets the json of the given string

    Parameters
    ----------
    string : str
        A string with a json

    Returns
    -------
    Dict[str, str]
        The extracted json
    """
    # check if ithas an embedded json (detailed by having a " char before its bracket)
    json_object = None

    if "{" in string and "}" in string:
        stats_re = re.compile("{.+?\}", re.MULTILINE | re.DOTALL)
        for match in stats_re.findall(string):
            json_object = match
        if json_object is None:
            raise ValueError
        else:
            json_object = json.loads(json_object)
        return json_object
    else:
        raise ValueError


def count_tokens_of_messages(messages: List[Dict[str, str]], model: str) -> int:
    """Returns the number of tokens used by a list of messages."""
    tokens_per_message, tokens_per_name = 0, 0
    if "gpt-3.5-turbo" in model:
        model = "gpt-3.5-turbo-0301"
        tokens_per_message = 4
        tokens_per_name = -1
    elif "gpt-4" in model:
        model = "gpt-4-0314"
        tokens_per_message = 3
        tokens_per_name = 1
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logging.error("Warning: model not found. Using cl100k_base encoding.")
    except:
        raise NotImplementedError(
            f"""count_tokens_of_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )

    tokens_messages = [
        len(encoding.encode(value))
        if key != "name"
        else len(encoding.encode(value)) + tokens_per_name
        for message in messages
        for key, value in message.items()
    ]
    num_tokens = sum(tokens_messages) + len(messages) * tokens_per_message + 3
    logging.info(f"Calculated tokens: {num_tokens}")
    return num_tokens


def log_usage(usage: Dict[int, float]):
    logging.info(f"usage data saved")


def read_text_file(path: str) -> str:
    try:
        with open(path, mode="r") as file:
            content = file.read()
    except FileNotFoundError:
        logging.debug(f"{path} was not found")
    return content


def basic_date_parse(possible_date_str: str) -> Union[dt.date, None]:
    """
    A basic date parser that returns null if the parse failed.
    Use for nullable date variables on chatbots functions

    Parameters
    ----------
    possible_date_str : str
        A possible date string

    Returns
    -------
    Union[datetime.Date, None]
        A date or None
    """
    try:
        return dt.datetime.strptime(possible_date_str, "%Y-%m-%d")
    except:
        return None
