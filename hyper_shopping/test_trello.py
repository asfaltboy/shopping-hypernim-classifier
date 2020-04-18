from copy import deepcopy

import pytest

from .trello import sort_checklist, Checklist


def test_get_checklist():
    with open("../shopping.json") as file:
        checklists = get_checklists(fp=file)
        assert len(checklists) == 2
        cl = checklists[1]
        assert cl["card_id"] == "5d4e82b1d61983302dea279b"
        assert cl["checklist_id"] == "5d4e8e1f40291b59633843bf"
        assert cl["items"] == ["usd beef steak 2 fingers tick"]


@pytest.fixture
def test_items():
    return [
        {
            "idChecklist": "5d4e82b6f1d1794340295fc5",
            "state": "incomplete",
            "id": "5d4e82b7ccb8513186f57701",
            "name": "Tomatoes",
            "nameData": None,
            "pos": 17311,
        },
        {
            "idChecklist": "5d4e82b6f1d1794340295fc5",
            "state": "incomplete",
            "id": "5d4e82b9f2e0800aebc0fc93",
            "name": "Milk",
            "nameData": None,
            "pos": 34651,
        },
        {
            "idChecklist": "5d4e82b6f1d1794340295fc5",
            "state": "incomplete",
            "id": "5d4e89271961f680be7c2268",
            "name": "Parmesan",
            "nameData": None,
            "pos": 34654,
        },
    ]


@pytest.fixture
def test_departments():
    return


@pytest.mark.parametrize(
    "test_departments", [["vegetables", "dairy"], ["dairy", "vegetables"],]
)
def test_sort_checklist(test_items, test_departments):
    original = deepcopy(test_items)

    sorted_items = sort_checklist(test_items, test_departments)

    assert test_items == original  # original is unchanged
    assert len(sorted_items) == 3
    assert sorted_items[0]["pos"] == "1"
    assert sorted_items[1]["pos"] == "2"
    assert sorted_items[2]["pos"] == "3"

    if test_departments[0] == "vegetables":
        assert sorted_items[0]["id"] == original[0]["id"]
        assert sorted_items[1]["id"] == original[1]["id"]
        assert sorted_items[2]["id"] == original[2]["id"]
    else:
        assert sorted_items[0]["id"] == original[1]["id"]
        assert sorted_items[1]["id"] == original[2]["id"]
        assert sorted_items[2]["id"] == original[0]["id"]
