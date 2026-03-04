from __future__ import annotations
import array
from dataclasses import dataclass, asdict, field
from h5py import File, Group, Dataset
import numpy as np
from typing import Dict, Optional


@dataclass()
class DataH5():
    name: str = '/'
    # h5_file: File = None


class H5Group():
    @property
    def sub_groups(self):
        return self._groups
    @property
    def sub_datasets(self):
        return self._datasets
    def __init__(self, name:str='/', h5_data_class:DataH5=None, h5_file:Optional[File] = None):
        self.name = name
        if h5_data_class is None:
            h5_data_class = DataH5()
        self.h5_data_class = h5_data_class
        self.h5_file = h5_file
        self._groups: Dict[str, H5Group] = {}
        self._datasets: Dict[str, H5DataSet] = {}

    def __getitem__(self, item):
        if item in self.h5_data_class.__dict__:
            return self.h5_data_class.__getattribute__(item)
        else:
            raise KeyError(f'{item} not found in {self.name}')

    def createGroup(self):
        '''
        Create the group in H5 file.
        If there's subgroups in this class, it will create subgroups in H5 file either.
        If there's datasets in this class, it will create datasets in H5 file either.
        '''
        assert self.h5_file is not None, 'None h5 files.'
        self.h5_file.require_group(self.name)
        for group in self._groups.values():
            group.h5_file = self.h5_file
            group.createGroup()

        for data_set in self._datasets.values():
            data_set.h5_file = self.h5_file
            data_set.createDataSet()
        return

    def updateH5Attributes(self):
        attributes = asdict(self.h5_data_class)
        for attr, config in attributes.items():
            if attr in ['h5_file', 'name', '_groups', '_datasets']:
                continue
            if config is None: # config should not be null
                config = str(config)
            self.setH5Attribute(attr, config)
        for group in self._groups.values():
            group.updateH5Attributes()
        pass

    def setH5Attribute(self, attribute, config):
        assert self.h5_file is not None, 'None h5 files.'
        # print(f'[{self.name}] {attribute} : {config}')
        self.h5_file[self.name].attrs[attribute] = config

    def getH5Attribute(self, attribute:str):
        '''
        Get attribute from current group of h5 file.
        '''
        assert self.h5_file is not None, 'None h5 files.'
        config = self.h5_file[self.name].attrs.get(attribute)
        if config:
            print('[{}] {} : {}'.format(self.name, attribute, config))
        return config

    def getH5Attributes(self):
        '''
        Get all attributes from group of h5 file.
        '''
        assert self.h5_file is not None, 'None h5 files.'
        config = dict(self.h5_file[self.name].attrs.items())
        if config:
            print('[{}]'.format(self.name))
        return config

    def getH5Dict(self, n=0)->Optional[dict]:
        '''
        Get all attributes from group of h5 file.
        '''
        if self.name not in self.h5_file.keys():
            return
        # print('\n' + ' ' * n, '[{}]'.format(self.name))

        group_dict={}
        for attr, config in dict(self.h5_file[self.name].attrs).items():
            print('  ' * (n + 1), '{} : {}'.format(attr, config))
            group_dict[attr] = config

        for group in self._groups.values():
            sub_group_dict = group.getH5Dict(n)
            if sub_group_dict:
                group_dict.update(sub_group_dict)

        data_set_dict = {}
        for data_set in self._datasets.values():
            data_set_dict[data_set.name] = data_set.getDataSet()
            group_dict.update(data_set_dict)

        return {self.name:group_dict}

    def addSubGroup(self, group):
        name = group.name
        if self.name == '/':
            group.name = self.name + group.name
        else:
            group.name = self.name + '/' + group.name
        group.h5_file = self.h5_file
        self._groups.setdefault(name, group)
        pass

    def getSubGroup(self, name:str)->Optional[H5Group]:
        group = self._groups.get(name)
        if group is None:
            for n , g in self.sub_groups.items():
                group = g.getSubGroup(name)
                if group is not None:
                    break
        return group

    def popSubGroup(self, name:str)->Optional[H5Group]:
        group = self._groups.get(name)
        if group is None:
            for n, g in self.sub_groups.items():
                group = g.getSubGroup(name)
                if group is not None:
                    break
        else:
            self._groups.pop(name)
        return group

    def addDataSet(self, data_set):
        name = data_set.name
        if self.name == '/':
            data_set.name = self.name + data_set.name
        else:
            data_set.name = self.name + '/' + data_set.name
        data_set.h5_file = self.h5_file
        self._datasets.setdefault(name, data_set)
        pass

    def showGroup(self, n=0):
        print('\n'+' '* n, '[{}]'.format(self.name))
        attributes = asdict(self.h5_data_class)
        for attr, config in attributes.items():
            if attr in ['h5_file', 'name', '_groups', '_datasets']:
                continue
            print('  '* (n+1), '{} : {}'.format(attr, config))
        for group in self._groups.values():
            group.showGroup(n)

        for data_set in self._datasets.values():
            data_set.showDataSet(n)

    def printAttributes(self, n=0):
        '''
        Print all attributes from group of h5 data class.
        '''
        print('\n'+' '* n, '[{}]'.format(self.name))
        attributes = asdict(self.h5_data_class)
        for attr, config in attributes.items():
            if attr in ['h5_file', 'name', '_groups', '_datasets']:
                continue
            print('  '* (n+1), '{} : {}'.format(attr, config))
        for group in self._groups.values():
            group.printAttributes(n)

    def showH5Attributes(self, n=0):
        '''
        Show all attributes from group of h5 file.
        '''
        if self.name not in self.h5_file.keys():
            return []
        txt_list = []
        group_label_txt = f'\n{" " * n}[{self.name}]'
        txt_list.append(group_label_txt)
        print(group_label_txt)

        for attr, config in dict(self.h5_file[self.name].attrs).items():
            attr_txt = f'{" "*(n+1)}{attr} : {config}'
            txt_list.append(attr_txt)
            print(attr_txt)

        for group in self._groups.values():
            t = group.showH5Attributes(n)
            txt_list.extend(t)

        for data_set in self._datasets.values():
            t = data_set.showH5DataSet(n)
            txt_list.extend(t)

        return txt_list

