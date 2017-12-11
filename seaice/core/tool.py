# ! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.coreset.py : Core and CoreStack class

"""
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__name__ = "load"
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "core.py contained classes to handle ice core data"
__CoreVersion__ = 1.1

__all__ = ["discretize_profile", "set_vertical_reference"]

module_logger = logging.getLogger(__name__)
TOL = 1e-6


def discretize_profile(profile, y_bins=None, y_mid=None, variables=None, display_figure=False, fill_gap=True):
    """
    :param profile:
    :param y_bins:
    :param y_mid:
    :param variables:
    :param display_figure:
    :param fill_gap:
    :return:
    """

    if profile.empty:
        return profile

    v_ref = profile.v_ref.unique()[0]

    # VARIABLES CHECK
    if y_bins is None and y_mid is None:
        y_bins = pd.Series(profile.y_low.dropna().tolist() + profile.y_sup.dropna().tolist()).sort_values().unique()
        y_mid = profile.y_mid.dropna().sort_values().unique()
    elif y_bins is None:
        if y_mid is not None:
            y_mid = y_mid.sort_values().values
            dy = np.diff(y_mid) / 2
            y_bins = np.concatenate([[y_mid[0] - dy[0]], y_mid[:-1] + dy, [y_mid[-1] + dy[-1]]])
            if y_bins[0] < 0:
                y_bins[0] = 0
    elif y_mid is None:
        if y_bins is not None:
            y_mid = np.diff(y_bins) / 2 + y_bins[:-1]
        else:
            y_mid = profile.y_mid.dropna().sort_values().unique()

    # check integrity of y_bins and y_mid:
    if min(y_mid) - min(y_bins) < TOL:
        y_bin_min = min(y_mid)-(min(y_bins)-min(y_mid))/2
        if y_bin_min >= 0:
            y_bins = np.concatenate(([y_bin_min], y_bins))
        else:
            y_bins = np.concatenate(([min(profile.y_mid)], y_bins))
    if max(profile.y_mid) - max(y_bins) <= TOL:
        y_bins = np.concatenate(([max(y_mid)+(max(y_bins)-max(y_mid))/2], y_bins))

    y_bins = np.array(y_bins)
    y_mid = np.array(y_mid)

    if variables is None:
        variables = [variable for variable in profile.variable.unique().tolist() if variable in profile.keys()]

    if not isinstance(variables, list):
        variables = [variables]

    discretized_profile = pd.DataFrame()

    module_logger.debug("Processing %s" % profile.name.unique()[0])
    # print("Processing %s" %profile.name.unique()[0])

    for variable in variables:
        #        profile[variable] = pd.to_numeric(profile[variable])
        temp = pd.DataFrame()

        if profile[profile.variable == variable].empty:
            module_logger.debug("no %s data" % (variable))
        else:
            module_logger.debug("%s data discretized" % variable)
            # print("\t%s data discretized" % (variable))
        # continuous profile (temperature-like)
        if (profile[profile.variable == variable].y_low.isnull().all() and
                    profile[profile.variable == variable].y_low.__len__() > 0):
            yx = profile[profile.variable == variable].set_index('y_mid').sort_index()[[variable]]
            yx = yx.dropna(how='all')  # drop row with all NA value

            y2x = yx.reindex(y_mid)
            for index in yx.index:
                y2x.loc[abs(y2x.index - index) < 1e-6, variable] = yx.loc[yx.index == index, variable].values
            # if np.isnan(y2x[variable].astype(float)).all():
            dat_temp = np.interp(y2x.index, yx.index, yx[variable].astype(float), left=np.nan, right=np.nan)
            y2x = pd.DataFrame(dat_temp, index=y2x.index, columns=[variable])
            # else:
            #    y2x.ix[(y2x.index <= max(yx.index)) & (min(yx.index) <= y2x.index)] = y2x.interpolate(method='index')[(y2x.index <= max(yx.index)) & (min(yx.index) <= y2x.index)]
            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(y_mid.__len__()))
            temp.update(y2x.reset_index())

            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop['variable'] = variable
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure:
                plt.figure()
                yx = yx.reset_index()
                plt.plot(yx[variable], yx['y_mid'], 'k')
                plt.plot(temp[variable], temp['y_mid'], 'xr')
                plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

        # step profile (salinity-like)
        elif (not profile[profile.variable == variable].y_low.isnull().all() and
                      profile[profile.variable == variable].y_low.__len__() > 0):
            if v_ref == 'bottom':
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_sup', 'y_low', variable])
                if yx[0, 0] > yx[0, 1]:
                    yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                        ['y_low', 'y_sup', variable])
            else:
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_low', 'y_sup', variable])
            x_step = []
            y_step = []
            ii_bin = 0
            if yx[0, 0] < y_bins[0]:
                ii_yx = np.where(yx[:, 0] - y_bins[0] <= TOL)[0][-1]
            else:
                ii_bin = np.where(y_bins - yx[0, 0] <= TOL)[0][-1]
                ii_yx = 0
                ii = 0
                while ii < ii_bin:
                    y_step.append(y_bins[ii])
                    y_step.append(y_bins[ii + 1])
                    x_step.append(np.nan)
                    x_step.append(np.nan)
                    ii += 1

            while ii_bin < y_bins.__len__() - 1:
                while ii_bin + 1 < y_bins.__len__() and y_bins[ii_bin + 1] - yx[ii_yx, 1] <= TOL:
                    S = s_nan(yx, ii_yx, fill_gap)
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                    x_step.append(S)
                    x_step.append(S)
                    ii_bin += 1
                    # plt.step(x_step, y_step, 'ro')
                    # if ii_bin == y_bins.__len__() - 1:
                    #    break

                if not yx[-1, 1] - y_bins[ii_bin] <= TOL:
                    L = 0
                    S = 0
                    if ii_yx < yx[:, 0].__len__() - 1:
                        while ii_yx < yx[:, 0].__len__() - 1 and yx[ii_yx, 1] - y_bins[ii_bin + 1] <= TOL:
                            L += (yx[ii_yx, 1] - y_bins[ii_bin])
                            S += (yx[ii_yx, 1] - y_bins[ii_bin]) * s_nan(yx, ii_yx, fill_gap)
                            ii_yx += 1

                            # ABOVE
                            # while ii_yx < len(yx[:, 1]) - 1 and yx[ii_yx + 1, 1] - y_bins[ii_bin + 1] <= TOL:
                            #    L += (yx[ii_yx + 1, 1] - yx[ii_yx + 1, 0])
                            #    S += (yx[ii_yx + 1, 1] - yx[ii_yx + 1, 0]) * s_nan(yx, ii_yx + 1, fill_gap)
                            #    ii_yx += 1
                            #    if ii_yx == yx[:, 1].__len__() - 1:
                            #        break
                            #   break
                        if yx[ii_yx, 0] - y_bins[ii_bin + 1] <= TOL:
                            S += (y_bins[ii_bin + 1] - yx[ii_yx, 0]) * s_nan(yx, ii_yx, fill_gap)
                            L += y_bins[ii_bin + 1] - yx[ii_yx, 0]
                        if L > TOL:
                            S = S / L
                        else:
                            S = np.nan

                    else:
                        S = yx[-1, -1]
                        # y_step.append(y_bins[ii_bin])
                        # y_step.append(y_bins[ii_bin + 1])
                        # x_step.append(S)
                        # x_step.append(S)
                        # ii_bin += 1
                    # ABOVE
                    # if yx[ii_yx, 1] - y_bins[ii_bin + 1] <= TOL and ii_yx + 1 < yx.__len__():
                    #     if np.isnan(s_nan(yx, ii_yx + 1, fill_gap)) and not np.isnan(S) and y_bins[ii_bin + 1] - yx[ii_yx+1, 1] < TOL:
                    #         S += S/L*(y_bins[ii_bin + 1] - yx[ii_yx + 1, 0])
                    #     else:
                    #         S += (y_bins[ii_bin + 1] - yx[ii_yx + 1, 0]) * s_nan(yx, ii_yx + 1, fill_gap)
                    #     L += (y_bins[ii_bin + 1] - yx[ii_yx + 1, 0])

                    # if S != 0 : #and y_bins[ii_bin] - yx[ii_yx, 1] < TOL:
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                    x_step.append(S)
                    x_step.append(S)
                    ii_bin += 1
                    # plt.step(x_step, y_step, 'ro')

                else:
                    while ii_bin + 1 < y_bins.__len__():
                        y_step.append(y_bins[ii_bin])
                        y_step.append(y_bins[ii_bin + 1])
                        x_step.append(np.nan)
                        x_step.append(np.nan)
                        ii_bin += 1

            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(np.unique(y_step).__len__() - 1))
            temp.update(pd.DataFrame(np.vstack(
                (np.unique(y_step)[:-1], np.unique(y_step)[:-1] + np.diff(np.unique(y_step)) / 2, np.unique(y_step)[1:],
                 [x_step[2 * ii] for ii in
                  range(int(x_step.__len__() / 2))])).transpose(),
                                     columns=['y_low', 'y_mid', 'y_sup', variable],
                                     index=temp.index[0:np.unique(y_step).__len__() - 1]))

            # properties
            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop['variable'] = variable
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure:
                plt.figure()
                x = []
                y = []
                for ii in range(yx[:, 0].__len__()):
                    y.append(yx[ii, 0])
                    y.append(yx[ii, 1])
                    x.append(yx[ii, 2])
                    x.append(yx[ii, 2])
                plt.step(x, y, 'bx')
                plt.step(x_step, y_step, 'ro')
                plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

                # profile = profile[(profile.name != profile.name.unique().tolist()[0]) | (profile.variable != variable)]
        discretized_profile = discretized_profile.append(temp)

    return discretized_profile


def set_vertical_reference(profile, h_ref=0, new_v_ref=None):
    """

    :param profile:
    :param h_ref:
    :param new_v_ref: default, same as profile origin
    :return:
    """

    if new_v_ref is None:
        if profile.v_ref.unique().__len__() > 1:
            module_logger.error("vertical reference for profile are not consistent")
            return CoreStack()
        else:
            new_v_ref = profile.v_ref.unique()[0]

    # look for ice thickness:
    if not np.isnan(profile.ice_thickness.astype(float)).all():
        hi = profile.ice_thickness.astype(float).dropna().unique()
    elif not np.isnan(profile.length.astype(float)).all():
        hi = profile.length.astype(float).dropna().unique()
    else:
        module_logger.warning("ice core length and ice thickness not available for the profile")
        return CoreStack()

    if not new_v_ref == profile.v_ref.unique()[0]:
        profile['y_low'] = hi - profile['y_low']
        profile['y_mid'] = hi - profile['y_mid']
        profile['y_sup'] = hi - profile['y_sup']

    if not h_ref == 0:
        profile['y_low'] = profile['y_low'] - h_ref
        profile['y_mid'] = profile['y_mid'] - h_ref
        profile['y_sup'] = profile['y_sup'] - h_ref


# Helper function
def s_nan(yx, ii_yx, fill_gap=True):
    """
    :param yx:
    :param ii_yx:
    :param fill_gap:
    :return:
    """
    if np.isnan(yx[ii_yx, 2]) and fill_gap:
        ii_yx_l = ii_yx - 1
        while ii_yx_l > 0 and np.isnan(yx[ii_yx_l, 2]):
            ii_yx_l -= 1
        s_l = yx[ii_yx_l, 2]

        ii_yx_s = ii_yx
        while ii_yx_s < yx.shape[0] - 1 and np.isnan(yx[ii_yx_s, 2]):
            ii_yx_s += 1
        s_s = yx[ii_yx_s, 2]

        s = (s_s + s_l) / 2
    else:
        s = yx[ii_yx, 2]
    return s

