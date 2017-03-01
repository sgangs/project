from hashids import Hashids
from django.conf import settings

def encoder(data):
    salter=settings.SALT
    hasher=Hashids(salt=salter, min_length=64)
    return hasher.encode(data)

def decoder(data):
    salter=settings.SALT
    hasher=Hashids(salt=salter, min_length=64)
    return hasher.decode(data)