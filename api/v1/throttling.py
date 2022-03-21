from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AnonBurstRate(AnonRateThrottle):
    scope = 'anon_burst'

class AnonSustainedRate(AnonRateThrottle):
    scope = 'anon_sustained'

class UserBurstRate(UserRateThrottle):
    scope = 'user_burst'

class SubscriberBurstRate(UserRateThrottle):
    scope = 'subscriber_burst'

class SubscriberSustainedRate(UserRateThrottle):
    scope = 'subscriber_sustained'