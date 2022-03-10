from django.urls import reverse

heat_flow = dict(
    label='Heat Flow',
    editor='heatFlow', #reuired to make a unique js variable
    url="/api/intervals/heat-flow/",
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
    url="/api/logs/heat-production/",
    header = [
        ('site.site_name','Site',''),
        ('site.latitude','Lat',''),
        ('site.longitude','Lon',''),
        ('data_count','Count',''),
        ('depth_upper','Depth Upper (m)',''),
        ('depth_lower','Depth Lower (m)',''),
        ('method','Method',''),
        ],
    )

conductivity = dict(
    label='Thermal Conductivity',
    editor='cond', #reuired to make a unique js variable
    url="/api/logs/conductivity/",
    preheader = [ 
        # (colspan,label,popup)
        (1,'',None),
        (2,'Depth',"[m]"),
        (1,'',None),
    ],
    header = [
        ('site.site_name','Site',''),
        ('site.latitude','Lat',''),
        ('site.longitude','Lon',''),
        ('data_count','Count',''),
        ('depth_upper','Upper',''),
        ('depth_lower','Lower',''),
        ('method','Method',''),
        ],
    )

temperature = dict(
    label='Temperature',
    editor='temperature', #reuired to make a unique js variable
    url="/api/logs/temperature/",

    preheader = [ 
        # (colspan,label,popup)
        (1,'',None),
        (2,'Depth',"[m]"),
        (1,'',None),
    ],
    header = [
        ('site.site_name','Site',''),
        ('site.latitude','Lat',''),
        ('site.longitude','Lon',''),
        ('data_count','Count',''),
        ('depth_upper','Upper',''),
        ('depth_lower','Lower',''),
        ('method','Method',''),
        ],
    )