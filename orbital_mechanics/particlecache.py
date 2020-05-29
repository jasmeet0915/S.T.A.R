import pandas as pd
import os
import struct
from os import path
from math import *
import random

def pack_string(v, size):
    return struct.pack('%ds' % size, v.encode(encoding='UTF-8'))


def unpack_string(b, size):
    return struct.unpack('%ds' % size, b)[0].decode(encoding='UTF-8')


def pack_uint(v):
    return struct.pack('I', v)


def unpack_uint(b):
    return struct.unpack('I', b)[0]


def pack_float(v):
    return struct.pack('f', v)


def unpack_float(b):
    return struct.unpack('f', b)[0]


def pack_vector(v):
    return struct.pack('fff', v[0], v[1], v[2])


def unpack_vector(b):
    return struct.unpack('fff', b)


def pack_quaternion(v):
    return struct.pack('ffff', v[0], v[1], v[2], v[3])


def unpack_quaternion(b):
    return struct.unpack('ffff', b)


def pack_color(v):
    return struct.pack('ffff', v[0], v[1], v[2], v[3])


def unpack_color(b):
    return struct.unpack('ffff', b)


class ParticleTimes:
    __slots__=('birthtime', 'lifetime', 'dietime')

    def __init__(self, birthtime, lifetime, dietime):
        self.birthtime=birthtime
        self.lifetime=lifetime
        self.dietime=dietime


def pack_particle_times(v):
    return struct.pack('fff', v.birthtime, v.lifetime, v.dietime)


def unpack_particle_times(b):
    birthtime, lifetime, dietime=struct.unpack('fff', b)
    return ParticleTimes(birthtime, lifetime, dietime)


class BoidData:
    __slots__=('health', 'acceleration', 'state_id', 'mode')

    def __init__(self, health, acceleration, state_id, mode):
        self.health=health
        self.acceleration=acceleration
        self.state_id=state_id
        self.mode=mode


def pack_boid(v):
    return struct.pack('ffffhh', v.health, v.acceleration[0], v.acceleration[1], v.acceleration[2], v.state_id, v.mode)


def unpack_boid(b):
    health, acc0, acc1, acc2, state_id, mode=struct.unpack('ffffhh', b)
    return BoidData(health, (acc0, acc1, acc2), state_id, mode)


_flag_map={
    0x00010000: 'compress',
    0x00020000: 'extra_data',
}


class TypeDesc:
    """Data type descriptor"""

    def __init__(self, index, name, size, pack, unpack):
        self.index=index
        self.name=name
        self.size=size
        self.pack=pack
        self.unpack=unpack

    def __str__(self):
        return self.name

    def __repr__(self):
        return "TypeDesc(name=%r, size=%d)" % (self.name, self.size)


_data_types_softbody=(
    TypeDesc(1, 'LOCATION', 12, pack_vector, unpack_vector),
    TypeDesc(2, 'VELOCITY', 12, pack_vector, unpack_vector),
)

_data_types_particles=(
    TypeDesc(0, 'INDEX', 4, pack_uint, unpack_uint),
    TypeDesc(1, 'LOCATION', 12, pack_vector, unpack_vector),
    TypeDesc(2, 'VELOCITY', 12, pack_vector, unpack_vector),
    TypeDesc(3, 'ROTATION', 16, pack_quaternion, unpack_quaternion),
    TypeDesc(4, 'AVELOCITY', 12, pack_vector, unpack_vector),
    TypeDesc(5, 'SIZE', 4, pack_float, unpack_float),
    TypeDesc(6, 'TIMES', 12, pack_particle_times, unpack_particle_times),
    TypeDesc(7, 'BOIDS', 20, pack_boid, unpack_boid),
)

_data_types_cloth=(
    TypeDesc(1, 'LOCATION', 12, pack_vector, unpack_vector),
    TypeDesc(2, 'VELOCITY', 12, pack_vector, unpack_vector),
    TypeDesc(4, 'XCONST', 12, pack_vector, unpack_vector),
)

_data_types_smoke=(
    TypeDesc(1, 'SMOKE_LOW', 12, pack_vector, unpack_vector),
    TypeDesc(2, 'SMOKE_HIGH', 12, pack_vector, unpack_vector),
)

_data_types_dynamicpaint=(
    TypeDesc(3, 'DYNAMICPAINT', 16, pack_color, unpack_color),
)

_data_types_rigidbody=(
    TypeDesc(1, 'LOCATION', 12, pack_vector, unpack_vector),
    TypeDesc(3, 'ROTATION', 16, pack_quaternion, unpack_quaternion),
)

