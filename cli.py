"""

TODO:
1. Write short intro for document
2. Add display command for:
   known-categories
   item-categories
   category-synonyms
   shop-routes
   shopping-lists
3. Add an add-shop-route command
4. Add a get list from trello command
5. Add a shopping list by shop-route command
"""

from pprint import pprint
import re
import shelve
from pathlib import Path
from typing import List

from spellchecker import SpellChecker
from nltk.corpus import wordnet as wn

import click
from click_repl import register_repl
from prompt_toolkit.shortcuts import (
    button_dialog,
    input_dialog,
    message_dialog,
    yes_no_dialog,
    radiolist_dialog,
)

from hyper_shopping.trello_helpers import get_card, get_checklist_items
from hyper_shopping.datastore import Storage

spell = SpellChecker()
dictionary = Path("./dictionary.txt")
if not dictionary.exists():
    dictionary.touch()
spell.word_frequency.load_text_file("./dictionary.txt")

re_non_word = re.compile("[^\w]+")

storage = Storage(shelve.open(".data"))


@click.group()
def cli():
    try:
        wn.synsets("test")
    except LookupError:
        if not yes_no_dialog(
            title="NLTK WordNet dataset is missing",
            text="Would you like to download it?",
        ).run():
            click.echo("NLTK Wordnet is required to run Hyper Shopping")
            return

        import nltk

        nltk.download("wordnet")


def make_labels(options: List[str]):
    """
    Given a list of strings, return the list with a tuple of (value, labels)
    for each of the strings
    """
    return [(value, value) for value in options]


def choose_word(item, **kwargs):
    return radiolist_dialog(
        title="Complex item found",
        text="Which of the words generally describes your item best?",
        values=make_labels(item.split()),
    ).run()


def choose_category(item, hypernims, **kwargs):
    return radiolist_dialog(
        values=make_labels(hypernims),
        title="Many categories found",
        text=f"Which of the categories describes '{item}' best?",
    ).run()


def choose_spelling(candidates, **kwargs):
    return radiolist_dialog(
        title="Unknown word",
        text="Did you mean?",
        buttons=make_labels(candidates) + [("*Custom*", None)],
    ).run()


def choose_checklist(checklists, **kwargs):
    return button_dialog(
        buttons=[(cl["name"], cl) for cl in checklists],
        title="More than one checklist found",
        text="Which checklist should we parse?",
    )


def choose_category_synonym(item, hypernims, **kwargs):
    synonym = radiolist_dialog(
        values=make_labels(hypernims),
        title="Hypernims without category found",
        text=f"Which hypernim is synonymous with a category for the item '{item}'?",
    ).run()
    if not synonym:
        return

    known_categories = storage.get_known_categories()
    category = radiolist_dialog(
        values=make_labels(sorted(known_categories)),
        title=f"Choose category for '{synonym}'",
        text=f"Which category is '{synonym}' synonymous with?",
    ).run()
    if not category:
        category = input_dialog(
            title=f"Add a new category synonymous with '{synonym}'",
        ).run()
    if not category:
        category = input_dialog(
            title="Unknown category",
            text=f"What is the category for synonym '{item}'",
        ).run()
    if category:
        storage.add_category_synonym(synonym, category)

    return category


def get_checklist():
    # TODO: get user's trello card matching ID
    card = get_card()
    card_prompt_result = yes_no_dialog(
        title="Card found",
        text=f"Is '{card.name}' (from {card.dateLastActivity}) the right card?",
    ).run()
    if not card_prompt_result:
        return

    items = get_checklist_items(card)
    print(*items, sep="\n")
    return items


def get_hypernims(item: str) -> List:
    """
    Unpack a list of synsets into a list of lemma names pertaining to each
    matched hypernim.

    :param synsets: a list of nltk.corpus.reader.wordnet.Synset
    :type synsets: List
    """
    synsets = wn.synsets(item)
    hypernim_paths = [
        paths for synset in synsets for paths in synset.hypernym_paths()
    ]
    hypernym_synsets = [
        synset for hypernims in hypernim_paths for synset in hypernims
    ]
    return [
        name for synset in hypernym_synsets for name in synset.lemma_names()
    ]


def get_valid_categories(hypernims):
    direct_matches = sorted(
        storage.get_known_categories() & set(hypernims), key=hypernims.index
    )
    synonyms = storage.get_category_synonyms()
    matched_synonyms = set()
    for hypernim in hypernims:
        if hypernim in synonyms:
            matched_synonyms.add(synonyms[hypernim])
    return direct_matches + list(matched_synonyms)


