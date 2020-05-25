from control import tf

def pi(Ki,Ti):
    return tf([Ki*Ti,Ki],[Ti,0])
