TEMP_METHOD = (
    ('bht','Bottom hole temperature (uncorrected)'),
    ('cbht','Bottom hole temperature (corrected)'),
    ('dst','Drill stem test'),
    ('pt100','Pt-100 probe'),
    ('pt1000','Pt-1000 probe'),
    ('log','Continuous temperature log'),
    ('clog','Corrected temperature log'),
    ('dts','Distributed temperature sensing'),
    ('cpd','Cure point depth estimate'),
    ('xen','Xenlith'),
    ('gtm','Geothermometry'),
    ('bsr','Bottom-simulating seismic reflector'),
    ('apct/set-2','Ocean drilling temperature tool'),
    ('sur','Surface temperature'))


EXPLORATION_PURPOSE = (
    ('hydrocarbon','Hydrocarbon'),
    ('underground_storage','Underground Storage'),
    ('geothermal','Geothermal'),
    ('mapping','Mapping'),
    ('mining','Mining'),
    ('tunneling','Tunneling'),
    ('unspec','Not Specified'),
)

EXPLORATION_METHOD = (
    ('drilling','Drilling'),
    ('mining','Mining'),
    ('tunneling','Tunneling'),
    ('probing_lake','Probing (Lake)'),
    ('probing_ocean','Probing (Ocean)'),
    ('unspec','Not Specified'),
)

Q_METHOD_CHOICES = (
    ('fourier',"Fourier's Law / Product / Interval Method"),
    ('bullard',"Bullard Method"),
    ('bootsrap',"Bootstrap Method"),
)

PROBE_TYPE = (
    ('corer-outrigger','Corer-outrigger'),
    ('bullard','Bullard Probe'),
    ('lister/violin','Lister Violin-Bow Probe'),
    ('ewing','Ewing Probe'),
    ('other','Other'),
    ('unspec','Not Specified'),
)

HEAT_TRANSFER = (
    ('conductive','Conductive'),
    ('convective_unspec','Convective Unspecified'),
    ('convective_upflow','Convective Upflow'),
    ('convective_downflow','Convective Downflow'),
    ('unspec','Not Specified'),
)