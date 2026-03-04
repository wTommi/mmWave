from typing import Optional
from KKT_Module.DataReceive.Core import Results, Data



class Motion(Data):
    def __init__(self, data):
        super(Motion, self).__init__(data)

class IMotion(Results):
    @property
    def motion(self) -> Optional[Motion]:
        return self['motion']

    @motion.setter
    def motion(self, data):
        if isinstance(data, Motion):
            self['motion'] = data
        else:
            self['motion'] = Motion(data)
