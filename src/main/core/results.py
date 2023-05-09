# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/2/14 下午5:13

import tkinter
from tkinter import ttk
from tkinter.constants import *


class ResultWindow:

    def __init__(self, master):
        self.child_window = tkinter.Toplevel(master)
        self.child_window.title("测试结果")
        self.child_window.geometry('1100x600+160+100')

        self.result_table = None

    def create_result_view(self, cols):
        child_frame = tkinter.Frame(self.child_window, borderwidth=5)
        result_frame = tkinter.Frame(child_frame, borderwidth=5)
        child_frame.pack()

        # 布置内容展示表格和滚动条
        table_columns = cols
        style = ttk.Style()
        style.configure('Table.Treeview.Heading', font=('宋体', 12), relief='sunken')
        style.configure('Table.Treeview', rowheight=40)
        self.result_table = ttk.Treeview(result_frame,
                                         columns=table_columns,
                                         height=10,  # 要显示的行数
                                         show='headings',
                                         style='Table.Treeview')
        for col in table_columns:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, minwidth=0, anchor=CENTER, stretch=True)  # stretch列的宽度是否随整个部件的改动而变化
        self.result_table.grid(row=1, column=2, columnspan=2, sticky=N + S + E + W)

        # 设置y轴的滚动条，并将滚动条与treeview控件联动
        yscrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_table.yview())
        yscrollbar.config(command=self.result_table.yview)
        yscrollbar.grid(row=1, column=4, sticky=N + S)
        self.result_table.config(yscrollcommand=yscrollbar.set)
        result_frame.pack(side=TOP, fill=X, expand=1)

        # 布置确认按钮
        button = tkinter.Button(child_frame, text="确认", fg='blue', command=self.child_window.destroy)
        button.pack(side=BOTTOM)
