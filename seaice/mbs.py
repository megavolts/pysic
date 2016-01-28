#! /usr/bin/python3.5
# -*- coding: UTF-8 -*-

"""
Created on Fri Aug 29 08:47:19 2014
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2014/11/25"
"""

import numpy as np
import datetime

import seaice.icdtools

# ----------------------------------------------------------------------------------------------------------------------#
def read(MBS_path, lcomment='n'):
    """
		Calculate the volume fraction of brine in function of the temperature and salinity

		Parameters
		----------
		MBS_path : string
			File path, included filename, to the file containing the data to import

		Returns
		----------
		vf_b: ndarray
			array containing the mbs data in the following column
			1 to 5  year month day hour minute
			6       ice thickness
			7       mean snow thickness (mean of sensor 1 to sensor 3)
			8       snow thickness (sensor 1)
			9       snow thickness (sensor 2)
			10      snow thickness (sensor 3)
			11      water depth
			12      water temperature
			13      air temperature
			14      HR
			15...21 air thermistor
			22      ice surface thermistor
			23...end ice and water thermistor

	"""

    import csv
    import datetime as dt

    MBSyear = int(MBS_path.split('/')[-1][3:5])
    ## CSV with dialect
    fopen = open(MBS_path, 'rU')

    # CSV dialect
    csv.register_dialect('MBS06', delimiter='\t', doublequote=False, quotechar='', lineterminator='\r\n', escapechar='',
                         quoting=csv.QUOTE_NONE)
    csv.register_dialect('MBS09', delimiter='\t', doublequote=True, quotechar='', lineterminator='\r\n', escapechar='',
                         quoting=csv.QUOTE_NONE)
    csv.register_dialect('MBS13', delimiter=',', doublequote=False, quotechar='', lineterminator='\n', escapechar='',
                         quoting=csv.QUOTE_NONE)

    if 13 <= MBSyear:
        source = csv.reader(fopen)
        nheader = 1
        col_date = 6 - 1  # YYYY-MM-DD HH:MM:SS
        col_Hi = 48 - 1
        col_Hs = np.nan
        col_Hs1 = 49 - 1
        col_Hs2 = 50 - 1
        col_Hs3 = 51 - 1
        col_Hw = 52 - 1
        col_Tw = 38 - 1
        col_Tair = 53 - 1
        col_HR = 2 - 1
        col_Tice_00 = 8 - 1
        n_th_air = 7
        n_th = 30
        tz = 'UTC'
    elif 10 <= MBSyear < 13:  # for 2012, 2011, 2010
        source = csv.reader(fopen, 'MBS09')
        nheader = 0
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Hs = np.nan
        col_Hs1 = 10 - 1
        col_Hs2 = 11 - 1
        col_Hs3 = 12 - 1
        col_Hi = 13 - 1
        col_Hw = 14 - 1
        col_Tw = 7 - 1
        col_Tair = 9 - 1
        col_HR = 8 - 1
        col_Tice_00 = 17 - 1
        n_th_air = 7
        n_th = 29
        if MBSyear == 12:
            tz = 'AKST'
        else:
            tz = 'UTC'
    elif 8 <= MBSyear < 10:  # for 2009, 2008
        source = csv.reader(fopen, 'MBS09')
        nheader = 0
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Hs = np.nan
        col_Hs1 = 10 - 1
        col_Hs2 = 11 - 1
        col_Hs3 = 12 - 1
        col_Hi = 13 - 1
        col_Hw = 14 - 1
        col_Tw = 7 - 1
        col_Tair = 9 - 1
        col_HR = 8 - 1
        col_Tice_00 = 16 - 1
        n_th_air = 4
        n_th = 29
        if MBSyear == 8:
            tz = 'UTC'
        elif MBSyear == 9:
            tz = 'AKST'
    elif 6 <= MBSyear < 8:  # for 2007
        source = csv.reader(fopen, 'MBS06')
        nheader = 0
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Hs = 10 - 1
        col_Hs1 = np.nan
        col_Hs2 = np.nan
        col_Hs3 = np.nan
        col_Hi = 11 - 1
        col_Hw = 12 - 1
        col_Tw = 7 - 1
        col_Tair = 9 - 1
        col_HR = 8 - 1
        col_Tice_00 = 14 - 1
        if MBSyear == 7:
            n_th_air = 0
            n_th = 19
        elif MBSyear == 6:
            n_th_air = 4
            n_th = 29
        tz = 'UTC'
    else:
        if lcomment == 'y':
            print('out of range')

    data = []
    # skip header
    for iiHeader in range(0, nheader):
        next(source)

    rownum = 0
    for row in source:
        data.append([])
        for col in row:
            if col == '-9999' or col == '-9999.0' or col == '-9999.000' or col == 'NAN' or col == 'nan' or col == '':
                col = np.nan
            data[rownum].append(col)
        rownum += 1

    dataout = []

    # parse data
    if tz == 'UTC':
        dtzone = +9 * 3600
    else:
        dtzone = 0

    for ii in range(0, len(data)):
        dataout.append([])
        # date and time
        if 12 < MBSyear:
            d = dt.datetime.strptime(data[ii][col_date], "%Y-%m-%d %H:%M:%S") + dt.timedelta(0, dtzone)
            dataout[ii].append(int(d.strftime("%Y")))  # 1
            dataout[ii].append(int(d.strftime("%m")))  # 2
            dataout[ii].append(int(d.strftime("%d")))  # 3
            dataout[ii].append(int(d.strftime("%H")))  # 4
            dataout[ii].append(int(d.strftime("%M")))  # 5
        elif 5 < MBSyear <= 12:
            d = dt.datetime(int(float(data[ii][col_date])), 1, 1) + dt.timedelta(
                float(data[ii][col_date - 1]) - 1) + dt.timedelta(0, dtzone)
            dataout[ii].append(int(d.strftime("%Y")))  # 1
            dataout[ii].append(int(d.strftime("%m")))  # 2
            dataout[ii].append(int(d.strftime("%d")))  # 3
            dataout[ii].append(int(d.strftime("%H")))  # 4
            dataout[ii].append(int(d.strftime("%M")))  # 5

        # ice
        dataout[ii].append(float(data[ii][col_Hi]))  # 6

        # snow
        if 6 <= MBSyear < 8:
            dataout[ii].append(float(data[ii][col_Hs]))  # 7
            dataout[ii].append(np.nan)  # 8
            dataout[ii].append(np.nan)  # 9
            dataout[ii].append(np.nan)  # 10
        else:
            dataout[ii].append(
                np.nanmean([float(data[ii][col_Hs1]), float(data[ii][col_Hs2]), float(data[ii][col_Hs3])]))  # 7
            dataout[ii].append(float(data[ii][col_Hs1]))  # 8
            dataout[ii].append(float(data[ii][col_Hs2]))  # 9
            dataout[ii].append(float(data[ii][col_Hs3]))  # 10

        # water depth
        dataout[ii].append(float(data[ii][col_Hw]))  # 11
        dataout[ii].append(float(data[ii][col_Tw]))  # 12
        dataout[ii].append(float(data[ii][col_Tair]))  # 13
        dataout[ii].append(float(data[ii][col_HR]))  # 14

        # thermistor
        for iiT in range(0, 7 - n_th_air):
            dataout[ii].append(np.nan)
        for iiT in range(col_Tice_00, col_Tice_00 + n_th):
            dataout[ii].append(float(data[ii][iiT]))
    return np.array(dataout)

