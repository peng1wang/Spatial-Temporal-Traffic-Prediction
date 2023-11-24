# !/usr/bin/python
# -*- coding: utf-8 -*-

#  作者：马欣宇
#  时间：2019-3-26
#  文件描述：
#  1.用于在道路文件输入时给出地图显示的中心点，以便前端人员显示地图
#  2.用于计算道路全长

import pandas as pd
import numpy as np
from refs.utils import coordinate_cal
import json


class handle_street:
    def __init__(self, file2):
        data2 = pd.read_csv(file2)
        self.data2 = np.array(data2)

    #  用道路文件中的第一条道路中心点做地图显示的中心
    def getMapCenter(self):
        firstStreet = self.data2[0]
        location1 = [firstStreet[2], firstStreet[3]]  # 起始点经纬度
        location2 = [firstStreet[4], firstStreet[5]]  # 终止点经纬度
        cul_cp = coordinate_cal.CenterPointFromListOfCoordinates()
        return cul_cp.center_geolocation([location1, location2])

    #  计算每条道路的全长和起点，格式为： 道路编号：【长度，起点】
    def getStreetAttr(self):
        streetAttr = {}
        for street in self.data2:
            if street[0] not in streetAttr.keys():
                cal = coordinate_cal.cal_distance(lat1=street[3], lon1=street[2], lat2=street[5], lon2=street[4])
                streetAttr[street[0]] = [cal.twopoint_distance(), [street[2], street[3]]]
        return streetAttr

    # 获取地图显示中心点的json
    def getMapCenterJson(self):
        location = self.getMapCenter()
        locationDict = {}
        locationDict["center_lon"] = location[0]
        locationDict["center_lat"] = location[1]
        return json.dumps(locationDict)


# file1 = 'file_toTry/time_accident.csv'
# file2 = 'file_toTry/roads.csv'
# h = handle_street(file2)
# print(h.getMapCenterJson())