_type_map={
    0: ('SOFTBODY', _data_types_softbody),
    1: ('PARTICLES', _data_types_particles),
    2: ('CLOTH', _data_types_cloth),
    3: ('SMOKE_DOMAIN', _data_types_smoke),
    4: ('SMOKE_HIGHRES', _data_types_smoke),
    5: ('DYNAMICPAINT', _data_types_dynamicpaint),
    6: ('RIGIDBODY', _data_types_rigidbody),
}


def cache_file_list(directory, index=0):
    """Cache frame files in a directory, sorted by frame
    """

    return sorted(cache_files(directory, index), key=lambda item: item[0])


def cache_files(directory, index=0):
    """Cache frame files in a directory
    """

    for filename in os.listdir(directory):
        try:
            base, ext=path.splitext(filename)
            parts=base.split('_')
            if len(parts) in (2, 3):
                cframe=int(parts[1])
                cindex=int(parts[2]) if len(parts) >= 3 else 0
                if cindex == index:
                    yield cframe, filename
        except:
            pass


class CacheFrame():
    def __init__(self, filename):
        self.filename = filename
        self.totpoint = 0
        self.data_types = tuple()
        self.data = tuple()

    def get_data_type(self, name):
        for dt in self.data_types:
            if dt.name == name:
                return dt
        return None

    def get_data(self, name):
        for dt, data in zip(self.data_types, self.data):
            if dt.name == name:
                return data
        return None

    def set_data(self, name, values):
        self.data = tuple(data if dt.name != name else values for dt, data in zip(self.data_types, self.data))

    def read(self, directory, read_data):
        cachetype = ""
        data_types = {}

        f = open(path.join(directory, self.filename), "rb")
        try:
            cachetype, data_types = self.read_header(f)

            if read_data:
                self.read_points(f)
            else:
                self.data = None

        finally:
            f.close()

        return cachetype, data_types

    def read_header(self, f):
        bphysics = unpack_string(f.read(8), 8)
        if bphysics != 'BPHYSICS':
            raise Exception("Not a valid BPHYSICS cache file")

        typeflag = unpack_uint(f.read(4))

        cachetype, data_types = _type_map[typeflag & 0x0000FFFF]
        self.cachetype = cachetype

        for bits, flag in _flag_map.items():
            setattr(self, flag, bool(typeflag & bits))

        self.totpoint = unpack_uint(f.read(4))

        data_types_flag = unpack_uint(f.read(4))
        # frame has filtered data types list in case not all data types are stored
        self.data_types = tuple(filter(lambda dt: ((1<<dt.index) & data_types_flag) != 0, data_types))

        return cachetype, data_types

    def read_points(self, f):
        data = tuple([None] * self.totpoint for dt in self.data_types)

        if self.compress:
            raise Exception("Compressed caches are not supported yet, sorry ...")
            return data

        def interleaved():
            for k in range(self.totpoint):
                yield k, tuple(dt.unpack(f.read(dt.size)) if dt else None for dt in self.data_types)

        for k, data_point in interleaved():
            for data_list, value in zip(data, data_point):
                data_list[k] = value

        self.data = data

    def write(self, directory):
        f = open(path.join(directory, self.filename), "wb")
        try:
            self.write_header(f)
            self.write_points(f)

        finally:
            f.close()

    def write_header(self, f):
        f.write(pack_string('BPHYSICS', 8))

        typeflag = 0
        for index, (name, _) in _type_map.items():
            if name == self.cachetype:
                typeflag = typeflag | index
                break

        for bits, flag in _flag_map.items():
            if getattr(self, flag):
                typeflag = typeflag | bits

        f.write(pack_uint(typeflag))

        f.write(pack_uint(self.totpoint))

        data_types_flag = 0
        for dt in self.data_types:
            data_types_flag = data_types_flag | (1<<dt.index)
        f.write(pack_uint(data_types_flag))

    def write_points(self, f):
        if self.compress:
            raise Exception("Compressed caches are not supported yet, sorry ...")
            return data

        for k in range(self.totpoint):
            for data, dt in zip(self.data, self.data_types):
                f.write(dt.pack(data[k]))

class PointCache():
    def __init__(self, directory, index=0):
        self.files = cache_file_list(directory, index)
        if not self.files:
            raise Exception("No point cache files for index %d in directory %s" % (index, directory))

        self.start_frame, self.info_filename = self.files[0]
        self.end_frame, self.last_filename = self.files[-1]

        info_frame = CacheFrame(self.info_filename)
        cachetype, data_types = info_frame.read(directory, read_data=False)

        self.cachetype = cachetype
        self.data_types = data_types

        for flag in _flag_map.values():
            setattr(self, flag, getattr(info_frame, flag))
        self.totpoint = info_frame.totpoint

    def get_data_type(self, name):
        for dt in self.data_types:
            if dt.name == name:
                return dt
        return None
    



