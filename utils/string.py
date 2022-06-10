import re
from typing import Union


def extract_hashtags(text: str) -> Union[list[str], None]:
    if not text:
        return None
    regex = r"#[A-Za-z0-9_]+"
    matches = re.findall(regex, text, re.MULTILINE)
    return [match.replace('#', '') for match in matches]
