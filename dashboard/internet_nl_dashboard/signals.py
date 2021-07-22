from actstream import action
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in)
def stream_login(sender, **kwargs):  # pylint: disable=unused-argument
    # sender = user
    action.send(kwargs['user'], verb='logged in', public=False)


@receiver(user_logged_out)
def stream_logout(sender, **kwargs):  # pylint: disable=unused-argument
    # sender = user
    # logging out via json requests went wrong somehow.
    if kwargs.get('user', None):
        action.send(kwargs['user'], verb='logged out', public=False)
