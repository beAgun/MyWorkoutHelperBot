from app.domain.notifications.notification_time import *
from pprint import pprint


def test_NotificationTime():
    t1 = NotificationTime(value=5, unit=TimeUnit.minute, label="5 min")
    t2 = NotificationTime(value=5, unit=TimeUnit.hour)
    pprint(t1)
    pprint(t2)
    assert (t1.key, t2.key) == (1, 2)
