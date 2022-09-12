SITE_TYPE = (   ('C','continental'),
                ('O','oceanic'),)


# ========== EXPORT SETS ==============
SITE = [
                'id',
                'name',
                'lat',
                'lng',
                'elevation',
                'well_depth',
                'seamount_distance',
                'sediment_thickness',
                'sediment_thickness_type',
                'crustal_thickness',
                'bottom_water_temp',
                'cruise',
                'site__country',
                'site__continent',
                'site__political',
                'site__sea',
                'site__province',
                'site__plate',

                ]   

intervals = SITE + [
            'q_top',
            'q_bot',
            'tilt',
            'num_temp',
            'temp_method',

            'heat_flow_corrected',
            'heat_flow_corrected_uncertainty',
            'heat_flow_uncorrected',
            'heat_flow_uncorrected_uncertainty',

            'gradient_corrected',
            'gradient_corrected_uncertainty',
            'gradient_uncorrected',
            'gradient_uncorrected_uncertainty',

            'tc_mean',
            'cond_unc',
            'num_cond',
            'cond_method',
        ]


conductivity = SITE + [
            'depth',
            'sample_name',
            'conductivity',
            'uncertainty',
            'orientation',
            'method',
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

heat_production = SITE + [
            'depth',
            'heat_production',
            'uncertainty',
            'method',
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

temperature = SITE + [
            'temperature',
            'uncertainty',
            'depth',
            'method',
            'source',
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