def ice_profile(mbs_data_yr, t_mbs_index, ice_thickness, section_thickness=0.05, lcomment='n'):
    import math

    mbs_ice_surface = {}
    mbs_ice_surface[2006] = 8
    mbs_ice_surface[2007] = 8
    mbs_ice_surface[2008] = 8
    mbs_ice_surface[2009] = 8
    mbs_ice_surface[2010] = 8
    mbs_ice_surface[2011] = 8
    mbs_ice_surface[2012] = 8
    mbs_ice_surface[2013] = 8
    mbs_ice_surface[2014] = 8

    year = mbs_data_yr[t_mbs_index[0]][0]
    Tmbs_avg = np.nanmean(mbs_data_yr[t_mbs_index], axis=0)
    Tmbs_avg = Tmbs_avg[15 + mbs_ice_surface[int(year)] - 1:]

    hI = np.nanmax(mbs_data_yr[t_mbs_index, 5])
    # TODO: detect automatically the bottom of the ice if their is no ice thickness data
    if math.isnan(hI):
        hI = ice_thickness
    xTmbs = np.arange(0, hI, 0.1)

    if xTmbs[-1] < hI:
        ThI = np.interp(hI, np.append(xTmbs, xTmbs[-1] + 0.1), Tmbs_avg[0:len(xTmbs)+1])
        Tavg = np.append(Tmbs_avg[0:len(xTmbs)], ThI)
        xTmbs = np.append(xTmbs, hI)
    else:
        Tavg = Tmbs_avg[0:len(xTmbs)]

    # scaling to ice core length
    xTmbs_scaled = xTmbs*(ice_thickness / hI)
    y_mbs = np.arange(section_thickness/2, ice_thickness, section_thickness)
    if (ice_thickness+len(y_mbs)*section_thickness)/2 < ice_thickness:
        y_mbs = np.append(y_mbs, (ice_thickness+len(y_mbs)*section_thickness)/2)
    Tmbs_avg = np.interp(y_mbs, xTmbs_scaled[~np.isnan(Tavg)], Tavg[~np.isnan(Tavg)])

    return y_mbs, Tmbs_avg

def daily_max(mbs_data, year, ii_col):
    day_start = datetime.datetime(year, int(mbs_data[year][0, 1]), int(mbs_data[year][0, 2]))
    day_end = datetime.datetime(year, int(mbs_data[year][-1, 1]), int(mbs_data[year][-1, 2]))
    ii_day = day_start
    ii_col = 6
    hi_day = []
    while ii_day <= day_end:
        day_index = seaice.icdtools.index_from_day(mbs_data[year], ii_day)
        try:
            hi_mean = np.nanmean(mbs_data[year][day_index, ii_col-1])
        except IndexError:
            hi_mean = np.nan
        else:
            hi_day.append(hi_mean)
        ii_day += datetime.timedelta(1)
    hi_max = np.nanmax(hi_day)
    np.where(np.array(hi_day) == hi_max)
    hi_max_index = np.where(np.array(hi_day) == hi_max)[0]
    hi_max_index
    if len(np.atleast_1d(hi_max_index)) > 1:
        hi_max_index = hi_max_index[-1]
    hi_max_day = day_start + datetime.timedelta(np.float(hi_max_index))
    return hi_max_day, hi_max


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]