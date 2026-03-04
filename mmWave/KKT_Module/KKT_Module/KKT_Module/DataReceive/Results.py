from KKT_Module.DataReceive.Data.DiagnosisDict import IDiagnosisDict
from KKT_Module.DataReceive.Data import ISiamese, ISoftMax, IFcLast
from KKT_Module.DataReceive.Data.FeatureMap import  IMap
from KKT_Module.DataReceive.Data import IGesture
from KKT_Module.DataReceive.Data import IMotion
from KKT_Module.DataReceive.Data import IRawData
from KKT_Module.DataReceive.Data.Tracking import ITracking
from KKT_Module.DataReceive.Data import IIMax, ICFAR
from KKT_Module.DataReceive.Data.ReferenceBank import IR_Bank

class Result168(IGesture, IMap, IRawData, ISiamese, ISoftMax, ITracking, ICFAR, IR_Bank, IIMax):...

class Result169(IGesture, IMap, IRawData, ISoftMax, ITracking, ICFAR, IR_Bank, IIMax, IDiagnosisDict, IMotion, IFcLast):...


if __name__ == '__main__':
    import time
    import numpy as np

    times = 100000
    r = Result168()
    t_data = [0,0,0]
    r_data = np.arange(8192)
    s = time.time_ns()
    for _ in range(times):
        r = Result168().new()
        r.tracking = t_data
        r.raw_data = r_data
    print(r)
    print(r.tracking.data)
    print(f'average :{(time.time_ns() - s) / times / (10 ** 6):.4f} ms')