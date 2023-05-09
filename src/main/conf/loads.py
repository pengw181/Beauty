# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/20 上午10:24

import os


class Properties(object):

    def __init__(self):
        self.fileName = os.path.dirname(__file__) + "/application.properties"
        self.properties = {}

    def __get_dict(self, strName, dictName, value):
        if strName.find('.') > 0:
            k = strName.split('.')[0]
            dictName.setdefault(k, {})
            return self.__get_dict(strName[len(k)+1:], dictName[k], value)
        else:
            dictName[strName] = value
            return

    def get_properties(self):
        try:
            pro_file = open(self.fileName, 'r')
            for line in pro_file.readlines():
                line = line.strip().replace('\n', '')
                if line.find("#") != -1:
                    line = line[0:line.find('#')]
                if line.find('=') > 0:
                    strs = line.split('=')
                    strs[1] = line[len(strs[0])+1:]
                    self.__get_dict(strs[0].strip(), self.properties, strs[1].strip())
        except Exception as e:
            raise e
        else:
            pro_file.close()
        return self.properties


properties = Properties().get_properties()
