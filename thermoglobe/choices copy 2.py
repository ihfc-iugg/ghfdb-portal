
SITE_TYPE = (   ('W','Well'),
                ('O','Outcrop'),
                ('S','Sea Floor'),
                ('L','Lake Bottom'),)          

ROCK_GROUPS = ( ('M','Metamorphic'),
                ('I','Igneous'),
                ('S','Sedimentary'),
                ('MI','Meta-Igneous'),
                ('MS','Meta-Sedimentary'),)
ROCK_ORIGIN = ( ('P','Plutonic'),
                ('V','Volcanic'),)

SITE_FIELDS = [
                'site_name',
                'latitude',
                'longitude',
                'elevation',
                'dip', 
                'well_depth',
                'site_type',
                'site_status',
                'country',
                'region',
                'sub_region',
                'geological_province',
                'USGS_code',
                'sea', 
                'seamount_distance',
                'sediment_thickness',
                'crustal_thickness',
                'basin',
                'sub_basin',
                'tectonic_environment',
                'ruggedness',
                'surface_temp',
                'bottom_hole_temp',
                'age_min',
                'age_max',
                'age_method',
                'tectonothermal_min',
                'tectonothermal_max',
                'juvenile_age_min',
                'juvenile_age_max',
                'operator',
                'cruise',
                'EOH_geo_unit',
                'EOH_rock_type',
                ]   

SITE_FIELDS_BASIC = [
                'site_name',
                'latitude',
                'longitude',
                'elevation',
                ] 
        
HEAT_FLOW_EXPORT_ORDER = ['site__'+field for field in SITE_FIELDS] + [
            'depth_min',
            'depth_max',
            'reliability',
            'corrected',
            'corrected_uncertainty',
            'uncorrected',
            'uncorrected_uncertainty',

            # 'thermal_gradient_corrected',
            # 'gradient_corrected_uncertainty',
            # 'gradient_uncorrected',
            # 'gradient_uncorrected_uncertainty',

            'conductivity',
            'conductivity_uncertainty',
            'number_of_conductivities',
            'conductivity_method',

            # 'has_climatic',
            # 'correction__climatic',
            # 'has_topographic',
            # 'correction__topographic',
            # 'has_refraction',
            # 'correction__refraction',
            # 'has_sedimentation',
            # 'correction__sedimentation',
            # 'has_fluid',
            # 'correction__fluid',
            # 'has_bottom_water_variation',
            # 'correction__bottom_water_variation',
            # 'has_compaction',
            # 'correction__compaction',
            # 'has_other',
            # 'correction__other',

            # 'lithology',
            'reference',
            'comment',
            ]

HEAT_FLOW_EXPORT_BASIC = SITE_FIELDS_BASIC + [
            'depth_min',
            'depth_max',
            'reliability',
            'heatflow_corrected',
            'heatflow_uncorrected',
            'thermal_gradient_corrected',
            'gradient_uncorrected',
            'thermal_conductivity',
            'reference',
            'comment',
            ]
   
PROPERTY_EXPORT_ORDER = SITE_FIELDS + [
            'sample_name',
            'value',
            'uncertainty',
            'method',
            'rock_group',
            'rock_origin',
            'rock_type',
            'geo_unit',
            'depth',
            'age',
            'age_min',
            'age_max',
            'age_method',
            'is_core',
            'reference',
            'comment'           
            ]

PROPERTY_EXPORT_BASIC = SITE_FIELDS_BASIC + [
            'sample_name',
            'value',
            'uncertainty',
            'method',
            'rock_group',
            'rock_origin',
            'rock_type',
            'geo_unit',
            'depth',
            'age',
            'age_min',
            'age_max',
            'age_method',
            'is_core',
            'reference',
            'comment'           
            ]

TEMPERATURE_EXPORT_ORDER = SITE_FIELDS + [
            'value',
            'depth',
            'method',
            'lag_time',
            'is_bottom_of_hole',
            'reference',
            'comment',           
            ]

TEMPERATURE_EXPORT_BASIC = SITE_FIELDS_BASIC + [
            'value',
            'depth',
            'method',
            'lag_time',
            'is_bottom_of_hole',
            'reference',
            'comment',           
            ]