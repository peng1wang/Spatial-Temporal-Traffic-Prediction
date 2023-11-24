#!/usr/bin/python
# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import math
from refs.utils import handle_streetFile, coordinate_cal


class dataIntegration:
    def __init__(self, file_1, file_2):
        data1 = pd.read_csv(file_1)
        self.data1 = np.array(data1)
        self.file_2 = file_2

    # 按道路整合数据,返回格式为 道路1：【事故1，事故2，...】，道路2：...
    def splitStreet(self, data):
        info = {}
        for accident in data:
            if accident[2] not in info.keys():
                info[accident[2]] = []
            info[accident[2]].append(accident)
        return info

    # 获取日期中的月份
    def getMonth(self,dateString):
        return int(dateString.split('/')[1])

    # 整合数据，返回
    # 每条道路的四个时间空间矩阵,三阶空间权值矩阵，每个位置的代表事故点格式为  道路1：【道路起点，道路长度，【事故数时间空间矩阵，死亡人数时间空间矩阵，重伤人数时间空间矩阵，轻伤人数时间空间矩阵，一阶空间权值矩阵，二阶空间权值矩阵，三阶空间权值矩阵,每个位置的代表事故点】】；道路2：【...】...
    def intergration(self):
        data_after = {}
        streetInfo = self.splitStreet(self.data1)

        # 每条道路的长度
        streetFile = handle_streetFile.handle_street(self.file_2)
        streetAttr = streetFile.getStreetAttr()

        # 空间权值矩阵的三个边界值
        border1 = 50
        border2 = 100
        border3 = 150

        # 为每条道路计算时间空间矩阵和三个空间权值矩阵
        for street in streetInfo.keys():
            # 一条道路上的所有事故
            allAccidents = streetInfo[street]

            # 每条道路的地点划分单元为100m
            unit = 100

            # 道路上共有几个位置点
            data = streetAttr[street][0]/unit
            locationNum = math.ceil(data)

            # 道路起点
            endPoint = streetAttr[street][1]

            # 一阶空间权值矩阵，距离小于border1标为1
            spatial_mx1 = np.zeros((locationNum, locationNum))
            # 二阶空间权值矩阵，距离大于等于border1，小于border2标为1
            spatial_mx2 = np.zeros((locationNum, locationNum))
            # 三阶空间权值矩阵，距离大于等于border2，小于border3标为1
            spatial_mx3 = np.zeros((locationNum, locationNum))

            # 事故数时间空间矩阵
            ts_mx1 = np.zeros((12, locationNum))
            # 死亡人数时间空间矩阵
            ts_mx2 = np.zeros((12, locationNum))
            # 重伤人数时间空间矩阵
            ts_mx3 = np.zeros((12, locationNum))
            # 轻伤人数时间空间矩阵
            ts_mx4 = np.zeros((12, locationNum))

            # 每一个位置点的代表事故，格式为 位置点：事故，位置点：事故...
            represent_accident = {}

            for accident in allAccidents:
                month = self.getMonth(accident[1])
                cal = coordinate_cal.cal_distance(lon1=endPoint[0], lat1=endPoint[1], lon2=accident[6], lat2=accident[7])
                location = int(cal.twopoint_distance() / unit)


                # 更新位置的代表事故点
                if location not in represent_accident.keys():
                    represent_accident[location] = accident
                else:
                    if accident[3]>represent_accident[month][3]:
                        represent_accident[month] = accident
                    elif accident[3]==represent_accident[month][3]:
                        if accident[4]>represent_accident[month][4]:
                            represent_accident[month] = accident
                        elif accident[4]==represent_accident[month][4]:
                            if accident[5]>represent_accident[month][5]:
                                represent_accident[month] = accident

                # 构建四个时间空间矩阵，以便分别做预测
                ts_mx1[month - 1][location - 1] += 1
                ts_mx2[month - 1][location - 1] += accident[3]
                ts_mx3[month - 1][location - 1] += accident[4]
                ts_mx4[month - 1][location - 1] += accident[5]

            # 构建空间权值矩阵
            for lo1 in range(locationNum):
                if lo1 in represent_accident.keys():
                    accident1 = represent_accident[lo1]
                    for lo2 in represent_accident.keys():
                        accident2 = represent_accident[lo2]
                        cal = coordinate_cal.cal_distance(lon1=accident1[6], lat1=accident1[7], lon2=accident2[6], lat2=accident2[7])
                        distance = cal.twopoint_distance()
                        if distance < border1:
                            spatial_mx1[lo1][lo2] = 1
                        elif distance < border2:
                            spatial_mx2[lo1][lo2] = 1
                        elif distance < border3:
                            spatial_mx3[lo1][lo2] = 1

            data_after[street] = [endPoint, streetAttr[street][0], [ts_mx1, ts_mx2, ts_mx3, ts_mx4, spatial_mx1, spatial_mx2, spatial_mx3, represent_accident]]

        return data_after







