from typing import List, Set, Dict, Mapping
from mypy_extensions import TypedDict
import shelve


KnownCategories = Set[str]
ItemCategories = Dict[str, str]
Store = TypedDict(
    "Store",
    {"known_categories": KnownCategories, "item_categories": ItemCategories},
)
DEFAULT_CATEGORIES = {
    "baked_goods",
    "baking",
    "dairy",
    "diy",
    "drink",
    "house_hold",
    "meat",
    "vegetable",
    "frozen_food",
    "canned_food",
}
DEFAULT_CATEGORY_SYNONYMS = {
    "component": "baking",
    "dairy_product": "dairy",
    "eggs": "vegetable",
    "juice": "drink",
    "pastry": "snacks",
    "picnic": "house_hold",
    "plant": "vegetable",
}


class Storage:
    data: Store

    def __init__(self, shelf):
        self.data = shelf
        self.update_defaults()

    def update_defaults(self):
        categories = self.data.get("known_categories") or set()
        categories.update(DEFAULT_CATEGORIES)
        self.data["known_categories"] = categories

        category_synonyms = self.data.get("category_synonyms") or {}
        category_synonyms.update(DEFAULT_CATEGORY_SYNONYMS)
        self.data["category_synonyms"] = category_synonyms

        if "item_categories" not in self.data:
            self.data["item_categories"] = {}

    def get_known_categories(self,):
        return self.data["known_categories"]

    def update_known_categories(self, categories):
        self.data["known_categories"] = categories

    def add_to_known_categories(self, category):
        categories = self.get_known_categories()
        categories.add(category)
        self.update_known_categories(categories)

    def get_item_category(self, item):
        return self.data["item_categories"].get(item)

    def set_item_category(self, item, category):
        self.add_to_known_categories(category)
        categories = self.data["item_categories"]
        categories[item] = category
        self.data["item_categories"] = categories

    def get_category_synonyms(self):
        return self.data["category_synonyms"]

    def add_category_synonym(self, synonym, category):
        category_synonyms = self.get_category_synonyms()
        category_synonyms["synonym"] = category
        self.data["category_synonyms"] = category_synonyms
