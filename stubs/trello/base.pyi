from typing import Any

class TrelloBase:
    id: Any = ...
    def __init__(self) -> None: ...
    def __hash__(self) -> Any: ...
    def __eq__(self, other: Any) -> Any: ...