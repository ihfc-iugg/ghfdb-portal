from django.utils.translation import gettext_lazy as _
from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.modules import ModelList, AppList, Group

class AdminDashboard(Dashboard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.children.append(Group(_('Global Heat Flow Database'),
            column=1,
            collapsible=True,
            children=[
                ModelList(_('Heat Flow'),
                    collapsible=False,
                    models=('database.models.*Site','*Interval','*Choice',),
                    # exclude=('database.models.Correction',)

                ),
                ModelList(_('Thermal Data'), models=(
                    'thermal_data.*',
                    # 'well_logs.*',
                    )),
                ModelList(_('Literature'), models=('publications*','crossref*',)),
                ModelList(_('Shapefiles'), models=('mapping*','global_tectonics*')),
                ModelList(_('Method Fields'), models=('database_choices.models.methods*',)),
                ModelList(_('Type Fields'), models=('database_choices.models.types*',)),
            ],
        ))

        self.children.append(ModelList(_('WHFD Project'),
            column=1,
            collapsible=True,
            models=('review*',),

        ))

        self.children.append(ModelList(_('GFZ Dataservices'),
            column=1,
            collapsible=True,
            models=(
                "datacite*",
                ),
        ))

        self.children.append(ModelList(_('Administration'),
            column=2,
            collapsible=True,                
            models=(
                'core*',
                "user*",
                'django.contrib.*',
                "invitations.*",
                ),
        ))

        # self.children.append(ModelList(_('Comments'),
        #     column=2,
        #     collapsible=True,
        #     models=(
        #         'fluent_comments.*',
        #         # 'threaded*'
        #         ),
        # ))

        # self.children.append(ModelList(_('CMS'),
        #     column=2,
        #     collapsible=True,
        #     models=(
        #         'cms*',
        #         ),
        # ))

        self.children.append(ModelList(_('Organizations'),
            column=2,
            collapsible=True,
            models=(
                "organizations.*",
                "research_organizations.*",
                ),
        ))


        self.children.append(ModelList(_('Django All-Auth'),
            column=2,
            collapsible=True,
            models=("allauth.*",),
        ))

        # self.children.append(ModelList(_('Files'),
        #     column=2,
        #     collapsible=True,
        #     models=(
        #         "filer*",
        #         "easy_thumbnails*",
        #         ),
        # ))

