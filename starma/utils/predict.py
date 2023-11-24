#!/usr/bin/python
# -*- coding: utf-8 -*-

#  作者：马欣宇
#  时间：2019-3-27
#  文件描述：用STARMA模型对每一个位置点的事故数，死亡人数，重伤人数，轻伤人数做预测

from refs.pySTARMA.pySTARMA import starma_model as sm
from refs.utils import dataIntegration


# 返回的信息为 道路：【起点坐标，道路长度，【【事故坐标，事故数，死亡人数，重伤人数，轻伤人数,事故编号】，【事故坐标，事故数，死亡人数，重伤人数，轻伤人数，事故编号】...】】，道路2：...
def predict(file_1, file_2):
    # 事故编号
    acci_num = 0
    # 每条道路的四个时间空间矩阵,三阶空间权值矩阵，每个位置的代表事故点格式为  道路1：【事故数时间空间矩阵，死亡人数时间空间矩阵，重伤人数时间空间矩阵，轻伤人数时间空间矩阵，一阶空间权值矩阵，二阶空间权值矩阵，三阶空间权值矩阵,每个位置的代表事故点】；道路2：【时间空间矩阵...
    di = dataIntegration.dataIntegration(file_1, file_2)
    # 对每一条道路，预测事故数矩阵，死亡人数矩阵，重伤人数矩阵，轻伤人数矩阵，再加一个位置代表事故点字典
    totaldata = di.intergration()

    predict_data = {}
    for street in totaldata.keys():
        predict_data[street] = [totaldata[street][0], totaldata[street][1], []]
        data = totaldata[street][2]
        event_ts = data[0]
        die_ts = data[1]
        severe_ts = data[2]
        mild_ts = data[3]
        spatial_mx1 = data[4]
        spatial_mx2 = data[5]
        spatial_mx3 = data[6]
        represent_accident = data[7]
        # print('street:', street, represent_accident)

        # Create instance of STARMA
        model = sm.STARMA(5, 2, event_ts, [spatial_mx1, spatial_mx2, spatial_mx3], 3)
        # Estimate parameters
        model.fit()

        # Print explicit item
        event_pred = model.predict(event_ts, 5)
        die_pred = model.predict(die_ts, 5)
        severe_pred = model.predict(severe_ts, 5)
        mild_pred = model.predict(mild_ts, 5)

        # 整合预测出的数据
        for represent in represent_accident:
            location = [represent_accident[represent][6], represent_accident[represent][7]]
            col = represent - 1
            acci_num = acci_num + 1
            predict_data[street][2].append([location, sum(event_pred[:, col]), sum(die_pred[:, col]), sum(severe_pred[:, col]), sum(mild_pred[:, col]), acci_num])
    return predict_data


# file1 = 'file_toTry/time_accident.csv'
# file2 = 'file_toTry/roads.csv'
# pre = predict(file1, file2)
# for street in pre.keys():
#     print('street:', street)
#     print('street start from:',pre[street][0])
#     print('street length:', pre[street][1])
#     for accident in pre[street][2]:
#         print(accident)
#     print("=====================")



