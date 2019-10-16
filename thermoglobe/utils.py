
from django.db.models import Avg, Count, Func, FloatField

class Round(Func):
    function = 'ROUND'
    template="%(function)s(%(expressions)s::numeric, 2)"

def get_db_summary(qs):

    heat_flow_sites = Count('heatflow',distinct=True)
    heat_flow_uncorrected = Count('heatflow__uncorrected', ouput_field=FloatField())
    heat_flow_corrected = Count('heatflow__corrected', ouput_field=FloatField())
    thermal_conductivity=Count('conductivity',distinct=True)
    heat_generation=Count('heatgeneration',distinct=True)
    thermal_gradient=Count('temperaturegradient',distinct=True)
    temperature=Count('temperature',distinct=True)

    # Calculates information on the current Site query
    counts = qs.aggregate(
        heat_flow_sites=heat_flow_sites,
        heat_flow_uncorrected=heat_flow_uncorrected,
        heat_flow_corrected=heat_flow_corrected,
    )
    # the following counts do not play nicely with the ones above, must keep seperate and join later
    counts2 = qs.aggregate(
        thermal_conductivity=thermal_conductivity,
        heat_generation=heat_generation,
        thermal_gradient=thermal_gradient,
        temperature=temperature,
    )  
    counts.update(counts2)


    heatflow_ave = ((Avg('heatflow__uncorrected', ouput_field=FloatField()) * heat_flow_uncorrected) + (Avg('heatflow__corrected', ouput_field=FloatField()) * heat_flow_corrected)) / (heat_flow_uncorrected + heat_flow_corrected)


    # calculating averages for separate table
    ave = qs.aggregate(
        heat_flow=Round(heatflow_ave, output_field=FloatField()),     

    )

    for i in [  qs.aggregate(thermal_conductivity=Round(Avg('conductivity__value'))),
                qs.aggregate(heat_generation=Round(Avg('heatgeneration__value'))),
                qs.aggregate(thermal_gradient=Round(Avg('temperaturegradient__uncorrected'))),
                qs.aggregate(temperature=Round(Avg('temperature__value'))),]:
        ave.update(i)

    return {'count': caps_dict_keys(counts),'average':caps_dict_keys(ave)}

def caps_dict_keys(my_dict):
    new_dict = {}
    for key in my_dict.keys():
        new_dict[key.replace('_',' ').title()] = my_dict[key]
    return new_dict