@dataclass
class H5DataSet():
    def __init__(self, name:str='/', dtype:str='int32', h5_file:File=None):
        self.name = name
        self.h5_file = h5_file
        self.dtype = dtype
    def createDataSet(self, shape:tuple=(0,)):
        '''
        Create dataset which data format follow init args in H5 file.
        '''
        assert self.h5_file is not None, 'None h5 files.'
        if isinstance(self.h5_file.get(self.name), Dataset):
            self.h5_file.pop(self.name)
        self.h5_file.require_dataset(name=self.name,data=np.zeros(shape) , shape=shape, dtype=self.dtype)
        return self.h5_file[self.name]

    def updateDataSet(self, data):
        '''
        Rewrite input data to dataset.
        '''
        assert self.h5_file is not None, 'None h5 files.'
        if not isinstance(self.h5_file.get(self.name), Dataset):
            self.createDataSet(shape = data.shape)
        else:
            if self.h5_file[self.name].shape != data.shape:
                self.createDataSet(shape = data.shape)
        self.h5_file[self.name][:] = data

    def getDataSet(self):
        assert self.h5_file is not None, 'None h5 files.'
        # print('[{}] shape:{}, type:{}'.format(self.name, self.h5_file[self.name].shape, self.h5_file[self.name].dtype))
        if self.h5_file[self.name].dtype.name == 'object':
            return eval(self.h5_file[self.name][()].decode())
        else:
            return self.h5_file[self.name][()]

    def getDataSetObject(self):
        assert self.h5_file is not None, 'None h5 files.'
        # print('[{}] shape:{}, type:{}'.format(self.name, self.h5_file[self.name].shape, self.h5_file[self.name].dtype))
        return self.h5_file[self.name]

    def showDataSet(self,n=0):
        print('\n' + ' ' * n, '[{}]'.format(self.name))
        for attr, config in self.__dict__.items():
            if attr in ['h5_file', 'name', '_groups', '_datasets']:
                continue
            print('  ' * (n + 1), '{} : {}'.format(attr, config))

    def showH5DataSet(self, n=0):
        if self.name not in self.h5_file.keys():
            return []
        label_txt = f'\n{" " * n}[{self.name}]'
        print(label_txt)
        shape_txt = f'{" " * (n + 1)}shape : {self.h5_file[self.name].shape}'
        print(shape_txt)
        type_txt = f'{" " * (n + 1)}type  : {self.h5_file[self.name].dtype}'
        print(type_txt)
        return [label_txt, shape_txt, type_txt]


