
SITE_TYPE = (   ('W','well'),
                ('O','outcrop'),
                ('S','sea floor'),
                ('L','lake bottom'),)          
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
                'site_type',
                # 'country',
                # 'region',
                # 'sub_region',
                # 'geological_province',
                # 'sea', 
                'seamount_distance',
                'sediment_thickness',
                'sediment_thickness_type',
                'crustal_thickness',
                'surface_temp',
                'bottom_water_temp',
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
            'heat_flow_corrected',
            'heat_flow_corrected_uncertainty',
            'heat_flow_uncorrected',
            'heat_flow_uncorrected_uncertainty',

            'gradient_corrected',
            'gradient_corrected_uncertainty',
            'gradient_uncorrected',
            'gradient_uncorrected_uncertainty',

            'thermal_conductivity',
            'conductivity_uncertainty',
            'number_of_conductivities',
            'conductivity_method',

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

            # 'reference',
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
            'value',
            'uncertainty',
            'orientation',
            'method',
            'rock_group',
            'rock_origin',
            'rock_type',
            # 'geo_unit',
            'depth',
            'age',
            'age_min',
            'age_max',
            'age_method',
            'reference',
            'comment'           
            ]

HEAT_GEN_FIELDS = CONDUCTIVITY_FIELDS.copy()
HEAT_GEN_FIELDS.remove('orientation')

TEMPERATURE_FIELDS = [
            'value',
            'depth',
            'method',
            'lag_time',
            'is_bottom_of_hole',
            'reference',
            'comment',           
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
    bottom_hole_temp='&deg;C',
    well_depth='m',






)