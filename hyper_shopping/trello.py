from functools import partial
from copy import deepcopy

from typing import List, Dict
from mypy_extensions import TypedDict
import json


CheckItem = TypedDict("CheckItem", {"id": str, "name": str, "pos": str})
Checklist = TypedDict(
    "Checklist",
    {"idCard": str, "id": str, "checkItems": List[CheckItem], "name": str},
)
Card = TypedDict(
    "Card", {"id": str, "name": str, "checklists": List[Checklist]}
)


def get_card(card_file_path: str) -> Card:
    with open(card_file_path) as file:
        return json.load(file)


def sort_checklists(card: Card, shop: str) -> List[Checklist]:
    """
    Sort a Trello card for all checklists using pre-defined sections for the given shop

    :param fp: test_trello.py
    """
    for checklist in card["checklists"]:
        checklist["checkItems"] = sort_checklist(checklist["checkItems"], shop)
    return card["checklists"]


# TODO: find items' departments via nltk
dummy_item_department_map = {
    "tomatoes": "vegetables",
    "milk": "dairy",
    "parmesan": "dairy",
}


def sort_function(item: CheckItem, department_order: List[str]):
    """
    A sorted key function that returns a tuple of two items:
     ( the index of the department of this item in the route,
       the name of the item )
    """
    normalized_name = item["name"].lower()
    department = dummy_item_department_map[normalized_name]
    return (department_order.index(department), normalized_name)


def sort_checklist(checklist: List[CheckItem], route: List[str]):
    """
    Given a route through a given shop's departments, sort
    the trello items in the list by the departments on the route
    grouping items that are available in that shop's section.

    :param checklist: the list of trello checklist items
    :param route: list of department names ordered for optimal route
    :returns: the sorted list of items
    """
    checklist = deepcopy(checklist)  # don't change original

    sorted_items = sorted(
        checklist, key=partial(sort_function, department_order=route)
    )

    # reset positions to new positive integer values
    for i, item in enumerate(sorted_items):
        item["pos"] = str(i + 1)
    return sorted_items
