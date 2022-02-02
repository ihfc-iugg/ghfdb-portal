from django.urls import reverse

heat_flow = dict(
    label='Heat Flow',
    editor='heatFlow', #reuired to make a unique js variable
    url="/api/heat-flow/",
    preheader = [ 
        # (colspan,label,popup)
        (4,'',None),
        (2,'Depth',"[m]"),
        (2,'Heat Flow',"[mW m<sup>-2</sup>]"),
        (2,'Gradient',"[&deg;C/km]"),
        (4,'Properties',""),
    ],
    header = [
        # (data-attribute,label,popup)
        ('site.site_name','Site',''),
        ('site.latitude','Lat',''),
        ('site.longitude','Lon',''),
        ('number_of_temperatures','T (n)','number_of_temperatures'),
        ('depth_min','Top',''),
        ('depth_max','Bottom',''),
        ('heat_flow','<i>q</i>',''),
        ('heat_flow_uncertainty','<i>&sigma;</i>',''),
        ('gradient','<i>&Delta;T</i>',''),
        ('gradient_uncertainty','<i>&sigma;</i>',''),
        ('average_conductivity','<i>k</i>','Thermal Conductivity<br>[W m<sup>-1</sup> K<sup>-1</sup>]'),
        ('heat_production','<i>a</i>','Heat Production [&mu;W m<sup>-3</sup>]'),
        ],
    )

heat_production = dict(
    label='Heat Production',
    editor='heatProd', #reuired to make a unique js variable
    url="/api/heat-production/",
    header = [
        ('site.site_name','Site',''),
        ('site.latitude','Lat',''),
        ('site.longitude','Lon',''),
        ('depth','Depth','[m]'),
        ('heat_production','Heat Prod. [<i>a</i>]',''),
        ('uncertainty','Uncertainty [<i>&sigma;</i>]',''),
        ('method','Method',''),
        ],
    )

conductivity = dict(
    label='Thermal Conductivity',
    editor='cond', #reuired to make a unique js variable
    url="/api/conductivity/",
    header = [
        ('site.site_name','Site',''),
        ('site.latitude','Lat',''),
        ('site.longitude','Lon',''),
        ('depth','Depth','[m]'),
        ('conductivity','Conductivity [<i>k</i>]',''),
        ('uncertainty','Uncertainty [<i>&sigma;</i>]',''),
        ('method','Method',''),
        ],
    )

temperature = dict(
    label='Temperature',
    editor='temperature', #reuired to make a unique js variable
    url="/api/temperature/",
    header = [
        ('site.site_name','Site',''),
        ('site.latitude','Lat',''),
        ('site.longitude','Lon',''),
        ('depth','Depth','[m]'),
        ('temperature','Temperature [<i>&deg;C</i>]',''),
        ('uncertainty','Uncertainty [<i>&sigma;</i>]',''),
        ('method','Method',''),
        ],
    )