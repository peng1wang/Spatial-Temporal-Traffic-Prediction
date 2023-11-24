#!/usr/bin/python
# -*- coding: utf-8 -*-

#  作者：马欣宇
#  时间：2019-3-27
#  文件描述：包含前后端交互所需的两个功能：
#  1. 用户输入本地的道路csv文件后，将路径传给后端，后端返回json格式的地图显示中心点
#  2. 用户输入本地的道路csv文件（同上）以及时间文件csv之后，将路径传给后端，后端返回json格式的道路黑点列表

from refs.utils import handle_streetFile, tellBP


# 接口1
# 输入：
#   file_2：道路csv文件路径
# 输出：
#   一个json格式的地图显示中心点。
#   格式例如：
#   {"center_lon": 118.82109195712025, "center_lat": 32.029136037816045}
def getCenter(file_2):
    h = handle_streetFile.handle_street(file_2)
    return h.getMapCenterJson()


# 接口2
# 输入：
#   file_1:时间文件csv
#   file_2:道路csv
# 输出：
#   json格式的道路黑点列表
#   格式例如：
#   [{"bp_num": 6.0, "bp_lon": 118.82001399999999, "bp_lat": 32.04607, "bp_r": 200.0},
#    {"bp_num": 11.0, "bp_lon": 118.81783, "bp_lat": 32.046192, "bp_r": 200.0},
#    {"bp_num": 10.0, "bp_lon": 118.80736599999999, "bp_lat": 32.046976, "bp_r": 200.0},
#    {"bp_num": 12.0, "bp_lon": 118.803227, "bp_lat": 32.047270000000005, "bp_r": 200.0}]
def getBP(file_1, file_2):
    bp = tellBP.tellBP(file_1, file_2)
    return bp.getBP_json()

