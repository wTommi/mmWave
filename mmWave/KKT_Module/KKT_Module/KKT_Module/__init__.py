import os
import re
import sys
import atexit
import shutil
import pathlib
from KKT_Module.ksoc_global import kgl
from KKT_Module.KKTModuleLogger import get_logger

logger = get_logger(__name__)

kkt_module_path = pathlib.Path(__file__).parent.parent
if not pathlib.Path(kkt_module_path).is_dir() or pathlib.Path(kkt_module_path).name != 'KKT_Module':
    main_path = os.getcwd()
    kkt_module_path = pathlib.Path(main_path).joinpath('.\KKT_Module')

# logger.info('KKT module path:{}'.format(kkt_module_path))
# sys.path.append(str(kkt_module_path))
# kgl.KKTModule = kkt_module_path

def addPath(r_path:str):
    path = os.path.normpath(os.path.join(kkt_module_path, r_path))
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    sys.path.append(str(path))
    logger.info("{0} path: {1}".format(r_path.split('\\')[-1],path))
    return path

kgl.KKTConfig = addPath('..\Config')
kgl.KKTTempParam = addPath('..\TempParam')
kgl.KKTImage = addPath('..\Image')
kgl.KKTSound = addPath('..\Sound')
kgl.KKTRecord = addPath('..\Record')

def clear():
    logger.info('Clear temp files.')
    for path in sys.path:
        if re.match(r'^_MEI\d+$', os.path.basename(path)):
            temp_dir = pathlib.Path(path).parent
            logger.info(f'temp dir : {temp_dir}')
            for file in pathlib.Path(temp_dir).iterdir():
                if re.match(r'^_MEI\d+$', os.path.basename(file)):
                    if str(file) == str(path):
                        continue
                    logger.info('Removing {}'.format(file))
                    shutil.rmtree(file)
            break
clear()
atexit.register(clear)
