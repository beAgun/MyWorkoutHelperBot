from app.domain.notifications.notification_time import *
from app.domain.notifications.notifications_times_list import *
from pprint import pprint


def test_NotificationsTimesList():
    t1 = NotificationTime(value=5, unit=TimeUnit.minute, label="5 min", chosen=False)
    t2 = NotificationTime(value=5, unit=TimeUnit.hour)
    # t1.chosen = True
    print(t1 == t1)
    times = NotificationsTimesList()
    times.append(t1)
    times.append(t1)
    print(times)


def test_NotificationsTimesList_set():
    t1 = NotificationTime(
        value=5, unit=TimeUnit.minute, label="5 min", is_preset=False, chosen=True
    )
    t2 = NotificationTime(value=5, unit=TimeUnit.hour, chosen=True)
    t3 = NotificationTime(value=5, unit=TimeUnit.minute, is_preset=True, chosen=True)
    times = NotificationsTimesList()
    times.append(t1)
    times.append(t2)
    times.append(t3)

    unique_times = set(times)
    pprint(unique_times)


if __name__ == "__main__":
    test_NotificationsTimesList_set()
