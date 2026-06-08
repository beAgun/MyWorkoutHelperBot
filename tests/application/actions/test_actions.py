from app.application.actions.actions import *


def test_Actions():
    action_name = "change_preset"
    a = Actions.get(action_name=action_name)
    assert a == KeyAction(action_name)


if __name__ == "__main__":
    test_Actions()
