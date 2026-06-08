from app.db.models import User, NotificationsRule, Notification, Workout
from pprint import pprint


def test_create_models():
    u1 = User(chat_id=1, username="test1")
    u2 = User(chat_id=2, username="test2", first_name="testik2", site_user_id=2)
    pprint([u1, u2])
    rule = NotificationsRule(user=u1, offset_minutes=30)
    pprint(rule)


if __name__ == "__main__":
    test_create_models()
