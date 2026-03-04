import numpy as np
from h5py import File, Dataset, Group
from KKT_Module.KKTUtility.H5Tool.Core import H5Group, H5DataSet
from KKT_Module.KKTUtility.H5Tool.Core.EncryptTool import EncryptTool
from pathlib import Path
from io import BytesIO


class Encryptor:
    @staticmethod
    def openH5(file_path) -> File:
        if Path(file_path).suffix.lower() == '.kkt':
            print('file is kkt')
            # print('Decompressing...')
            with open(file_path, 'rb') as F:
                Ouput_IOFile = BytesIO(F.read())
            private_key = EncryptTool.Get_private_Key()
            Decrypted_file, decrpyted_string = EncryptTool.Decode_BytesIOObject(Ouput_IOFile, private_key)
            return File(Decrypted_file, 'r+')

        elif Path(file_path).suffix.lower() == '.h5':
            print('file is h5')
            return File(file_path, 'r+')

    @staticmethod
    def encryptToKKT(file_path, enable_compress=False):
        output_path = Path(file_path).with_suffix('.kkt')
        with open(file_path, 'rb') as F:
            BytesIOObject = BytesIO(F.read())
        if enable_compress:
            BytesIOObject = EncryptTool.compressBytesIOObject(BytesIOObject)
        public_key = EncryptTool.Get_public_Key()
        Ouput_IOFile, encrypted_b64 = EncryptTool.Encode_BytesIOObject(BytesIOObject, public_key)
        with open(output_path, 'wb') as F:
            F.write(Ouput_IOFile.getvalue())


class H5Editor():
    def __init__(self):
        self._file:File = None
        self._H5_group:H5Group = None
        pass

    @property
    def H5(self):
        return self._file

    def closeH5(self):
        if self._file is not None:
            self._file.flush()
            self._file.close()

    def openH5File(self, file_path):
        self._file = Encryptor.openH5(file_path)
        self._H5_group = H5Group(h5_file=self._file)
        self._createH5Object(self._file, self._H5_group)
        return self._file

    def _createH5Object(self, file_group:Group, group:H5Group):
        for k,v in file_group.items():
            if isinstance(v, Group):
                subgroup = H5Group(name=k, h5_file=self._file)
                group.addSubGroup(subgroup)
                self._createH5Object(file_group[k], subgroup)
            elif isinstance(v, Dataset):
                subdataset = H5DataSet(name=k, h5_file=self._file, dtype=v.dtype)
                group.addDataSet(subdataset)
        return

    def showH5Attributes(self):
        assert self._H5_group is not None, 'Root H5 group should not be None type object.'
        return self._H5_group.showH5Attributes()

    def getDict(self)->dict:
        return self._H5_group.getH5Dict(n=0)

    def getH5Attribute(self, attribute_name:str, group_name:str=None, group:H5Group=None):
        if group is None:
            group = self._H5_group
            assert group is not None,'Root H5 group should not be None type object.'

        if group_name is None:
            config = group.getH5Attribute(attribute_name)
            if config:
                return config

        if attribute_name is None:
            config = group.sub_groups[group_name].getH5Attributes()
            return config


        if group_name in group.sub_groups.keys():
            config = group.sub_groups[group_name].getH5Attribute(attribute_name)
            if config:
                return config

        for g in group.sub_groups.values():
            config = self.getH5Attribute(attribute_name=attribute_name,
                                         group_name=group_name,
                                         group=g)
            if config:
                return config

        if group_name :
            config = group.getH5Attribute(attribute_name)
            if config:
                return config
        return None

    def getH5Dataset(self, dataset_name:str, group:H5Group=None, output_object:bool=False):
        if group is None:
            group = self._H5_group
            assert group is not None, 'Root H5 group should not be None type object.'

        if dataset_name in group.sub_datasets.keys():
            if output_object:
                return group.sub_datasets.get(dataset_name).getDataSetObject()
            return group.sub_datasets.get(dataset_name).getDataSet()

        for g in group.sub_groups.values():
            data =  self.getH5Dataset(dataset_name=dataset_name,
                                     group = g)
            if data is not None:
                return data
        return None

    def setAttribute(self, attribute_name:str, config, group_name:str=None, group:H5Group=None):
        if group is None:
            group = self._H5_group
            assert group is not None,'Root H5 group should not be None type object.'

        if group_name is None:
            group.setH5Attribute(attribute_name, config)
            return

        if group_name[0] == '/':
            group_name = group_name[1:]
        group_name_list = group_name.split('/')
        group_name = group_name_list.pop(0)
        if (group_name == '') and (len(group_name_list)==0):
            group.setH5Attribute(attribute_name, config)
            return

        if group_name  in group.sub_groups.keys():
            sub_group = group.sub_groups[group_name]
        else:
            sub_group = H5Group(group_name, group.h5_file)
            group.addSubGroup(sub_group)

        self.setAttribute(attribute_name=attribute_name,
                             config=config,
                             group_name='_'.join(group_name_list),
                             group=sub_group)
        return

    def setDataset(self, dataset_name:str, data:np.ndarray, dtype:str, group:H5Group=None):
        if group is None:
            group = self._H5_group
            assert group is not None, 'Root H5 group should not be None type object.'

        if dataset_name[0] == '/':
            dataset_name = dataset_name[1:]
        group_name_list = dataset_name.split('/')
        dataset_name = group_name_list.pop(-1)
        if len(group_name_list) == 0:
            self._file.require_dataset(name=dataset_name,data=data, shape=data.shape, dtype=dtype)
        else:
            self._file['_'.join(group_name_list)].require_dataset(name=dataset_name,data=data, shape=data.shape, dtype=dtype)
        self._createH5Object(file_group=self._file, group=group)




