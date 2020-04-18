import os
from functools import partial
from copy import deepcopy
from trello import TrelloClient
from trello.card import Card
from trello.checklist import Checklist

from typing import List, Dict
from mypy_extensions import TypedDict
import json

CheckItem = TypedDict("CheckItem", {"id": str, "name": str, "pos": str})

SHOP_ROUTES = {"smart": ["bbq", "drinks", "diy", "vegetables", "dairy"]}

trello = TrelloClient(
    api_key=os.getenv("TRELLO_API_KEY"),
    api_secret=os.getenv("TRELLO_API_SECRET"),
)


def get_shopping_cards() -> List[Card]:
    """
    Return a list of shopping cards sorted by creation date
    in ascending order.
    """
    boards = trello.list_boards()
    board = [b for b in boards if b.name == "Our Board"][0]
    cards = board.open_cards()
    return [
        card
        for card in sorted(
            cards, key=lambda c: c.dateLastActivity, reverse=True
        )
        if card.name.lower() == "shopping"
    ]


def get_checklist_items(card: Card):
    """
    Return all item names in the first checklist of given card
    """
    checklist = card.checklists[0]
    return [ci["name"] for ci in checklist.items]


def get_card() -> Card:
    first_shopping_card = get_shopping_cards()[0]
    return first_shopping_card


def get_card_from_file(card_file_path: str) -> Card:
    """ Dummy getter for the file """
    with open(card_file_path) as file:
        return json.load(file)


def sort_checklists(card: Card, shop: str) -> List[Checklist]:
    """
    Sort a Trello card for all checklists using pre-defined sections for the given shop
    """
    preferred_shop_route = SHOP_ROUTES[shop]
    for checklist in card.checklists:
        checklist.items = sort_checklist(
            checklist=checklist.items, route=preferred_shop_route
        )
    return card.checklists


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
