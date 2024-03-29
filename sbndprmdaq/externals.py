'''
Collection of functions to check the status of other SBND systems
'''

import datetime

import epics
import psycopg2
import numpy as np

def pmt_hv_pw_on():
    '''
    Returns False if ALL PMT channels are off
    '''
    #pylint: disable=line-too-long,invalid-name

    pvs = ['sbnd_pmt_hv_00_000/Pw', 'sbnd_pmt_hv_00_001/Pw', 'sbnd_pmt_hv_00_002/Pw', 'sbnd_pmt_hv_00_003/Pw', 'sbnd_pmt_hv_00_004/Pw', 'sbnd_pmt_hv_00_005/Pw', 'sbnd_pmt_hv_00_006/Pw', 'sbnd_pmt_hv_00_007/Pw', 'sbnd_pmt_hv_00_008/Pw', 'sbnd_pmt_hv_00_009/Pw', 'sbnd_pmt_hv_00_010/Pw', 'sbnd_pmt_hv_00_011/Pw', 'sbnd_pmt_hv_00_012/Pw', 'sbnd_pmt_hv_00_013/Pw', 'sbnd_pmt_hv_00_014/Pw', 'sbnd_pmt_hv_00_015/Pw', 'sbnd_pmt_hv_00_016/Pw', 'sbnd_pmt_hv_00_017/Pw', 'sbnd_pmt_hv_00_018/Pw', 'sbnd_pmt_hv_00_019/Pw', 'sbnd_pmt_hv_00_020/Pw', 'sbnd_pmt_hv_00_021/Pw', 'sbnd_pmt_hv_00_022/Pw', 'sbnd_pmt_hv_00_023/Pw', 'sbnd_pmt_hv_00_024/Pw', 'sbnd_pmt_hv_00_025/Pw', 'sbnd_pmt_hv_00_026/Pw', 'sbnd_pmt_hv_00_027/Pw', 'sbnd_pmt_hv_00_028/Pw', 'sbnd_pmt_hv_00_029/Pw', 'sbnd_pmt_hv_00_030/Pw', 'sbnd_pmt_hv_00_031/Pw', 'sbnd_pmt_hv_00_032/Pw', 'sbnd_pmt_hv_00_033/Pw', 'sbnd_pmt_hv_00_034/Pw', 'sbnd_pmt_hv_00_035/Pw', 'sbnd_pmt_hv_00_036/Pw', 'sbnd_pmt_hv_00_037/Pw', 'sbnd_pmt_hv_00_038/Pw', 'sbnd_pmt_hv_00_039/Pw', 'sbnd_pmt_hv_00_040/Pw', 'sbnd_pmt_hv_00_041/Pw', 'sbnd_pmt_hv_00_042/Pw', 'sbnd_pmt_hv_00_043/Pw', 'sbnd_pmt_hv_00_044/Pw', 'sbnd_pmt_hv_00_045/Pw', 'sbnd_pmt_hv_00_046/Pw', 'sbnd_pmt_hv_00_047/Pw', 'sbnd_pmt_hv_02_000/Pw', 'sbnd_pmt_hv_02_001/Pw', 'sbnd_pmt_hv_02_002/Pw', 'sbnd_pmt_hv_02_003/Pw', 'sbnd_pmt_hv_02_004/Pw', 'sbnd_pmt_hv_02_005/Pw', 'sbnd_pmt_hv_02_006/Pw', 'sbnd_pmt_hv_02_007/Pw', 'sbnd_pmt_hv_02_008/Pw', 'sbnd_pmt_hv_02_009/Pw', 'sbnd_pmt_hv_02_010/Pw', 'sbnd_pmt_hv_02_011/Pw', 'sbnd_pmt_hv_02_012/Pw', 'sbnd_pmt_hv_02_013/Pw', 'sbnd_pmt_hv_02_014/Pw', 'sbnd_pmt_hv_02_015/Pw', 'sbnd_pmt_hv_02_016/Pw', 'sbnd_pmt_hv_02_017/Pw', 'sbnd_pmt_hv_02_018/Pw', 'sbnd_pmt_hv_02_019/Pw', 'sbnd_pmt_hv_02_020/Pw', 'sbnd_pmt_hv_02_021/Pw', 'sbnd_pmt_hv_02_022/Pw', 'sbnd_pmt_hv_02_023/Pw', 'sbnd_pmt_hv_02_024/Pw', 'sbnd_pmt_hv_02_025/Pw', 'sbnd_pmt_hv_02_026/Pw', 'sbnd_pmt_hv_02_027/Pw', 'sbnd_pmt_hv_02_028/Pw', 'sbnd_pmt_hv_02_029/Pw', 'sbnd_pmt_hv_02_030/Pw', 'sbnd_pmt_hv_02_031/Pw', 'sbnd_pmt_hv_02_032/Pw', 'sbnd_pmt_hv_02_033/Pw', 'sbnd_pmt_hv_02_034/Pw', 'sbnd_pmt_hv_02_035/Pw', 'sbnd_pmt_hv_02_036/Pw', 'sbnd_pmt_hv_02_037/Pw', 'sbnd_pmt_hv_02_038/Pw', 'sbnd_pmt_hv_02_039/Pw', 'sbnd_pmt_hv_02_040/Pw', 'sbnd_pmt_hv_02_041/Pw', 'sbnd_pmt_hv_02_042/Pw', 'sbnd_pmt_hv_02_043/Pw', 'sbnd_pmt_hv_02_044/Pw', 'sbnd_pmt_hv_02_045/Pw', 'sbnd_pmt_hv_02_046/Pw', 'sbnd_pmt_hv_02_047/Pw', 'sbnd_pmt_hv_04_000/Pw', 'sbnd_pmt_hv_04_001/Pw', 'sbnd_pmt_hv_04_002/Pw', 'sbnd_pmt_hv_04_003/Pw', 'sbnd_pmt_hv_04_004/Pw', 'sbnd_pmt_hv_04_005/Pw', 'sbnd_pmt_hv_04_006/Pw', 'sbnd_pmt_hv_04_007/Pw', 'sbnd_pmt_hv_04_008/Pw', 'sbnd_pmt_hv_04_009/Pw', 'sbnd_pmt_hv_04_010/Pw', 'sbnd_pmt_hv_04_011/Pw', 'sbnd_pmt_hv_04_012/Pw', 'sbnd_pmt_hv_04_013/Pw', 'sbnd_pmt_hv_04_014/Pw', 'sbnd_pmt_hv_04_015/Pw', 'sbnd_pmt_hv_04_016/Pw', 'sbnd_pmt_hv_04_017/Pw', 'sbnd_pmt_hv_04_018/Pw', 'sbnd_pmt_hv_04_019/Pw', 'sbnd_pmt_hv_04_020/Pw', 'sbnd_pmt_hv_04_021/Pw', 'sbnd_pmt_hv_04_022/Pw', 'sbnd_pmt_hv_04_023/Pw', 'sbnd_pmt_hv_04_024/Pw', 'sbnd_pmt_hv_04_025/Pw', 'sbnd_pmt_hv_04_026/Pw', 'sbnd_pmt_hv_04_027/Pw', 'sbnd_pmt_hv_04_028/Pw', 'sbnd_pmt_hv_04_029/Pw', 'sbnd_pmt_hv_04_030/Pw', 'sbnd_pmt_hv_04_031/Pw', 'sbnd_pmt_hv_04_032/Pw', 'sbnd_pmt_hv_04_033/Pw', 'sbnd_pmt_hv_04_034/Pw', 'sbnd_pmt_hv_04_035/Pw', 'sbnd_pmt_hv_04_036/Pw', 'sbnd_pmt_hv_04_037/Pw', 'sbnd_pmt_hv_04_038/Pw', 'sbnd_pmt_hv_04_039/Pw', 'sbnd_pmt_hv_04_040/Pw', 'sbnd_pmt_hv_04_041/Pw', 'sbnd_pmt_hv_04_042/Pw', 'sbnd_pmt_hv_04_043/Pw', 'sbnd_pmt_hv_04_044/Pw', 'sbnd_pmt_hv_04_045/Pw', 'sbnd_pmt_hv_04_046/Pw', 'sbnd_pmt_hv_04_047/Pw']

    satuses = []
    for pv in pvs:
        satuses.append(epics.caget(pv))

    return any(satuses)


