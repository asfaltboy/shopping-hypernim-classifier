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
    "meat",
    "diy",
    "dairy",
    "vegetable",
    "drink",
    "house_hold",
}
DEFAULT_CATEGORY_SYNONYMS = {
    "juice": "drink",
    "substance": "baking",
    "plan": "vegetable",
    "eggs": "vegetable",
    "dairy_product": "dairy",
    "pastry": "snacks",
}


class Storage:
    data: Store

    def __init__(self, shelf):
        self.data = shelf

    def get_known_categories(self,):

        if not self.data.get("known_categories"):
            self.update_known_categories(DEFAULT_CATEGORIES)
        return self.data["known_categories"]

    def update_known_categories(self, categories):
        self.data["known_categories"] = categories

    def get_item_category(self, item):
        if "item_categories" not in self.data:
            self.data["item_categories"] = []
        return self.data["item_categories"].get(item)

    def set_item_category(self, item, category):
        if "item_categories" not in self.data:
            self.data["item_categories"] = {}
        categories = self.data["item_categories"]
        categories[item] = category
        self.data["item_categories"] = categories

    def get_category_synonyms(self):
        return DEFAULT_CATEGORY_SYNONYMS
        # return {
        #     "juice": "drink",
        #     "substance": "baking",
        #     "plant": "vegetable",
        # }

        # if "category_synonyms" not in self.data:
        # self.data["category_synonyms"] = DEFAULT_CATEGORY_SYNONYMS
        # return self.data["category_synonyms"]
