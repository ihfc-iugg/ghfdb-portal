gradient = [
            dict(type='choropleth', 
                template='stacked',
                reverse=True,  
                wide=True),
            dict(
                type='continental_vs_oceanic', 
                template='standard', 
                reverse=True,
                wide=True),
            dict(
                type='age_plot', 
                fields=['juvenile_age','thermotectonic_age'],
                template='stacked', 
                wide=False),
            dict(
                type='box', 
                fields=['tectonic_environment'],
                template='stacked',),
        ]

heat_flow = [
            dict(type='choropleth', 
                template='stacked',
                reverse=True,  
                wide=True),
            dict(
                type='continental_vs_oceanic', 
                template='standard', 
                reverse=True,
                wide=True),
            dict(
                type='box', 
                fields=['seas'],
                template='standard'),
            dict(
                type='box', 
                fields=['tectonic_environment'],
                template='standard',
                reverse=True),
            dict(
                type='age_plot', 
                fields=['juvenile_age','thermotectonic_age'],
                # fields=['juvenile_age'],
                template='stacked', 
                wide=False),
            # dict(
            #     type='sunburst', 
            #     fields=['thermotectonic_age','juvenile_age'],
            #     titles=['Thermo-tectonic age', 'Juvenile age'],
            #     template='stacked', 
            #     wide=False),
        ]

field_mapping = dict(
        seas='site__sea__name',
        province='site__province__name',
        tectonic_environment='site__province__type',
        sub_regime_group='site__basin__sub_regime',
        juvenile_age='juvenile_age',
        thermotectonic_age='thermotectonic_age',
        )