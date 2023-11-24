#!/usr/bin/python
# -*- coding: utf-8 -*-

#  作者：马欣宇
#  时间：2019-3-27
#  文件描述：用预测出来的数据做黑点识别，返回黑点的经纬度以及半径

from sklearn.cluster import KMeans
from sklearn import preprocessing
import numpy as np
import pandas as pd
import math
from collections import Counter
from refs.utils import predict, coordinate_cal
import json


class tellBP:
    def __init__(self, file_1, file_2):
        self.pre_data = predict.predict(file_1, file_2)

    # 用聚类的方法将道路危险程度聚为5类并返回最危险的道路，格式为  道路编号:事故数
    def findSevereStreet(self):
        feature = []  # [道路编号，事故数，死亡人数，受伤人数]
        severeStreet = {}  # 最严重的道路编号, 事故数
        for street in self.pre_data.keys():
            feature.append(
                [street, sum(np.array(self.pre_data[street][2])[:, 1]), sum(np.array(self.pre_data[street][2])[:, 2]),
                 sum(np.array(self.pre_data[street][2])[:, 3]) + sum(np.array(self.pre_data[street][2])[:, 4])])
        featureArray = np.array(feature)[:, 1:]
        featureArrayScaled = preprocessing.scale(featureArray)

        # 用最小离差平方和的聚类方法
        k = 5  # 道路危险程度，5类
        iteration = 500  # 聚类最大循环次数
        model = KMeans(n_clusters=k, n_jobs=4, max_iter=iteration)  # 分为k类, 并发数4
        model.fit(featureArrayScaled)  # 开始聚类

        center = np.array(pd.DataFrame(model.cluster_centers_))
        # 确定最严重的类severeClass
        maxResult = -1000
        severeClass = -1
        for classNum in range(5):
            result = 500 * center[classNum][1] + 100 * center[classNum][2] + center[classNum][0]
            if result > maxResult:
                severeClass = classNum
                maxResult = result

        for i in range(len(feature)):
            if model.labels_[i] == severeClass:
                severeStreet[feature[i][0]] = feature[i][1]
        return severeStreet

    # 计算最优累计频率,输入为道路事故数,各路段事故数,总路段数，道路长度。返回最优累计频率
    def culFrequency(self, streetEntNum, infoPerPriod, numOfPriod, length):
        frequency = {}
        for priod in infoPerPriod.keys():
            frequency[priod] = infoPerPriod[priod] * 1.00000 / streetEntNum
        frequency = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        # print(frequency)

        # %30的事故发生路段的长度比例
        ratio = 0
        for priod in range(numOfPriod):
            ratio += frequency[priod][1]
            if ratio >= 0.3:
                return (priod + 1) * 500 / length

        # 计算某事故点的事故严重程度, 输入的是某一事故点邻域半径内的的事故集合[[事故1][事故2][事故3]],输出为严重程度fs

    def eventDegree(self, accident):
        eventType = []  # 1代表死亡， 2代表重伤， 3代表轻伤
        for acci in accident:
            if (acci[3] >= acci[4]) & (acci[3] >= acci[5]):
                eventType.append(1)
            elif (acci[4] > acci[3]) & (acci[4] >= acci[5]):
                eventType.append(2)
            else:
                eventType.append(3)
        res = Counter(eventType)  # {严重程度：数量,...}
        degree = (res[1] + res[2]) * 9.5 + res[3] * 3.5
        return degree

        # 寻找某事故点邻域半径内的事故集合,输入为事故集合，此事故,邻域半径r，密度阈值minpts

    def findEvents(self, accidentForOneStreet, accident, r):
        rangeEvents = []
        location1 = [accident[6], accident[7]]
        for acci in accidentForOneStreet:
            location2 = [acci[6], acci[7]]
            cal = coordinate_cal.cal_distance(lon1=location1[0], lat1=location1[1], lon2=location2[0],
                                              lat2=location2[1])
            if cal.twopoint_distance() <= 200:
                # if acci[0] != accident[0]:
                rangeEvents.append(acci)
        return rangeEvents

        # 计算所有事故点的邻域集合事故

    def culRange(self, accidentForOneStreet, r):
        rangeForAllAcci = {}
        for accident in accidentForOneStreet:
            rangeForAllAcci[accident[0]] = self.findEvents(accidentForOneStreet, accident, r)
        return rangeForAllAcci


    def culInitDegree(self, accidentForOneStreet, r):
        degreeForEachAcci = {}
        rangeForAllAcci = self.culRange(accidentForOneStreet, r)
        for accident in accidentForOneStreet:
            rangeEvents = rangeForAllAcci[accident[0]]
            degree = self.eventDegree(rangeEvents)
            degreeForEachAcci[accident[0]] = [degree, accident[6], accident[7]]
        degreeForEachAcci = sorted(degreeForEachAcci.items(), key=lambda x: x[1], reverse=True)
        return degreeForEachAcci

    # 识别黑点，输入为核心点【【事故编号，经度，纬度，半径，严重程度】，【】，【】】，输出为【【事故编号，经度，纬度，半径，严重程度】，【】】
    def findBlackPoint(self, corePoint, minpts):
        coreNum = list(range(len(corePoint)))
        while (True):
            changed = False
            coreAmountBef = len(coreNum)  # 聚合之前的核心数
            num1 = 0
            while num1 < (coreAmountBef - 1):
                location1 = [corePoint[coreNum[num1]][1], corePoint[coreNum[num1]][2]]
                degree1 = corePoint[coreNum[num1]][4]
                range1 = corePoint[coreNum[num1]][3]
                num2 = num1 + 1
                while num2 < coreAmountBef:
                    location2 = [corePoint[coreNum[num2]][1], corePoint[coreNum[num2]][2]]
                    degree2 = corePoint[coreNum[num2]][4]
                    range2 = corePoint[coreNum[num2]][3]
                    cal = coordinate_cal.cal_distance(lon1=location1[0], lat1=location1[1], lon2=location2[0],
                                                      lat2=location2[1])
                    di = cal.twopoint_distance()
                    if di <= (range1 + range2) / 2:
                        location1 = coordinate_cal.center_geolocation([location1, location2])
                        range1 = max(range1, range2) + di / 2
                        degree1 = degree1 + degree2
                        corePoint[coreNum[num1]] = [corePoint[coreNum[num1]][0], location1[0], location1[1],
                                                    range1, degree1]
                        coreNum.pop(num2)
                        changed = True
                        coreAmountBef -= 1
                    else:
                        num2 += 1
                num1 += 1
            if changed == False:
                # print(coreNum)
                return np.array(corePoint)[coreNum]

    def getBP(self):
        result = []
        severeStreet = self.findSevereStreet()

        # 对每条危险道路识别黑点，将结果经纬度和半径存储
        for street in severeStreet.keys():
            exampleStreet = street

            # 获取当前道路上的所有事故
            # 由于使用了自己以前写的数据结构，所以这里花了一些步骤调整数据顺序，日后可以改进
            a = self.pre_data[street][2]
            accidentForOneStreet = []
            for accident in a:
                accidentForOneStreet.append(
                    [accident[5], 0, '', accident[2], accident[3], accident[4], accident[0][0], accident[0][1]])

            startxy = self.pre_data[street][0]
            length = self.pre_data[street][1]
            # 分为几段
            numOfPriod = math.ceil(length / 500)
            # print(numOfPriod)
            # print('\n')

            # 每一段(从第0段开始）的信息  段号：事故数
            infoPerPriod = {}
            for priod in range(numOfPriod):
                infoPerPriod[priod] = 0

            for accident in accidentForOneStreet:
                accidentLocation = [accident[6], accident[7]]
                # print(accidentLocation)
                cal = coordinate_cal.cal_distance(lon1=startxy[0], lat1=startxy[1], lon2=accidentLocation[0],
                                                  lat2=accidentLocation[1])
                d = cal.twopoint_distance()
                priod = int(d / 500)
                # print(priod)
                # 事故数加一
                infoPerPriod[priod] += 1

            # 最优累计频率
            bestFre = self.culFrequency(severeStreet[exampleStreet], infoPerPriod, numOfPriod, length)

            # 邻域半径为200米
            r = 200

            i = 1
            while (i < 30):
                minpts = i
                degreeForEachAccident = self.culInitDegree(accidentForOneStreet, r)
                # print(degreeForEachAccident)
                corePoint = []
                for acci in degreeForEachAccident:
                    if acci[1][0] >= minpts:
                        corePoint.append([acci[0], acci[1][1], acci[1][2], 200, acci[1][0]])

                bp = self.findBlackPoint(corePoint, minpts)
                bp = list(bp)
                if bp == []:
                    i -= 1
                    corePoint = []
                    for acci in degreeForEachAccident:
                        if acci[1][0] >= i:
                            corePoint.append([acci[0], acci[1][1], acci[1][2], 200, acci[1][0]])
                    break
                else:
                    bpLength = 0
                    for point in bp:
                        bpLength += point[3] * 2
                    if bpLength < length * bestFre:
                        break
                i += 1


            # print(i)
            # print(findBlackPoint(corePoint, i))
            bp = self.findBlackPoint(corePoint, i)
            # print(bp)
            for point in bp:
                result.append(point)
            return result

    def getBP_json(self):
        result = self.getBP()
        str = []
        for re in result:
            listunit = {}
            listunit["bp_num"] = re[0]
            listunit["bp_lon"] = re[1]
            listunit["bp_lat"] = re[2]
            listunit["bp_r"] = re[3]
            str.append(listunit)
        return json.dumps(str)



# file1 = 'file_toTry/time_accident.csv'
# file2 = 'file_toTry/roads.csv'
# model = tellBP(file1, file2)
# print(model.getBP_json())

# file = '结果.csv'
# np.savetxt(file,result,delimiter=',')

