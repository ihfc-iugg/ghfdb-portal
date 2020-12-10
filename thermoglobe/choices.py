SITE_TYPE = (   ('C','continental'),
                ('O','oceanic'),)

# ========== EXPORT SETS ==============
SITE_BASIC = [
            'id',
            'site_name',
            'latitude',
            'longitude',
            'elevation',
            'site__country__name',
            'site__sea__name',
            ] 

SITE_STANDARD = [
                'id',
                'site_name',
                'latitude',
                'longitude',
                'elevation',
                'well_depth',
                'seamount_distance',
                'sediment_thickness',
                'sediment_thickness_type',
                'crustal_thickness',
                # 'surface_temp',
                'bottom_water_temp',
                'cruise',
                'site__country__name',
                'site__sea__name',
                ]   

SITE_DETAILED = [
            'id',
            'site_name',
            'latitude',
            'longitude',
            'elevation',
            'well_depth',
            'seamount_distance',
            'sediment_thickness',
            'sediment_thickness_type',
            'crustal_thickness',
            # 'surface_temp',
            'bottom_water_temp',
            'cruise',
            'site__country__name',
            'site__sea__name',
            'site__country__name',
            'site__country__region',
            'site__country__subregion',
            'site__continent__name',
            'site__political__name',
            'site__province__name',
            'site__province__juvenile_age_min',
            'site__province__juvenile_age_max',
            'site__province__thermotectonic_age_min',
            'site__province__thermotectonic_age_max',
            'site__province__last_orogen',
                ]

HEAT_FLOW_BASIC = [
            'depth_min',
            'depth_max',
            'heat_flow',
            'gradient',
            'average_conductivity',
            'heat_generation',
            ]

HEAT_FLOW_STANDARD = [
            'depth_min',
            'depth_max',
            'reliability',
            'number_of_temperatures',
            'temp_method',

            'heat_flow_corrected',
            'heat_flow_corrected_uncertainty',
            'heat_flow_uncorrected',
            'heat_flow_uncorrected_uncertainty',

            'gradient_corrected',
            'gradient_corrected_uncertainty',
            'gradient_uncorrected',
            'gradient_uncorrected_uncertainty',

            'average_conductivity',
            'conductivity_uncertainty',

            'heat_generation',
            'heat_generation_uncertainty',

            ]

HEAT_FLOW_DETAILED = [
            'depth_min',
            'depth_max',
            'tilt',
            'reliability',
            'number_of_temperatures',
            'temp_method',

            'heat_flow_corrected',
            'heat_flow_corrected_uncertainty',
            'heat_flow_uncorrected',
            'heat_flow_uncorrected_uncertainty',

            'gradient_corrected',
            'gradient_corrected_uncertainty',
            'gradient_uncorrected',
            'gradient_uncorrected_uncertainty',

            'average_conductivity',
            'conductivity_uncertainty',
            'number_of_conductivities',
            'conductivity_method',

            'heat_generation',
            'heat_generation_uncertainty',
            'number_of_heat_gen',
            'heat_generation_method',
            
            'corrections__climate_flag',
            'corrections__climate',
            'corrections__topographic_flag',
            'corrections__topographic',
            'corrections__refraction_flag',
            'corrections__refraction',
            'corrections__sed_erosion_flag',
            'corrections__sed_erosion',
            'corrections__fluid_flag',
            'corrections__fluid',
            'corrections__bwv_flag',
            'corrections__bwv',
            'corrections__compaction_flag',
            'corrections__compaction',
            'corrections__other_flag',
            'corrections__other_type',
            'corrections__other',

            'global_flag',
            'comment',
        ]

CONDUCTIVITY_BASIC = [
            'depth',
            'sample_name',
            'conductivity',
            'uncertainty',
            'orientation',
            'method',
            ]

CONDUCTIVITY_STANDARD = CONDUCTIVITY_BASIC + [
            'sample_thickness',
            'sample_length',
            'sample_width',
            'sample_diameter',
            'formation',
            'rock_type',
            'year_logged',
            'operator',
            'reference',
            'comment',
            'source',
            'source_id',    
            'log_id',
        ]

HEAT_GEN_BASIC = [
            'depth',
            'heat_generation',
            'uncertainty',
            'method',
            ]

HEAT_GEN_STANDARD = HEAT_GEN_BASIC + [
            'formation',
            'rock_type',
            'year_logged',
            'operator',
            'reference',
            'comment',
            'source',
            'source_id',    
            'log_id',
        ]

TEMPERATURE_BASIC = [
            'temperature',
            'uncertainty',
            'depth',
            'method',
            'source',
            ]

TEMPERATURE_STANDARD = TEMPERATURE_BASIC + [
            'log_id',
            'year_logged',
            'circ_time',
            'lag_time',
            'correction',
            'formation',
            'operator',
            'comment',  
            'source',
            'source_id', 
            ]

heat_flow = dict(
    basic = SITE_BASIC + HEAT_FLOW_BASIC,
    standard = SITE_STANDARD + HEAT_FLOW_STANDARD,
    detailed = SITE_DETAILED + HEAT_FLOW_DETAILED,
    )

gradient = intervals = heat_flow

temperature = dict(
    basic = SITE_BASIC + TEMPERATURE_BASIC,
    standard = SITE_STANDARD + TEMPERATURE_STANDARD,
    detailed = SITE_DETAILED + TEMPERATURE_STANDARD,
    )

conductivity = dict(
    basic = SITE_BASIC + CONDUCTIVITY_BASIC,
    standard = SITE_STANDARD + CONDUCTIVITY_STANDARD,
    detailed = SITE_DETAILED + CONDUCTIVITY_STANDARD,
    )

heatgeneration = dict(
    basic = SITE_BASIC + HEAT_GEN_BASIC,
    standard = SITE_STANDARD + HEAT_GEN_STANDARD,
    detailed = SITE_DETAILED + HEAT_GEN_STANDARD,
    )
