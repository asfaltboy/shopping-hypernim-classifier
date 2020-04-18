from typing import List
from mypy_extensions import TypedDict
import json


Checklist = TypedDict(
    "Checklist", {"card_id": str, "checklist_id": str, "items": List[str], "name": str}
)
Card = TypedDict("Card", {"id": str, "name": str, "checklists": List[Checklist]})


def get_checklists(card: Card) -> List[Checklist]:
    """
    Parse a Trello card for all checklists

    :param fp: test_trello.py
    """
    return [
        {
            "card_id": card["id"],
            "checklist_id": checklist["id"],
            "name": f"[{len(checklist['checkItems'])}]{checklist['name']}",
            "items": [item["name"] for item in checklist["checkItems"]],
        }
        for checklist in card["checklists"]
    ]


def get_card(card_file_path: str) -> Card:
    with open(card_file_path) as file:
        return json.load(file)
