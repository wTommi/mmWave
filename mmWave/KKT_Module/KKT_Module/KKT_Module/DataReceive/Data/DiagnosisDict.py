from typing import Optional
from KKT_Module.DataReceive.Core import Results, Data
import numpy as np


class DiagnosisDict(Data):
    def __init__(self, data):
        super(DiagnosisDict, self).__init__(data)

    @staticmethod
    def convertDiagnosisDictData(diagnosis_dict, diagnosis, interrupt_list):
        for i in range(len(diagnosis)):
            if interrupt_list[i] == 'SF_SOFTMAX':
                # combine 4 byte to float32, <f：little endian; >f：big endian
                assert len(bytearray(diagnosis[i])) % 4 == 0, 'The length of SF_SOFTMAX is wrong !'
                d = np.frombuffer(bytearray(diagnosis[i]), dtype='float32')
            elif interrupt_list[i] == 'TRACKING':
                # combine 2 byte to int16
                assert len(bytearray(diagnosis[i])) % 2 == 0, 'The length of TRACKING is wrong !'
                d = np.frombuffer(bytearray(diagnosis[i]), dtype='int16')
            else:
                d = np.asarray(bytearray(diagnosis[i]), dtype='int8')

            diagnosis_dict.setdefault(interrupt_list[i], Data(d))

        return diagnosis_dict


class IDiagnosisDict(Results):
    @property
    def diagnosis_dict(self) -> Optional[DiagnosisDict]:
        return self['diagnosis_dict']

    @diagnosis_dict.setter
    def diagnosis_dict(self, data):
        if isinstance(data, DiagnosisDict):
            self['diagnosis_dict'] = data
        else:
            self['diagnosis_dict'] = DiagnosisDict(data)
