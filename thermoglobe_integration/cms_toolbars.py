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
        site_menu.add_sideframe_item(
            name='View sites',                              # name of the new menu item
            url=admin_reverse('thermoglobe_site_changelist'),    # the URL it should open with
            )
        data_menu = self.toolbar.get_or_create_menu(
            'thermoglobe_intervals_integration',  # a unique key for this menu
            'Data',                        # the text that should appear in the menu
            )

        data_menu.add_sideframe_item(
            name='Intervals',                              # name of the new menu item
            url=admin_reverse('thermoglobe_interval_changelist'),    # the URL it should open with
        )
        data_menu.add_sideframe_item(
            name='Temperature',                              # name of the new menu item
            url=admin_reverse('thermoglobe_temperature_changelist'),    # the URL it should open with
        )
        data_menu.add_sideframe_item(
            name='Thermal Conductivity',                              # name of the new menu item
            url=admin_reverse('thermoglobe_conductivity_changelist'),    # the URL it should open with
        )
        data_menu.add_sideframe_item(
            name='Heat Generation',                              # name of the new menu item
            url=admin_reverse('thermoglobe_heatgeneration_changelist'),    # the URL it should open with
        )
        # publications_menu = self.toolbar.get_or_create_menu(
        #     'publications_integration',  # a unique key for this menu
        #     'Publications',                        # the text that should appear in the menu
        #     )

        # publications_menu.add_sideframe_item(
        #     name='Publications',                              # name of the new menu item
        #     url=admin_reverse('publications_publication_changelist'),    # the URL it should open with
        # )


# register the toolbar
toolbar_pool.register(SiteToolbar)
