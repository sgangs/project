import random, time

START_TIME = 2**39+1

def make_id():
    t = int(time.time()*1000) - START_TIME
    u = random.SystemRandom().getrandbits(23)
    id = (t << 23 ) | u
    return id

def reverse_id_time(id):
    t  = id >> 23
    return (t + START_TIME)/1000