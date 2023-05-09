# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/2/17 下午2:51

from tinui.TinUI import TinUI


class TinUISpace:

    def __init__(self, master):
        self.ui = TinUI(master)
        self.ui.pack(fill='both', expand=True)

    def add_table(self, data):
        self.ui.add_table(pos=(0, 0),
                          outline='#E1E1E1',
                          fg='black',
                          bg='white',
                          data=data,
                          minwidth=150,
                          font=('微软雅黑', 12),
                          headbg='#d9ebf9')


