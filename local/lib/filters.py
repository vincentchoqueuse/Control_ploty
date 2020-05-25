import math

def moodle_numerical(value,tolerance=0.1):
    
    abs_tolerance = value*tolerance
    abs_tolerance = math.ceil(abs_tolerance*100)/100
    return "{{1:NUMERICAL:={}:{}}}".format(value,abs_tolerance)


def moodle_filter_type(type):
    filter_list =["passe bas","passe haut","passe bande","réjecteur"]
    if type == "LP":
        filter_list[0] = "={}".format(filter_list[0])
    if type == "HP":
        filter_list[1] = "={}".format(filter_list[1])
    if type == "BP":
        filter_list[2] = "={}".format(filter_list[2])
    if type == "Notch":
        filter_list[3] = "={}".format(filter_list[3])

    moodle_str = " ~".join(filter_list)
    return "{{1:MC:{} }}".format(moodle_str)


