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
)

from hyper_shopping import trello

spell = SpellChecker()
dictionary = Path("./dictionary.txt")
if not dictionary.exists():
    dictionary.touch()
spell.word_frequency.load_text_file("./dictionary.txt")

KNOWN_CATEGORIES = {"meat", "diy", "drink", "house_hold"}


@click.group()
def cli():
    try:
        wn.synsets("test")
    except LookupError:
        if not yes_no_dialog(
            title="NLTK WordNet dataset is missing",
            text="Would you like to download it?",
        ):
            click.echo("NLTK Wordnet is required to run Hyper Shopping")
            return

        import nltk

        nltk.download("wordnet")


def choose_option(*args, **kwargs):
    buttons = [(i if isinstance(i, tuple) else (i, i)) for i in args]
    return button_dialog(buttons=buttons, **kwargs)


def choose_word(item, **kwargs):
    return choose_option(
        *item.split(),
        title="Complex item found",
        text="Which of the words generally describes your item the best?",
    )


def choose_spelling(candidates, **kwargs):
    return choose_option(
        *(list(candidates) + ("*Custom*", None)),
        title="Unknown word",
        text="Did you mean?",
    )


def choose_checklist(checklists, **kwargs):
    return button_dialog(
        buttons=[(cl["name"], cl) for cl in checklists],
        title="More than one checklist found",
        text="Which checklist should we parse?",
    )


def get_checklist():
    ...  # get user's trello card matching ID
    card = trello.get_card(card_file_path="shopping.json")
    if not yes_no_dialog(
        title="Card found", text=f"Is '{card['name']}' the right card?"
    ):
        return

    checklists = trello.get_checklists(card)
    if not checklists:
        return message_dialog(title="Error", text="This card has no checklists!")

    if len(checklists) > 1:
        return choose_checklist(checklists)
    else:
        return checklists[0]


def get_hypernims(synsets: List) -> List:
    """
    Unpack a list of synsets into a list of lemma names pertaining to each
    matched hypernim.

    :param synsets: a list of nltk.corpus.reader.wordnet.Synset
    :type synsets: List
    """
    hypernim_paths = [paths for synset in synsets for paths in synset.hypernym_paths()]
    hypernym_synsets = [synset for hypernims in hypernim_paths for synset in hypernims]
    return [name for synset in hypernym_synsets for name in synset.lemma_names()]


def category_from_hypernims():
    """
    Given a list of hypernims, choose a category
    """
    pass


def get_category(item):
    synsets = wn.synsets(item)
    hypernims = get_hypernims(synsets)
    if not hypernims:
        words_in_item = item.split()
        if len(words_in_item) > 1:
            # sentence unmatchable
            item = choose_word(item)

    synsets = wn.synsets(item)
    hypernims = get_hypernims(synsets)
    if hypernims:
        return category_from_hypernims(hypernims)

    if not spell.unknown(words_in_item):
        # handle unknown category:
        # 1. check if it's in known categories
        # 2. if not, ask user to confirm they want to add it
        # 3. return the category
        category = input_dialog(
            title="Unknown category", text="What is the category for this item"
        )
        return category

    # possible typo
    candidates = spell.candidates(item)
    if not candidates:
        ...  # unknown word, no hypernims, ask user
        raise RuntimeError("Unknown word, no spelling error and no hypernism, what do?")
    else:
        chosen = choose_spelling(candidates)
        if chosen is None:
            chosen = input_dialog(
                title="Custom value", text="Please enter the correct word"
            )
            if chosen == item:
                spell.word_frequency.load_words([chosen])
        item = chosen

    synsets = wn.synsets(item)
    hypernims = get_hypernims(synsets)
    if hypernims:
        return category_from_hypernims(hypernims)


@cli.command()
def get_trello_checklists():
    checklist = get_checklist()

    for i, item in enumerate(checklist["items"]):
        click.echo(f"Processing '{item}'")
        category = get_category(item)

    # item = "usd beef steak 2 fingers tick"
    # choose_word(item)


if __name__ == "__main__":
    register_repl(cli)
    cli()