class H5Creator():
    def __init__(self):
        self._file:File = None
        pass

    @property
    def H5(self):
        return self._file

    def deleteH5(self):
        if self._file:
            print(self._file.filename)
            path = self._file.filename
            self._file.close()
            Path(path).unlink(missing_ok=True)
            # os.remove(path)
            self._file = None
        pass

    def closeH5(self):
        if self._file is not None:
            self._file.flush()
            self._file.close()

    def createH5File(self, file_path):
        from h5py import File
        if not Path(file_path).parent.exists():
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        self._file = File(file_path, 'x')
        return self._file

    @classmethod
    def setRecordingConfigs(cls, h5:File, h5_data_config:H5Group):
        h5_data_config.h5_file = h5
        h5_data_config.createGroup()
        h5_data_config.updateH5Attributes()

    @classmethod
    def updateDataset(self, data_set:H5DataSet, data):
        data_set.updateDataSet(data)

    def addDataset(self, name, shape, group:H5Group, dtype='int16')->H5DataSet:
        ds = H5DataSet(name=name, dtype=dtype)
        # for DS_name in group.sub_datasets.keys():
        #     if ds.name == DS_name.split('/')[-1]:
        #         ds = group.sub_datasets[DS_name]
        #         ds.createDataSet()

        group.addDataSet(ds)
        return ds


    def encryptH5toKKT(self, is_kkt_only=False):
        Encryptor.encryptToKKT(file_path=self._file.filename)
        if is_kkt_only:
            self.deleteH5()

    def genSaveFileName(self, gesture_name:list, data_number:str, data_time:str, Info:tuple=None):
        gesture = '_'.join((ges for ges in gesture_name))
        # gesture = gesture.replace(' ', '_')
        if Info is None:
            Info = []
        save_file_Name = '_'.join([gesture, f'{int(data_number):04}', data_time]+list(Info))
        return save_file_Name

    def genSaveDir(self, root:str , data_type:str, record_dir:str=''):
        '''
        save_file_dir = os.path.join(root, data_type_dir, record_dir)
        '''
        data_dict= {'RDIPHD':'RDI_fx',
                    'RawData':'RawData'}
        if data_dict.get(data_type) is None:
            data_type = data_dict.get(data_type)
        # record_dir = recording_config.Record_Folder
        save_file_dir = Path(root).joinpath( data_type, record_dir)
        if not Path(save_file_dir).parent.exists():
            Path(save_file_dir).mkdir(parents=True, exist_ok=True)
            print('Make Data record dir : {}'.format(save_file_dir))
        return str(save_file_dir)


if __name__ == '__main__':
    from KKTRecordingConfig import KKTRecordConfig
    from Core.Groups import *
    def test_creator(file):
        data_config = DataConfig(Data_format='RDIPHD')
        RF_config = RFConfig()
        RDI_config = RDIConfig()
        PHD_config = PHDConfig()
        AGC_config = AGCConfig()
        AIC_config = AICConfig()
        DSP_config = DSPConfig()
        Video_config = VideoConfig()

        RC = KKTRecordConfig(Data_Configs=data_config,
                             RF_Configs=RF_config,
                             RDI_Configs=RDI_config,
                             PHD_Configs=PHD_config,
                             AGC_Configs=AGC_config,
                             AIC_Configs=AIC_config,
                             DSP_Configs=DSP_config,
                             Video_Configs=Video_config,
                             )
        e = H5Editor()
        e.createH5File('123.h5')
        e.setRecordingConfigs(e.H5, RC.Root)
        RC.Root.updateH5Attributes()
        e.closeH5()
    def test_editor(file):
        reader = H5Editor()
        reader.openH5File(file)
        reader.showH5Attributes()
        reader.closeH5()
        print('')

    # Encryptor.encryptToKKT(r'C:\Users\eric.li\Desktop\Python\0_Standard_Ksoc_Tool\Record\RawData\1\NearDoublePinch_0001_2022_12_15_15_57_07.h5')
    test_editor(r'C:\Users\eric.li\Desktop\Python\0_Standard_Ksoc_Tool\Record\RawData\1\NearDoublePinch_0001_2022_12_15_15_57_07.h5')

