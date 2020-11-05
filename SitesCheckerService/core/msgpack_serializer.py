import msgpack
from datetime import datetime


def encode_datetime(obj):
    if isinstance(obj, datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f").encode()}
    return obj


def decode_datetime(obj):
    if '__datetime__' in obj:
        obj = datetime.strptime(obj['as_str'], "%Y%m%dT%H:%M:%S.%f")
    return obj


def packb(msg: dict):
    return msgpack.packb(msg, default=encode_datetime)


def unpackb(msg: bytes):
    return msgpack.unpackb(msg, raw=False, object_hook=decode_datetime)