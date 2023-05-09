# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/2/10 下午6:16

import os
import configparser
from src.main.lib.globals import gbl


class Configuration:

    def __init__(self):

        self.service = {}  # 业务参数，可以修改

    def load_properties(self):
        self.service = Properties(os.path.dirname(__file__) + "/application.properties").get_properties()
        for key, value in self.service.items():
            gbl.service.set(key, value)


class Properties(object):

    def __init__(self, path):
        self.properties = {}
        self.path = path

    def __get_dict(self, strName, dictName, value):
        if strName.find('.') > 0:
            k = strName.split('.')[0]
            dictName.setdefault(k, {})
            return self.__get_dict(strName[len(k) + 1:], dictName[k], value)
        else:
            dictName[strName] = value
            return

    def get_properties(self):

        with open(self.path, 'r') as f:
            for line in f.readlines():
                line = line.strip().replace('\n', '')
                if line.find("#") != -1:
                    line = line[0:line.find('#')]
                if line.find('=') > 0:
                    strs = line.split('=')
                    strs[1] = line[len(strs[0]) + 1:]
                    self.__get_dict(strs[0].strip(), self.properties, strs[1].strip())

        return self.properties


class IniConfig:

    def __init__(self, ini_dir):

        # 对内容隐藏字符做处理，替换隐藏字符
        # content = open(ini_dir).read()
        # content = re.sub(r"\n", "", content)
        # content = re.sub(r"\xfe\xff", "", content)
        # content = re.sub(r"\xff\xfe", "", content)
        # content = re.sub(r"\xef\xbb\xbf", "", content)
        # open(dir, 'w').write(content)

        self.cf = configparser.ConfigParser()
        self.config = self.cf.read(ini_dir)

    def get_sections(self):
        return self.cf.sections()

    def get_option(self, section):
        return self.cf.options(section)

    def get_value(self, section, option):
        return self.cf.get(section, option)

    def get_config(self):
        self.config = {}
        for s in self.get_sections():
            _config = {}
            for o in self.get_option(s):
                value = self.get_value(s, o)
                _config[o] = value
            self.config[s] = _config
        return self.config


config = Configuration()
