from invitations.signals import invite_accepted
from django.dispatch import receiver
from django.contrib import auth

@receiver(invite_accepted, sender=auth.get_user_model())
def invite_accepted(sender, request, email, **kwargs):
    print('Someone accepted an invite')
    pass