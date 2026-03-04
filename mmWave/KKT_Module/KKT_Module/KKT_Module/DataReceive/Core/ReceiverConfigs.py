from KKT_Module.Configs import INIConfigs
class ReceiverConfigs(INIConfigs):
    def __init__(self, filename):
        super(ReceiverConfigs, self).__init__(filename=filename)
        self.setINIConfigs()

    def setINIConfigs(self):
        for section in self.section:
            self.__setattr__(section, dict(self.config[section].items()))

    def getConfig(self, section):
        if not hasattr(self, section):
            return {}
        return self.__getattribute__(section)