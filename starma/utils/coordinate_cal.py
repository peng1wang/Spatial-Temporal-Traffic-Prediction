# !/usr/bin/python
# -*- coding: utf-8 -*-

#  作者：马欣宇
#  时间：2019-3-26
#  文件描述：用于一系列与经纬度有关的计算
# 1.类cal_distance用于计算两个经纬度表示的点的实际距离（m)
# 2.类CenterPointFromListOfCoordinates用于计算多个经纬度坐标的中心点

import math

# 计算距离
class cal_distance:
    def __init__(self, **kwargs):
        self.lat1 = kwargs.get('lat1')
        self.lon1 = kwargs.get('lon1')
        self.lat2 = kwargs.get('lat2')
        self.lon2 = kwargs.get('lon2')

    def twopoint_distance(self):
        R = 6371.393
        dlat = self.deg2rad(self.lat2 - self.lat1)
        dlon = self.deg2rad(self.lon2 - self.lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(self.deg2rad(self.lat1)) * math.cos(self.deg2rad(self.lat2)) * math.sin(
            dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c * 1000

    def deg2rad(self, deg):
        return deg * (math.pi / 180)



class CenterPointFromListOfCoordinates:
    def center_geolocation(self, geolocations):
        """
        输入多个经纬度坐标，找出中心点
        :param geolocations: 集合
        :return:
        """
        x = 0
        y = 0
        z = 0
        length = len(geolocations)
        for lon, lat in geolocations:
            lon = math.radians(float(lon))
            lat = math.radians(float(lat))
            x += math.cos(lat) * math.cos(lon)
            y += math.cos(lat) * math.sin(lon)
            z += math.sin(lat)

        x = float(x / length)
        y = float(y / length)
        z = float(z / length)

        return math.degrees(math.atan2(y, x)), math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))