def category_from_hypernims(item, hypernims):
    """
    Given a list of hypernims for item, choose a category
    """
    sorted_hypernims = sorted(set(hypernims))
    categories = sorted(set(get_valid_categories(hypernims)))
    if categories:
        category = choose_category(item, categories)
    else:
        category = choose_category(item, sorted_hypernims)
    if not category:
        category = choose_category_synonym(item, sorted_hypernims)

    assert category, f"Fail: choose a category from: {sorted_hypernims}!"
    return category


def normalize_word(item):
    return re.sub(re_non_word, "_", item)


def test_typos(item):
    # possible typo
    candidates = spell.candidates(item)
    if not candidates:
        ...  # unknown word, no hypernims, ask user
        raise RuntimeError(
            "Unknown word, no spelling error and no hypernims, what do?"
        )
    else:
        chosen = choose_spelling(candidates)
        if chosen is None:
            chosen = input_dialog(
                title="Custom value",
                text=f"Spelling not found, please enter the correct word for {item}",
            ).run()
            if chosen == item:
                spell.word_frequency.load_words([chosen])
            item = normalize_word(chosen)
        else:
            item = chosen
    return item


def get_category(item):
    # replace all spaces with '_' for synset lookup to work
    normalized_item = normalize_word(item)
    hypernims = get_hypernims(normalized_item)
    words_in_item = item.split()
    if not hypernims:
        # sentence unmatchable
        word = choose_word(item)
        if not word:
            word = test_typos(item)
        assert item, "no word chosen"
        normalized_item = normalize_word(word)

    hypernims = get_hypernims(normalized_item)
    if hypernims:
        return category_from_hypernims(normalized_item, hypernims)

    # handle unknown category:
    # 1. check if it's in known categories
    # 2. if not, ask user to confirm they want to add it
    # 3. return the category
    category = input_dialog(
        title="Unknown category", text=f"What is the category for {item}"
    ).run()
    return category


def create_shopping_card():
    items = []
    result = ""
    while result is not None:
        result = input_dialog(
            title="Add shopping item",
            ok_text="Add more",
            cancel_text="Finished",
        ).run()
        if result:
            items.append(result)

    print(items)

    item_list = "\n".join(items)
    response = yes_no_dialog(
        title="Done?",
        text=(
            f"You've entered the following items: "
            f"\n{item_list}\n would you like to "
            f"create the card?"
        ),
    ).run()


dummy_words = [
    "Coke",
    "Ace Juice",
    "Sparkling water",
    "Glycerine",
    "Mushrooms",
    "Garlic",
    "Peppers red and green",
    "Tomatoes",
    "Eggs",
    "Milk *3",
    "Butter",
    "Sour cream",
    "Flour",
    "Sausages pig",
    "Anti mold solution for cleaning wall or clor",
    "Pop tards",
    "Polish salty cucumbers in a bag",
    "Marinated gogosari",
    "Mozzarella a piece  for grating for lasagna",
    "Black and white bread",
    "Lemons",
    "Barbeque for 1 time",
    "Mint leaves fresh",
    "Basil leaves fresh",
    "Cream for cooking",
    "Insect repellent machine and solution",
    "Frozen Chips",
    "Vanilla essence",
    "Polenta",
    "Strawberries",
    "Sugar",
    "toilet paper",
    "pastizzi",
    "canned peas",
]


@cli.command()
def get_categories():
    for i, item in enumerate(dummy_words):
        click.echo(f"{i}. '{item}'")
        stored_category = storage.get_item_category(item)
        if not stored_category:
            category = get_category(item)
            if category:
                storage.set_item_category(item, category)
            else:
                raise Exception("Category could not be found!")

    pprint(storage.data["item_categories"])


@cli.command()
def get_items_from_checklists():
    """
    Fetch shopping card checklists and try to place the items in their
    related shopping categories, using a combination of nltk wordnet
    search as well manual choices to disambiguate.
    """
    checklist = get_checklist()
    if checklist:
        print(*checklist, sep="\n")
        return

    should_create_card = yes_no_dialog(
        title="Card not found", text=f"Shall we create a new shopping card?",
    ).run()
    print(should_create_card)
    if not should_create_card:
        return

    create_shopping_card()


@cli.command()
def create():
    create_shopping_card()


if __name__ == "__main__":
    register_repl(cli)
    cli()
