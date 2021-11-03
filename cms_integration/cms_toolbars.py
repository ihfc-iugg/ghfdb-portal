from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from thermoglobe.models import Site
from cms.utils.urlutils import admin_reverse

class SiteToolbar(CMSToolbar):

    def populate(self):
        site_menu = self.toolbar.get_or_create_menu(
            'thermoglobe_site_integration',  # a unique key for this menu
            'Sites',                        # the text that should appear in the menu
            )
        site_menu.add_sideframe_item(name='View sites',url=admin_reverse('thermoglobe_site_changelist'))
        data_menu = self.toolbar.get_or_create_menu('thermoglobe_intervals_integration','Data')

        data_menu.add_sideframe_item('Heat Flow',admin_reverse('thermoglobe_heatflow_changelist'))
        data_menu.add_sideframe_item('Thermal Gradient',admin_reverse('thermoglobe_gradient_changelist'))
        data_menu.add_sideframe_item('Temperature',admin_reverse('thermoglobe_temperature_changelist'))
        data_menu.add_sideframe_item('Thermal Conductivity',admin_reverse('thermoglobe_conductivity_changelist'))
        data_menu.add_sideframe_item('Heat Production',admin_reverse('thermoglobe_heatproduction_changelist'))
        # publications_menu = self.toolbar.get_or_create_menu(
        #     'publications_integration',  # a unique key for this menu
        #     'Publications',                        # the text that should appear in the menu
        #     )

        # publications_menu.add_sideframe_item(
        #     name='Publications',
        #     url=admin_reverse('publications_publication_changelist'),
        # )


# register the toolbar
toolbar_pool.register(SiteToolbar)
