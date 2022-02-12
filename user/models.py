from django.utils.translation import gettext_lazy as _
from authentication.abstract import NoUsernameAbstractUser
 
# Create your models here.
class User(NoUsernameAbstractUser):

    def get_provider(self, provider):
        return self.socialaccount_set.get(provider=provider)

    def orcid(self):
        return self.get_provider('orcid')
