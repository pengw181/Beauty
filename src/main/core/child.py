# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/2/14 下午5:13

import os
import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter.constants import *
from src.main.lib.logger import log
from src.main.lib.globals import gbl


class ChildWindow:

    def __init__(self, master):
        self.child_window = tkinter.Toplevel(master)
        self.child_window.title("更多参数")
        self.child_window.geometry('1100x600+160+100')

        self.properties_frame = None
        self.yaml_frame = None
        self.prop_combobox = None
        self.yaml_combobox = None
        self.properties_text = None
        self.yaml_text = None

        self.conf_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/conf/'
        self.prop_filename = None
        self.yaml_filename = None
        self.prop_file_content = None
        self.yaml_file_content = None
        self.files = None

    def create_child_main(self):
        child_frame = tkinter.Frame(self.child_window, borderwidth=5)
        child_frame.pack()
        # child框架分成上下两部分，底部是按钮
        child_body_frame = tkinter.Frame(child_frame, borderwidth=5)
        child_body_frame.pack(side=TOP, fill=BOTH, expand=1)
        child_bottom_frame = tkinter.Frame(child_frame, borderwidth=5)
        child_bottom_frame.pack(side=BOTTOM, fill=BOTH, expand=1)

        # 将body区域均分成左右两半，分别用来展示properties和yaml配置文件
        child_body_frame.grid_rowconfigure(0, weight=1)
        child_body_frame.grid_columnconfigure(0, weight=1)
        child_body_frame.grid_columnconfigure(1, weight=1)
        self.properties_frame = tkinter.Frame(child_body_frame, borderwidth=5)
        self.yaml_frame = tkinter.Frame(child_body_frame, borderwidth=5)
        self.properties_frame.grid(column=0, row=0, sticky=N+S+E+W)
        self.yaml_frame.grid(column=1, row=0, sticky=N+S+E+W)
        self.layout_properties_frame()
        self.layout_yaml_frame()

        # properties文件回显
        if gbl.service.get("PropContent"):
            self.properties_text.delete('1.0', 'end')
            file_content = gbl.service.get("PropContent")
            self.properties_text.insert(INSERT, file_content)

        # yaml文件回显
        if gbl.service.get("YamlContent"):
            self.yaml_text.delete('1.0', 'end')
            file_content = gbl.service.get("YamlContent")
            self.yaml_text.insert(INSERT, file_content)

        # 布置确认按钮
        button = tkinter.Button(child_bottom_frame, text="确认", fg='blue', command=self.ok)
        button.pack(side=BOTTOM)

    def layout_properties_frame(self):
        header_frame = tkinter.Frame(self.properties_frame, borderwidth=5)
        properties_content_frame = tkinter.Frame(self.properties_frame, borderwidth=5)

        # 遍历conf目录，寻找所有properties文件
        prop_list = ['请选择']
        for filename in os.listdir(self.conf_path):
            if filename.endswith(".properties"):
                prop_list.append(filename)
        if self.prop_filename is None:
            self.prop_filename = gbl.service.get("PropFilename")
        # noinspection PyBroadException
        try:
            current = prop_list.index(self.prop_filename)
        except:
            current = 0

        # 布置properties下拉框
        prop_label = tkinter.Label(header_frame, text="Properties: ")
        prop_label.grid(column=0, row=0, rowspan=3)
        self.prop_combobox = ttk.Combobox(header_frame)
        self.prop_combobox["values"] = tuple(prop_list)
        self.prop_combobox.current(current)
        self.prop_combobox.bind("<<ComboboxSelected>>", self.choose_prop)
        self.prop_combobox.grid(column=1, row=0, rowspan=3)

        # text展示properties内容
        properties_content_frame.grid_rowconfigure(0, weight=10)
        properties_content_frame.grid_rowconfigure(1, weight=1)
        properties_content_frame.grid_columnconfigure(0, weight=10)
        properties_content_frame.grid_columnconfigure(1, weight=1)

        # 将Text控件添加进Frame控件
        self.properties_text = tkinter.Text(properties_content_frame, relief='sunken')
        self.properties_text.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W, padx=(2, 2), pady=5)

        # 设置y轴的滚动条，并将滚动条与text控件联动
        yscrollbar = tkinter.Scrollbar(properties_content_frame)
        yscrollbar.grid(row=0, column=3, columnspan=1, sticky=N+S+E+W)
        yscrollbar.config(command=self.properties_text.yview)
        self.properties_text.config(yscrollcommand=yscrollbar.set)

        # 设置x轴的滚动条，并将滚动条与text控件联动
        xscrollbar = ttk.Scrollbar(properties_content_frame, orient='horizontal')
        xscrollbar.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)
        xscrollbar.config(command=self.properties_text.xview)
        self.properties_text.config(xscrollcommand=xscrollbar.set)
        self.properties_text.config(wrap=NONE)  # 不自动换行

        # 布置编辑按钮
        button = tkinter.Button(header_frame, text="编辑", command=self.edit_properties)
        button.grid(column=2, row=0)
        # 布置锁定按钮
        button = tkinter.Button(header_frame, text="锁定", command=self.lock_properties)
        button.grid(column=3, row=0)

        header_frame.pack(side=TOP, fill=X, expand=0)
        properties_content_frame.pack(side=TOP, fill=BOTH, expand=1)

    def layout_yaml_frame(self):
        header_frame = tkinter.Frame(self.yaml_frame, borderwidth=5)
        yaml_content_frame = tkinter.Frame(self.yaml_frame, borderwidth=5)

        # 遍历conf目录，寻找所有yaml文件，包含后缀.yaml或.yml
        yaml_list = ['请选择']
        for filename in os.listdir(self.conf_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                yaml_list.append(filename)
        if self.yaml_filename is None:
            self.yaml_filename = gbl.service.get("YamlFilename")
        # noinspection PyBroadException
        try:
            current = yaml_list.index(self.yaml_filename)
        except:
            current = 0

        # 布置yaml下拉框
        yaml_label = tkinter.Label(header_frame, text="Yaml: ")
        yaml_label.grid(column=0, row=0, rowspan=3)
        self.yaml_combobox = ttk.Combobox(header_frame)
        self.yaml_combobox["values"] = tuple(yaml_list)
        self.yaml_combobox.bind("<<ComboboxSelected>>", self.choose_yaml)
        self.yaml_combobox.grid(column=1, row=0, rowspan=3)
        self.yaml_combobox.current(current)

        # text展示yaml内容
        yaml_content_frame.grid_rowconfigure(0, weight=15)
        yaml_content_frame.grid_rowconfigure(1, weight=1)
        yaml_content_frame.grid_columnconfigure(0, weight=10)
        yaml_content_frame.grid_columnconfigure(1, weight=1)

        # 将Text控件添加进Frame控件
        self.yaml_text = tkinter.Text(yaml_content_frame, relief='sunken')
        self.yaml_text.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W, padx=(2, 2), pady=5)

        # 设置y轴的滚动条，并将滚动条与text控件联动
        yscrollbar = tkinter.Scrollbar(yaml_content_frame)
        yscrollbar.grid(row=0, column=3, columnspan=1, sticky=N+S+E+W)
        yscrollbar.config(command=self.yaml_text.yview)
        self.yaml_text.config(yscrollcommand=yscrollbar.set)

        # 设置x轴的滚动条，并将滚动条与text控件联动
        xscrollbar = ttk.Scrollbar(yaml_content_frame, orient='horizontal')
        xscrollbar.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)
        xscrollbar.config(command=self.yaml_text.xview)
        self.yaml_text.config(xscrollcommand=xscrollbar.set)
        self.yaml_text.config(wrap=NONE)  # 不自动换行

        # 布置编辑按钮
        button = tkinter.Button(header_frame, text="编辑", command=self.edit_yaml)
        button.grid(column=2, row=0)
        # 布置锁定按钮
        button = tkinter.Button(header_frame, text="锁定", command=self.lock_yaml)
        button.grid(column=3, row=0)

        header_frame.pack(side=TOP, fill=X, expand=0)
        yaml_content_frame.pack(side=TOP, fill=BOTH, expand=1)

    def choose_prop(self, *args):
        # 选择properties后自动将内容展示出来
        self.prop_filename = self.prop_combobox.get()
        log.info("Properties: {}".format(self.prop_filename))
        gbl.service.set("PropFilename", self.prop_filename)

        self.edit_properties()
        self.properties_text.delete('1.0', 'end')
        file_content = ""
        first_line = True
        with open(self.conf_path + self.prop_filename, 'r') as f:
            for line in f.readlines():
                if not file_content and first_line:
                    file_content = line
                    first_line = False
                else:
                    file_content += line
        self.properties_text.insert(INSERT, file_content)
        self.lock_properties()

    def edit_properties(self, *args):
        self.properties_text.config(state=NORMAL)

    def lock_properties(self, *args):
        self.properties_text.config(state=DISABLED)

    def choose_yaml(self, *args):
        # 选择yaml后自动将内容展示出来
        self.yaml_filename = self.yaml_combobox.get()
        log.info("Yaml: {}".format(self.yaml_filename))
        gbl.service.set("YamlFilename", self.yaml_filename)

        self.edit_yaml()
        self.yaml_text.delete('1.0', 'end')
        file_content = ""
        first_line = True
        with open(self.conf_path + self.yaml_filename, 'r') as f:
            for line in f.readlines():
                if not file_content and first_line:
                    file_content = line
                    first_line = False
                else:
                    file_content += line
        self.yaml_text.insert(INSERT, file_content)
        self.lock_yaml()

    def edit_yaml(self, *args):
        self.yaml_text.config(state=NORMAL)

    def lock_yaml(self, *args):
        self.yaml_text.config(state=DISABLED)

    def ok(self, *args):
        files = {}
        miss = False
        if self.prop_filename:
            prop_content = self.properties_text.get('1.0', 'end')
            self.prop_file_content = prop_content
            files[self.prop_filename] = self.prop_file_content
            gbl.service.set("PropContent", prop_content)
        else:
            miss = True
        if self.yaml_filename:
            yaml_content = self.yaml_text.get('1.0', 'end')
            self.yaml_file_content = yaml_content
            files[self.yaml_filename] = self.yaml_file_content
            gbl.service.set("YamlContent", yaml_content)
        else:
            miss = True

        if miss:
            choice = tkinter.messagebox.askokcancel(title='Warn', message="配置文件未选择将使用服务端默认配置")
            if choice:
                self.child_window.destroy()
        else:
            self.child_window.destroy()
        self.files = files