def pmt_hv_on():
    '''
    Returns False if ALL PMT HV are below 10 volts
    '''
    #pylint: disable=line-too-long,invalid-name

    pvs = ['sbnd_pmt_hv_00_000/VMon', 'sbnd_pmt_hv_00_001/VMon', 'sbnd_pmt_hv_00_002/VMon', 'sbnd_pmt_hv_00_003/VMon', 'sbnd_pmt_hv_00_004/VMon', 'sbnd_pmt_hv_00_005/VMon', 'sbnd_pmt_hv_00_006/VMon', 'sbnd_pmt_hv_00_007/VMon', 'sbnd_pmt_hv_00_008/VMon', 'sbnd_pmt_hv_00_009/VMon', 'sbnd_pmt_hv_00_010/VMon', 'sbnd_pmt_hv_00_011/VMon', 'sbnd_pmt_hv_00_012/VMon', 'sbnd_pmt_hv_00_013/VMon', 'sbnd_pmt_hv_00_014/VMon', 'sbnd_pmt_hv_00_015/VMon', 'sbnd_pmt_hv_00_016/VMon', 'sbnd_pmt_hv_00_017/VMon', 'sbnd_pmt_hv_00_018/VMon', 'sbnd_pmt_hv_00_019/VMon', 'sbnd_pmt_hv_00_020/VMon', 'sbnd_pmt_hv_00_021/VMon', 'sbnd_pmt_hv_00_022/VMon', 'sbnd_pmt_hv_00_023/VMon', 'sbnd_pmt_hv_00_024/VMon', 'sbnd_pmt_hv_00_025/VMon', 'sbnd_pmt_hv_00_026/VMon', 'sbnd_pmt_hv_00_027/VMon', 'sbnd_pmt_hv_00_028/VMon', 'sbnd_pmt_hv_00_029/VMon', 'sbnd_pmt_hv_00_030/VMon', 'sbnd_pmt_hv_00_031/VMon', 'sbnd_pmt_hv_00_032/VMon', 'sbnd_pmt_hv_00_033/VMon', 'sbnd_pmt_hv_00_034/VMon', 'sbnd_pmt_hv_00_035/VMon', 'sbnd_pmt_hv_00_036/VMon', 'sbnd_pmt_hv_00_037/VMon', 'sbnd_pmt_hv_00_038/VMon', 'sbnd_pmt_hv_00_039/VMon', 'sbnd_pmt_hv_00_040/VMon', 'sbnd_pmt_hv_00_041/VMon', 'sbnd_pmt_hv_00_042/VMon', 'sbnd_pmt_hv_00_043/VMon', 'sbnd_pmt_hv_00_044/VMon', 'sbnd_pmt_hv_00_045/VMon', 'sbnd_pmt_hv_00_046/VMon', 'sbnd_pmt_hv_00_047/VMon', 'sbnd_pmt_hv_02_000/VMon', 'sbnd_pmt_hv_02_001/VMon', 'sbnd_pmt_hv_02_002/VMon', 'sbnd_pmt_hv_02_003/VMon', 'sbnd_pmt_hv_02_004/VMon', 'sbnd_pmt_hv_02_005/VMon', 'sbnd_pmt_hv_02_006/VMon', 'sbnd_pmt_hv_02_007/VMon', 'sbnd_pmt_hv_02_008/VMon', 'sbnd_pmt_hv_02_009/VMon', 'sbnd_pmt_hv_02_010/VMon', 'sbnd_pmt_hv_02_011/VMon', 'sbnd_pmt_hv_02_012/VMon', 'sbnd_pmt_hv_02_013/VMon', 'sbnd_pmt_hv_02_014/VMon', 'sbnd_pmt_hv_02_015/VMon', 'sbnd_pmt_hv_02_016/VMon', 'sbnd_pmt_hv_02_017/VMon', 'sbnd_pmt_hv_02_018/VMon', 'sbnd_pmt_hv_02_019/VMon', 'sbnd_pmt_hv_02_020/VMon', 'sbnd_pmt_hv_02_021/VMon', 'sbnd_pmt_hv_02_022/VMon', 'sbnd_pmt_hv_02_023/VMon', 'sbnd_pmt_hv_02_024/VMon', 'sbnd_pmt_hv_02_025/VMon', 'sbnd_pmt_hv_02_026/VMon', 'sbnd_pmt_hv_02_027/VMon', 'sbnd_pmt_hv_02_028/VMon', 'sbnd_pmt_hv_02_029/VMon', 'sbnd_pmt_hv_02_030/VMon', 'sbnd_pmt_hv_02_031/VMon', 'sbnd_pmt_hv_02_032/VMon', 'sbnd_pmt_hv_02_033/VMon', 'sbnd_pmt_hv_02_034/VMon', 'sbnd_pmt_hv_02_035/VMon', 'sbnd_pmt_hv_02_036/VMon', 'sbnd_pmt_hv_02_037/VMon', 'sbnd_pmt_hv_02_038/VMon', 'sbnd_pmt_hv_02_039/VMon', 'sbnd_pmt_hv_02_040/VMon', 'sbnd_pmt_hv_02_041/VMon', 'sbnd_pmt_hv_02_042/VMon', 'sbnd_pmt_hv_02_043/VMon', 'sbnd_pmt_hv_02_044/VMon', 'sbnd_pmt_hv_02_045/VMon', 'sbnd_pmt_hv_02_046/VMon', 'sbnd_pmt_hv_02_047/VMon', 'sbnd_pmt_hv_04_000/VMon', 'sbnd_pmt_hv_04_001/VMon', 'sbnd_pmt_hv_04_002/VMon', 'sbnd_pmt_hv_04_003/VMon', 'sbnd_pmt_hv_04_004/VMon', 'sbnd_pmt_hv_04_005/VMon', 'sbnd_pmt_hv_04_006/VMon', 'sbnd_pmt_hv_04_007/VMon', 'sbnd_pmt_hv_04_008/VMon', 'sbnd_pmt_hv_04_009/VMon', 'sbnd_pmt_hv_04_010/VMon', 'sbnd_pmt_hv_04_011/VMon', 'sbnd_pmt_hv_04_012/VMon', 'sbnd_pmt_hv_04_013/VMon', 'sbnd_pmt_hv_04_014/VMon', 'sbnd_pmt_hv_04_015/VMon', 'sbnd_pmt_hv_04_016/VMon', 'sbnd_pmt_hv_04_017/VMon', 'sbnd_pmt_hv_04_018/VMon', 'sbnd_pmt_hv_04_019/VMon', 'sbnd_pmt_hv_04_020/VMon', 'sbnd_pmt_hv_04_021/VMon', 'sbnd_pmt_hv_04_022/VMon', 'sbnd_pmt_hv_04_023/VMon', 'sbnd_pmt_hv_04_024/VMon', 'sbnd_pmt_hv_04_025/VMon', 'sbnd_pmt_hv_04_026/VMon', 'sbnd_pmt_hv_04_027/VMon', 'sbnd_pmt_hv_04_028/VMon', 'sbnd_pmt_hv_04_029/VMon', 'sbnd_pmt_hv_04_030/VMon', 'sbnd_pmt_hv_04_031/VMon', 'sbnd_pmt_hv_04_032/VMon', 'sbnd_pmt_hv_04_033/VMon', 'sbnd_pmt_hv_04_034/VMon', 'sbnd_pmt_hv_04_035/VMon', 'sbnd_pmt_hv_04_036/VMon', 'sbnd_pmt_hv_04_037/VMon', 'sbnd_pmt_hv_04_038/VMon', 'sbnd_pmt_hv_04_039/VMon', 'sbnd_pmt_hv_04_040/VMon', 'sbnd_pmt_hv_04_041/VMon', 'sbnd_pmt_hv_04_042/VMon', 'sbnd_pmt_hv_04_043/VMon', 'sbnd_pmt_hv_04_044/VMon', 'sbnd_pmt_hv_04_045/VMon', 'sbnd_pmt_hv_04_046/VMon', 'sbnd_pmt_hv_04_047/VMon']

    voltages = []
    for pv in pvs:
        voltages.append(epics.caget(pv))

    voltages = np.array(voltages)

    # All should be below 10 volts
    return any(voltages > 10)



