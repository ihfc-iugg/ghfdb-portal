
ROCK_GROUPS = ( ('M','metamorphic'),
                ('I','igneous'),
                ('S','sedimentary'),
                ('MI','meta-igneous'),
                ('MS','meta-sedimentary'),)
ROCK_ORIGIN = ( ('P','plutonic'),
                ('V','volcanic'),)

# ========== FIELD SETS ==============
SITE_FIELDS = [
                'site_name',
                'latitude',
                'longitude',
                'elevation',
                'well_depth',
                # 'site_type',

                'seamount_distance',
                'sediment_thickness',
                'sediment_thickness_type',
                'crustal_thickness',
                'surface_temp',
                'bottom_water_temp',
                # 'operator',
                'cruise',
                ]   

SITE_FIELDS_BASIC = [
                'site_name',
                'latitude',
                'longitude',
                'elevation',
                ] 

HEAT_FLOW_FIELDS = [
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

            'climate_flag',
            'climate_correction',
            'topographic_flag',
            'topographic_correction',
            'refraction_flag',
            'refraction_correction',
            'sed_erosion_flag',
            'sed_erosion_correction',
            'fluid_flag',
            'fluid_correction',
            'bottom_water_variation_flag',
            'bottom_water_variation_correction',
            'compaction_flag',
            'compaction_correction',
            'other_flag',
            'other_type',
            'other_correction',

            'global_flag',
            'comment',
            ]

HEAT_FLOW_FIELDS_BASIC = [
            'depth_min',
            'depth_max',
            'reliability',
            'heatflow_corrected',
            'heatflow_uncorrected',
            'gradient_corrected',
            'gradient_uncorrected',
            'thermal_conductivity',
            'reference',
            'comment',
            ]

CONDUCTIVITY_FIELDS = [
            'sample_name',
            'conductivity',
            'uncertainty',
            'orientation',
            'sample_thickness',
            'sample_length',
            'sample_width',
            'sample_diameter',
            'method',
            'formation',
            'rock_group',
            'rock_origin',
            'rock_type',
            'depth',
            'age',
            'age_type',
            'year_logged',
            'operator',
            'reference',
            'comment',
            'source',
            'source_id',    
            'log_id',
            ]

HEAT_GEN_FIELDS = [
            'sample_name',
            'heat_generation',
            'uncertainty',
            'method',
            'formation',
            'rock_group',
            'rock_origin',
            'rock_type',
            'depth',
            'age',
            'age_type',
            'year_logged',
            'operator',
            'reference',
            'comment',
            'source',
            'source_id',    
            'log_id',
            ]

TEMPERATURE_FIELDS = [
            'temperature',
            'uncertainty',
            'depth',
            'method',

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

# ========== EXPORT SETS ==============

HEAT_FLOW_EXPORT = SITE_FIELDS + HEAT_FLOW_FIELDS
HEAT_FLOW_EXPORT_BASIC = SITE_FIELDS_BASIC + HEAT_FLOW_FIELDS_BASIC
   

CONDUCTIVITY_EXPORT = SITE_FIELDS + CONDUCTIVITY_FIELDS
CONDUCTIVITY_EXPORT_BASIC = SITE_FIELDS_BASIC + CONDUCTIVITY_FIELDS


HEAT_GEN_EXPORT = SITE_FIELDS + HEAT_GEN_FIELDS
HEAT_GEN_EXPORT_BASIC = SITE_FIELDS_BASIC + HEAT_GEN_FIELDS


TEMPERATURE_EXPORT = SITE_FIELDS + TEMPERATURE_FIELDS
TEMPERATURE_EXPORT_BASIC = SITE_FIELDS_BASIC + TEMPERATURE_FIELDS

# Can write these in html
UNITS = dict(
    elevation='m',
    age_min='Ma',
    age_max='Ma',
    tectonothermal_min='Ma',
    tectonothermal_max='Ma',
    juvenile_age_min='Ma',
    juvenile_age_max='Ma',
    seamount_distance='km',
    outcrop_distance='km',
    sediment_thickness='km',
    crustal_thickness='km',
    surface_temp='&deg;C',
    well_depth='m',






)