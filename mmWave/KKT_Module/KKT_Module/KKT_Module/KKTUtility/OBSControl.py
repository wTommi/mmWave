import os.path
import sys
sys.path.append('../../')
import time
from obswebsocket import obsws, requests
from KKT_Module.KKTModuleLogger import main_logger as log


class OBSControl:
    def __init__(self):
        self._ws = None
        self.connected = False

    def connectOBSWebSocket(self, host = "localhost", port = 4444, password = "secret"):
        self._ws = obsws(host, port, password)
        self._ws.connect()
        self.connected = True
        log.info('OBS web socket connected')

        scenes = self._ws.call(requests.GetSceneList())
        log.info('Scenes:')
        for s in scenes.getScenes():
            name = s['name']
            log.info('\t'+name)

        sources = self._ws.call(requests.GetSourcesList()).getSources()
        log.info('Source:')
        for s in sources:
            source = s['name']
            log.info('\t'+ source)
            self._ws.call(requests.SetMute(source, True))

        self.connected = True

    def setRecordPath(self, dir , file_name):
        self._ws.call(requests.SetFilenameFormatting(str(file_name)))
        self._ws.call(requests.SetRecordingFolder(str(dir)))
        time.sleep(1)


    def startRecording(self):
        if self.connected:
            self._ws.call(requests.StartRecording())
            log.info("Start Video Recording")

    def stopRecording(self):
        path = None
        if self.connected:
            self._ws.call(requests.StopRecording())
            log.info("Stop Video Recording")
            outputs = self._ws.call(requests.ListOutputs()).getOutputs()
            for output in outputs:
                if output['name'] == 'simple_file_output':
                    path = output['settings']['path']
                    log.debug('Record path : {}'.format(path))
                    break
        return path

    def pauseRecording(self):
        self._ws.call(requests.PauseRecording())
        log.info("Pause Recording")

    def resumeRecording(self):
        self._ws.call(requests.ResumeRecording())
        log.info("Resume Recording")

    def disconnectOBSWebSocket(self):
        if not self.connected:
            return
        self._ws.disconnect()
        self.connected = False
        log.info('OBS websocket disconnect')



def main():
    try:
        ws = OBSControl()

        ws.connectOBSWebSocket()

        ws.setRecordPath(r'C:\Users\eric.li\Desktop\Python\py_study\OBS_control\Record', 'test')

        ws.startRecording()

        time.sleep(5)

        ws.stopRecording()

        ws.disconnectOBSWebSocket()

        del ws

    except KeyboardInterrupt:
        pass



if __name__ == '__main__':
   main()
