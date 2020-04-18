from .trello import get_checklists


def test_get_checklist():
    with open("../shopping.json") as file:
        checklists = get_checklists(fp=file)
        assert len(checklists) == 2
        cl = checklists[1]
        assert cl["card_id"] == "5d4e82b1d61983302dea279b"
        assert cl["checklist_id"] == "5d4e8e1f40291b59633843bf"
        assert cl["items"] == ["usd beef steak 2 fingers tick"]