class H5DynamicDataSet(H5DataSet):
    '''
    args:
        name : dataset name create in H5 file.
        shape : Tuple of data set shape, set None that which axis data is appended dynamically.

            ex. (2, 32, 128, None) -> H5 file appended data in shape(2, 32, 128) in axis "3" dynamically.

        dtype : Data type in dataset, default is int32.

    '''
    def __init__(self, name:str='/', dtype:str='int32',axis:int=0, h5_file:File=None):
        super().__init__(h5_file=h5_file, name=name, dtype=dtype)
        self.axis = axis

    def createDataSet(self, shape:tuple=(0,)):
        '''
        Create a data set in h5 file.
        '''
        assert self.h5_file is not None, 'None h5 files.'
        if isinstance(self.h5_file.get(self.name), Dataset):
            self.h5_file.pop(self.name)
        max_shape = list(shape)
        shape = list(shape)
        max_shape.insert(self.axis, None)
        shape.insert(self.axis, 0)
        self.h5_file.require_dataset(self.name, shape=shape, data=np.zeros(shape=tuple(shape)), dtype=self.dtype, maxshape=max_shape, chunks=True)
        return self.h5_file[self.name]

    def updateDataSet(self, data):
        '''
        Update data in data set.
        '''
        assert self.h5_file is not None, 'None h5 files.'
        if not isinstance(self.h5_file.get(self.name), Dataset):
            self.createDataSet(shape = data.shape)
        else:
            max_shape = list(data.shape)
            max_shape.insert(self.axis, None)
            if list(self.h5_file[self.name].maxshape) != list(max_shape):
                self.createDataSet(shape = data.shape)
        self.h5_file[self.name].resize(self.h5_file[self.name].shape[self.axis]+1, axis=self.axis)
        # d = self.replaceAxisData(self.h5_file[self.name], self.axis)
        # d = data
        if self.axis == 0:
            self.h5_file[self.name][self.h5_file[self.name].shape[self.axis]-1] = data
        elif self.axis == len(self.h5_file[self.name].maxshape)-1:
            self.h5_file[self.name][...,self.h5_file[self.name].shape[self.axis] - 1] = data
    def replaceAxisData(self, data:array.array, axis:int):
        if axis == 0:
            return data[-1]
        else:
            return self.replaceAxisData(data[:], axis-1)






if __name__ == '__main__':
    f = File('test2.H5', 'w')
    # ds1 = H5DataSet(h5_file=f, name='DS1')
    ds1 = H5DynamicDataSet(h5_file=f, name='DS1', axis=3)
    # ds1.createDataSet()
    g1 = H5Group(h5_file=f, name='6666')
    g1.addDataSet(ds1)
    g1.updateH5Attributes()
    # ds1.updateDataSet(np.ones((2,2,32,128)))
    ds1.updateDataSet(np.ones((2, 32, 128)))
    ds1.updateDataSet(np.ones((2, 32, 128)))
    ds1.updateDataSet(np.ones((2, 32, 128)))
    ds1.showH5DataSet()
    f.close()

