from dataclasses import dataclass
from typing import Any


@dataclass
class SystemTask:
    """
    Represents a non-character change to be made on the FE

    Attributes:

    """

    type: str
    payload: Any
