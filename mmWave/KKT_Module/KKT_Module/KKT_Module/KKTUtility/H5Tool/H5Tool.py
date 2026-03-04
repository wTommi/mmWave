from KKT_Module.KKTUtility.H5Tool.H5Edition import H5Editor

class KKTH5Tool:
    @classmethod
    def getGestureDict(cls, filename:str):
        '''
        :param weights_path: AI Weight H5 file
        :return: gesture mapping dict , background id
        '''
        editor = H5Editor()
        editor.openH5File(filename)
        gesture_dicts = {}
        gesture_map_list = ['Mapping_dict', 'Mapping_dict_core', 'Mapping_dict_siamese']
        for gesDict in gesture_map_list:
            # note that you read a bytes data from h5, but it is string in python3 actually, str=b'123'
            if editor.getH5Dataset(gesDict) is None:
                continue
            mapping_dict = editor.getH5Dataset(gesDict)
            gesture_dicts[gesDict] = mapping_dict
        editor.closeH5()
        return gesture_dicts

    @classmethod
    def readData(cls, filename):
        print('# =============== Read H5 Dataset ================')
        # open h5 file
        editor = H5Editor()
        editor.openH5File(filename)
        # f = cls.openH5(filename)
        # extract RDI/PhD from h5 data and transform as numpy
        data = editor.getH5Dataset('DS1')
        if data is not None:
            # data = data[:].astype(np.float32)
            # data = data[0, :, :, 0]
            print(data.shape)

        # extract label from h5 data and transform as numpy
        label = editor.getH5Dataset('LABEL')
        if label is not None:
            print(label.shape)

        # extract axis from h5 data and transform as numpy
        axis = editor.getH5Dataset('AXIS')
        if axis is not None:
            print(axis.shape)
        # remember to close file
        editor.closeH5()
        return data, label, axis

    # -------- parsing H5 file--------------
    @classmethod
    def parsingRecordH5(cls, filename):
        # open h5 file
        print('======== Parse h5 file info ==========')
        editor = H5Editor()
        editor.openH5File(filename)
        editor.showH5Attributes()
        editor.closeH5()
        return

    @classmethod
    def getH5Attribute(cls, filename, group_name, attribute=None) -> dict:
        print('# ======== get h5 attrs ==========')
        editor = H5Editor()
        editor.openH5File(filename)
        config = editor.getH5Attribute(attribute_name=attribute, group_name=group_name)
        editor.closeH5()
        return config






if __name__ == '__main__':
    H5_path = r'C:\Users\eric.li\Desktop\Python\0_Sniff_Collection_Tool\Record\RawData\KKT\_2022_10_31_19_26_02.h5'
    KKTH5Tool.readData(H5_path)