class IgnitionAPI:
    '''
    Allows access to the Ignition database
    '''

    #pylint: disable=invalid-name,consider-using-f-string,bare-except

    def __init__(self):

        self._connection = None

        self.connect()

    def connect(self):
        '''
        Establishes a connection to the Ignition database
        '''

        self._connection = psycopg2.connect(user="dcs_reader",
                                            password="qcd56RUc",
                                            host="ifdb09",
                                            port="5456",
                                            database="sbnd_online_prd")

    def get_values(self, pv='te-8101a', month='02', limit=1):
        '''
        Returns values for a certain PV

        Args:
            pv (string): parameter value
            month (string): the month to look into, 2 digits only, ex '02' for February
            limit (int): limit to the number of values to be returned

        Returns:
            list: a list of sets containind 3 entries (x, pv value, datetime)
        '''

        if self._connection is None:
            self.connect()

        if self._connection.status != psycopg2.extensions.STATUS_READY:
            self.connect()

        query = """SELECT d.tagid, COALESCE((d.intvalue::numeric)::text, (trunc(d.floatvalue::numeric,3))::text), d.t_stamp
FROM cryo_prd.sqlt_data_1_2024_{} d, cryo_prd.sqlth_te s
WHERE d.tagid=s.id
AND s.tagpath LIKE '%sbnd%'
AND s.tagpath LIKE '%{}%'
AND s.tagpath LIKE '%{}%'
ORDER BY d.t_stamp DESC 
LIMIT {}""".format(month, '', pv, limit)

        cursor = self._connection.cursor()

        cursor.execute(query)

        dbrows = cursor.fetchall()

        cursor.close()

        formatted = []
        for row in dbrows:
            try:
                time = datetime.datetime.fromtimestamp(row[2]/1000) # ms since epoch
                time = time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time = row[2]
            formatted.append((row[0], row[1], row[2], time))

        print(formatted)
        return formatted

    def prm_covered(self, prm_id):
        '''
        Returns True if the PrM is covered with LAr

        Args:
            prm_id (int): the PrM ID
        '''

        if self._connection is None:
            self.connect()

        if self._connection.status != psycopg2.extensions.STATUS_READY:
            self.connect()

        if prm_id == 1:
            pv = 'te-8106a'
        elif prm_id == 2:
            pv = 'te-8102a'
        elif prm_id == 3:
            pv = 'lt-7133a'
        else:
            print('PrM ID {prm_id} not supported.')
            return False

        current_time = datetime.datetime.now()
        this_month = current_time.month
        month_2digit = str(this_month).zfill(2)

        query = """SELECT d.tagid, COALESCE((d.intvalue::numeric)::text, (trunc(d.floatvalue::numeric,3))::text), d.t_stamp
FROM cryo_prd.sqlt_data_1_2024_{} d, cryo_prd.sqlth_te s
WHERE d.tagid=s.id
AND s.tagpath LIKE '%sbnd%'
AND s.tagpath LIKE '%{}%'
AND s.tagpath LIKE '%{}%'
ORDER BY d.t_stamp DESC 
LIMIT {}""".format(month_2digit, '', pv, 1)

        cursor = self._connection.cursor()

        cursor.execute(query)

        dbrows = cursor.fetchall()

        cursor.close()

        formatted = []
        for row in dbrows:
            try:
                time = datetime.datetime.fromtimestamp(row[2]/1000) # ms since epoch
                time = time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time = row[2]
            formatted.append((row[0], row[1], row[2], time))

        # print(formatted)

        if prm_id in [1, 2]:
            if float(formatted[0][1]) < 88:
                return True
        else:
            if float(formatted[0][1]) > 20:
                return True
        return False
