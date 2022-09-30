from django.db.models import Q
from django.apps import apps
from django.db.models import OneToOneField, ForeignKey, ManyToManyField


def choice_limiter(root_code):
    
    def func():
        model = apps.get_model('database.Choice')
        node = model.objects.get(code=root_code)
        # return Q(id = node.id) | Q(pk__in=node.get_descendants())
        return Q(pk__in=node.get_descendants())

    return func


environment_choices = choice_limiter('env')

class ChoiceAbstract():

    def __init__(self, verbose_name=None, root_code=None, allow_unspec=True, *args, **kwargs):
        kwargs['to'] = "database.Choice"
        kwargs['limit_choices_to'] = self.choice_limiter
        kwargs['related_name'] = '+'
        kwargs['verbose_name'] = verbose_name

        self.root_code = root_code
        self.allow_unspecified = allow_unspec
        super().__init__(*args,**kwargs)


   
    def choice_limiter(self):
        model = apps.get_model(self.related_model)
        node = model.objects.get(code=self.root_code if self.root_code else self.name)

        query = Q(pk__in=node.get_descendants())
        if self.allow_unspecified:
            query = query | Q(code = 'unspecified')
        return query

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if "limit_choices_to" in kwargs:
            del kwargs['limit_choices_to']
        return name, path, args, kwargs

class ChoicesOneToOne(ChoiceAbstract, OneToOneField):
    pass

class ChoicesForeignKey(ChoiceAbstract, ForeignKey):
    pass

class ChoicesManyToMany(ChoiceAbstract, ManyToManyField):
    pass