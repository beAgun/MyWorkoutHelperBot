from app.domain.notifications.notification_time import *
from app.domain.notifications.notifications_settings import *
from pprint import pprint


def test_NotificationsSettings_create_ins():
    s = NotificationsSettings()
    pprint(s)


def test_NotificationsSettings():
    s1 = NotificationsSettings(
        notification_type=NotificationType.trainings,
        trainings_notification_type=TrainingsNotificationType.all,
    )
    s2 = NotificationsSettings(
        notification_type=NotificationType.trainings,
        trainings_notification_type=TrainingsNotificationType.all,
    )
    t1 = NotificationTime(value=5, unit=TimeUnit.minute, label="5 min")
    t2 = NotificationTime(value=5, unit=TimeUnit.hour)
    s1.notifications_times.append(t1)
    # pprint(s1.notifications_times)
    # pprint(s2.notifications_times)
    print(s1.notifications_times is s2.notifications_times)
    assert (s1.notifications_times is s2.notifications_times) == False


def test_NotificationsSettings_methods():
    s = NotificationsSettings(
        notification_type=NotificationType.trainings,
        trainings_notification_type=TrainingsNotificationType.all,
    )
    s.add_custom()


if __name__ == "__main__":
    # test_NotificationTime()
    # test_NotificationsSettings()
    # test_NotificationsTimesList()
    # test_NotificationsSettings_methods()
    test_NotificationsSettings_create_ins()
