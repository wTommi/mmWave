from KKT_Module.DataReceive.Core import Receiver
from KKT_Module.GuiUpdater.GuiUpdater import Updater
from KKT_Module.FiniteReceiverMachine import FRM, log
from typing import Any, Dict


if __name__ == '__main__':
    import sys

    class TestUpdater(Updater):
        def update(self, res) -> None:
            if res is None:
                return
            log.info(f'Receive results from FSM : {res}')

        def setConfigs(self, **kwargs) -> None:
            for k, v in kwargs.items():
                if not hasattr(self, k):
                    log.info('Attribute "{}" not in Updater.'.format(k))
                    continue
                self.__setattr__(k, v)
                log.info('Attribute "{}", set "{}"'.format(k, v))

    class TestReceiver(Receiver):
        res = None
        chirps = 16
        def getResults(self) -> Any:
            res = self.res
            self.res = None
            return res

        def setConfigs(self, **kwargs) -> None:
            for k, v in kwargs.items():
                if not hasattr(self, k):
                    log.info('Attribute "{}" not in receiver.'.format(k))
                    continue
                self.__setattr__(k, v)
                log.info('Attribute "{}", set "{}"'.format(k, v))

        def trigger(self, **kwargs) -> None:
            self.setConfigs(**kwargs)
            log.info('trigger Receiver')


        def stop(self) -> None:
            log.info('stop Receiver')

    def main(r:Receiver, u:Updater):
        try:
            FRM.setFRM(r, u)
            FRM.trigger(chirps=32)
            while True:
                query = input('input query :')
                if query.upper() == 'PAUSE':
                    FRM.pause()
                elif query.upper() == 'RESTART':
                    FRM.start()
                elif query.upper() == 'START':
                    FRM.start()
                elif query.upper() == 'STOP':
                    FRM.stop()
                elif query.upper() == 'Q':
                    break
                else:
                    r.res = query
            sys.exit(FRM.stop())
        except Exception as e:
            log.warning(f'{e}')


    main(r=TestReceiver(), u=TestUpdater())