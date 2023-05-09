# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/1/30 下午3:17

import tkinter
import threading
from time import sleep
from tkinter.constants import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import warnings
from src.main.bin.request_start import request_server
from src.main.lib.thds import stop_thread
from src.main.lib.files import read_file
from src.main.core.child import ChildWindow
from src.main.core.results import ResultWindow
from src.main.lib.logger import log
from src.main.lib.globals import gbl
from src.main.conf.config import config
warnings.filterwarnings('ignore')


class Application:

    """
    __________________________________________________________________________________
    |           _____________          _____________                                  |
    |    应用:  |____________|文件路径: |____________|  选择文件  预览   退出             |
    |                                                                                 |
    |    ________________________________________________________________________     |
    |   |                                   |                                   |     |
    |   |                                 滚|             _____________        |      |
    |   |                                 动|    用例文件: |___2_________|       |      |
    |   |                                 条|              _____________        |      |
    |   |                                   |    开始行  : |___2_________|       |     |
    |   |                                   |                                   |     |
    |   |                                   |          运 行                     |     |
    |   |                                   |                                   |     |
    |   |                                   |                                   |     |
    |   | ________滚动条_____________________|__________________________________｜     |
    |                                                                                 |
    |                                                                                 |
    |_________________________________________________________________________________|

    """
    def __init__(self):
        self.tk = tkinter.Tk()
        self.init_window()

        self.content_text_frame = None
        self.content_table_frame = None
        self.app_combobox = None
        self.env_combobox = None
        self.select_path = None
        self.filename_label = None
        self.content_text = None
        self.content_table = None
        self.log_text = None
        self.auto_refresh = None
        self.file_entry = None
        self.file_begin_entry = None
        self.case_begin_entry = None
        self.log_path_entry = None
        self.username_entry = None
        self.password_entry = None
        self.run_button = None

        self.application = None
        self.environment = None
        self.view_file_path = None
        self.file_name = ""
        self.log_file = None
        self.reload_thread = None

        self.child_win = None   # 更多子窗口

        self.app_list = ('AiSee', 'VisualModeler', 'AlarmPlatform', 'WebApi', 'Crawler')
        self.env_list = ('v31_postgres', 'v31_oracle', 'v31_maria', 'v30_postgres', 'v33_maria')

    def init_window(self):
        width, height = self.tk.maxsize()
        self.tk.geometry('{}x{}'.format(int(width*0.8), int(height*0.9)))
        # self.tk.geometry('{}x{}'.format(width, height))
        self.tk.resizable(False, False)
        self.tk.title('Welcome to Auto-Test program')

    def create_main_page(self):

        self.create_header()
        self.create_file_view()
        self.create_body()

    def create_header(self):

        header_frame = tkinter.Frame(self.tk, borderwidth=5)
        header_frame.pack(side=TOP, fill=X, expand=0)

        # 布置application下拉框
        app_label = tkinter.Label(header_frame, text="应用: ")
        app_label.grid(column=0, row=0, rowspan=3)
        self.app_combobox = ttk.Combobox(header_frame)
        self.app_combobox["values"] = self.app_list
        self.app_combobox.current(1)
        self.app_combobox.bind("<<ComboboxSelected>>", self.choose_app)
        self.app_combobox.grid(column=1, row=0, rowspan=3)

        # 布置environment下拉框
        app_label = tkinter.Label(header_frame, text="环境: ")
        app_label.grid(column=2, row=0, rowspan=3)
        self.env_combobox = ttk.Combobox(header_frame)
        self.env_combobox["values"] = self.env_list
        self.env_combobox.current(0)
        self.env_combobox.bind("<<ComboboxSelected>>", self.choose_env)
        self.env_combobox.grid(column=3, row=0, rowspan=3)

        # 布置文件选择组件
        self.select_path = tkinter.StringVar()
        file_label = tkinter.Label(header_frame, text="文件路径: ")
        file_label.grid(column=4, row=0, rowspan=3)
        self.file_entry = tkinter.Entry(header_frame, textvariable=self.select_path)
        self.file_entry.grid(column=5, row=0, rowspan=3)
        file_button = tkinter.Button(header_frame, text="选择文件", command=self.select_file)
        file_button.grid(column=6, row=0, rowspan=3)

        # 布置预览文件内容按钮
        view_button = tkinter.Button(header_frame, text="预览", command=self.show_file)
        view_button.grid(column=8, row=0)

        # 退出按钮
        exit_button = tkinter.Button(header_frame, text="退出", bg="gray", fg="blue", command=self.quit)
        exit_button.grid(column=9, row=0, sticky=E)

    def create_file_view(self):

        # body分成2部分，content_frame、param_frame，content_frame用来占住位置
        content_frame = tkinter.Frame(self.tk, borderwidth=5)
        content_frame.pack(side=TOP, fill=BOTH, expand=1)
        # content_frame.pack_propagate(1)

        # 定义2个frame，每次只有一个pack，另一个pack_forget
        self.content_text_frame = tkinter.Frame(content_frame, borderwidth=0)
        self.content_table_frame = tkinter.Frame(content_frame, borderwidth=0)
        # 初始化
        self.display_content_text()

    def display_content_text(self):
        self.content_text_frame.pack_forget()
        self.layout_text_content()
        self.content_text_frame.pack(side=TOP, fill=BOTH, expand=1)
        self.content_table_frame.pack_forget()

    def display_content_table(self, cols):
        self.content_table_frame.pack_forget()
        self.layout_table_content(cols)
        self.content_table_frame.pack(side=TOP, fill=BOTH, expand=1)
        self.content_text_frame.pack_forget()

    def create_body(self):
        # body分成左右两部分，左侧为参数配置，右侧输出日志
        body_frame = tkinter.Frame(self.tk)
        body_frame.pack(side=TOP, fill=BOTH, expand=1)
        body_frame.pack_propagate(1)
        body_frame.grid_rowconfigure(0, weight=1)
        body_frame.grid_columnconfigure(0, weight=1)
        body_frame.grid_columnconfigure(1, weight=4)

        # 参数配置
        param_frame = tkinter.Frame(body_frame, borderwidth=5, bg='green')
        param_frame.grid(column=0, row=0, padx=10, pady=10, sticky=W+S+N+E)
        # 展示参数配置
        title_label = tkinter.Label(param_frame, text="参数配置", bg='green')
        title_label.grid(column=1, row=0, pady=10, ipady=5, sticky=W)
        # 从哪一个用例文件开始
        need_label = tkinter.Label(param_frame, text="*", bg='green', fg='red')
        need_label.grid(column=0, row=1, sticky=E)
        file_begin_label = tkinter.Label(param_frame, text="用例文件行: ", bg='green')
        file_begin_label.grid(column=1, row=1, padx=3, pady=10, sticky=E)
        self.file_begin_entry = tkinter.Entry(param_frame)
        self.file_begin_entry.grid(column=2, row=1)
        # 从用例文件的第几行开始
        need_label = tkinter.Label(param_frame, text="*", bg='green', fg='red')
        need_label.grid(column=0, row=2, sticky=E)
        case_begin_label = tkinter.Label(param_frame, text="开始行: ", bg='green')
        case_begin_label.grid(column=1, row=2, padx=3, pady=10, sticky=E)
        self.case_begin_entry = tkinter.Entry(param_frame)
        self.case_begin_entry.grid(column=2, row=2)
        # 用户名
        need_label = tkinter.Label(param_frame, text="*", bg='green', fg='red')
        need_label.grid(column=0, row=3, sticky=E)
        username_label = tkinter.Label(param_frame, text="用户名: ", bg='green')
        username_label.grid(column=1, row=3, padx=3, pady=10, sticky=E)
        default_username = tkinter.StringVar(value='pw')    # 默认值
        self.username_entry = tkinter.Entry(param_frame, textvariable=default_username)
        self.username_entry.grid(column=2, row=3, columnspan=1)
        # 密码
        need_label = tkinter.Label(param_frame, text="*", bg='green', fg='red')
        need_label.grid(column=0, row=4, sticky=E)
        password_label = tkinter.Label(param_frame, text="密码: ", justify=RIGHT, bg='green')
        password_label.grid(column=1, row=4, padx=3, pady=10, sticky=E)
        default_pwd = tkinter.StringVar(value='1qazXSW@')    # 默认值
        self.password_entry = tkinter.Entry(param_frame, show="*", textvariable=default_pwd)
        self.password_entry.grid(column=2, row=4, columnspan=1)
        # 更多
        link1 = tkinter.Label(param_frame, text="更 多", bg="green", fg='blue', cursor="hand2")
        link1.grid(column=1, row=5, columnspan=1, pady=20)
        link1.bind("<Button-1>", self.show_more)
        # 运行按钮
        self.run_button = tkinter.Button(param_frame, text="运 行", fg="blue", command=self.start_test)
        self.run_button.grid(column=2, row=5, columnspan=1, pady=20)

        # 日志输出
        log_frame = tkinter.Frame(body_frame)
        log_frame.grid(column=1, row=0, sticky=W+S+N+E)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=10)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_propagate(1)
        log_header_frame = tkinter.Frame(log_frame)
        log_header_frame.grid(column=0, row=0, sticky=W)
        # 日志文件路径
        log_path_label = tkinter.Label(log_header_frame, text="日志文件路径: ")
        log_path_label.grid(column=0, row=0, padx=3, sticky=W)
        self.log_path_entry = tkinter.Entry(log_header_frame)
        self.log_path_entry.grid(column=1, row=0, pady=10, columnspan=1, sticky=W)
        # 自动刷新
        self.auto_refresh = tkinter.BooleanVar()
        refresh_button = tkinter.Checkbutton(log_header_frame, text='自动刷新', variable=self.auto_refresh,
                                             onvalue=True, offvalue=False, command=self.auto_fresh)
        refresh_button.grid(column=2, row=0, sticky=W)
        # 清空日志
        clear_button = tkinter.Button(log_header_frame, text="清空", command=self.clear_log)
        clear_button.grid(column=3, row=0, sticky=W)

        # 将Text控件添加进Frame控件
        self.log_text = tkinter.Text(log_frame, relief='sunken')
        self.log_text.grid(row=1, column=0, sticky=W+S+N+E, padx=(5, 5), pady=10)
        self.log_text.config(state=DISABLED)        # 设置只读
        # 设置y轴的滚动条，并将滚动条与text控件联动
        yscrollbar = tkinter.Scrollbar(log_frame)
        yscrollbar.grid(row=1, column=1, pady=10, sticky=N+S)
        yscrollbar.config(command=self.log_text.yview)
        self.log_text.config(yscrollcommand=yscrollbar.set)

    def layout_text_content(self):

        self.content_text_frame.grid_columnconfigure(0, weight=15)
        self.content_text_frame.grid_columnconfigure(1, weight=1)
        self.content_text_frame.grid_rowconfigure(0, weight=1)
        self.content_text_frame.grid_rowconfigure(1, weight=10)
        self.content_text_frame.grid_rowconfigure(2, weight=1)

        # 顶部展示文件名
        _file_name = tkinter.StringVar()
        _file_name.set(self.file_name)
        self.filename_label = tkinter.Label(self.content_text_frame, textvariable=_file_name)
        self.filename_label.grid(row=0, column=0, pady=2, sticky=W+E)

        # 布置内容展示文本和滚动条
        self.content_text = tkinter.Text(self.content_text_frame, relief='sunken', borderwidth=5)
        self.content_text.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)  # 加上columnspan后宽度扩展

        # 设置y轴的滚动条，并将滚动条与text控件联动
        yscrollbar = tkinter.Scrollbar(self.content_text_frame)
        yscrollbar.grid(row=1, column=2, sticky=N+S+E+W)
        yscrollbar.config(command=self.content_text.yview)
        self.content_text.config(yscrollcommand=yscrollbar.set)
        self.content_text.config(state=DISABLED)  # 设置只读

        # 设置x轴的滚动条，并将滚动条与text控件联动
        xscrollbar = ttk.Scrollbar(self.content_text_frame, orient='horizontal')
        xscrollbar.grid(row=2, column=0, columnspan=2, sticky=N+S+E+W)
        xscrollbar.config(command=self.content_text.xview)
        self.content_text.config(xscrollcommand=xscrollbar.set)
        self.content_text.config(wrap=NONE)  # 不自动换行

    def layout_table_content(self, cols=None):

        self.content_table_frame.grid_columnconfigure(0, weight=1)
        self.content_table_frame.grid_columnconfigure(1, weight=15)
        self.content_table_frame.grid_columnconfigure(2, weight=1)
        self.content_table_frame.grid_rowconfigure(0, weight=1)
        self.content_table_frame.grid_rowconfigure(1, weight=10)
        self.content_table_frame.grid_rowconfigure(2, weight=1)
        self.content_table_frame.grid_propagate(1)
        # index_frame = tkinter.Frame(self.content_table_frame, borderwidth=0, bg='yellow')
        # table_frame = tkinter.Frame(self.content_table_frame, borderwidth=0, bg='green')
        # index_frame.grid(row=0, column=0, pady=2, sticky=N+S+E+W)
        # table_frame.grid(row=0, column=1, pady=2, sticky=N+S+E+W)
        #
        # # 左侧加入序号列
        # index = [i for i in range(1, row_num)]
        # print(index)
        # # tkinter.Label(index_frame, text='', height=5).grid(row=0, column=0)
        # # tkinter.Label(index_frame, text='序号', bg='red', height=5).grid(row=1, column=0)
        # # for index_col in index:
        # #     index_label = tkinter.Label(index_frame, textvariable=str(index_col), height=10)
        # #     index_label.grid(row=index_col, column=0)
        #
        # tkinter.Label(index_frame, text='', height=1).pack(side=TOP, fill=X, expand=0)
        # tkinter.Label(index_frame, text='序号').pack(side=TOP, fill=X, expand=0)
        # for index_col in index:
        #     _index = tkinter.StringVar()
        #     _index.set(index_col)
        #     index_label = tkinter.Label(index_frame, textvariable=_index, height=2)
        #     index_label.pack(side=TOP, fill=X, expand=0)

        # 顶部展示文件名
        _file_name = tkinter.StringVar()
        _file_name.set(self.file_name)
        self.filename_label = tkinter.Label(self.content_table_frame, textvariable=_file_name)
        self.filename_label.grid(row=0, column=2, sticky=W+E)

        # 布置内容展示表格和滚动条
        table_columns = cols
        style = ttk.Style()
        # style.theme_use('clam')
        style.configure('Table.Treeview.Heading', font=('宋体', 12), relief='sunken')
        style.configure('Table.Treeview', rowheight=40)
        self.content_table = ttk.Treeview(self.content_table_frame,
                                          columns=table_columns,
                                          height=10,    # 要显示的行数
                                          show='headings',
                                          style='Table.Treeview')
        for col in table_columns:
            self.content_table.heading(col, text=col)
            self.content_table.column(col, minwidth=0, anchor=CENTER, stretch=True)     # stretch列的宽度是否随整个部件的改动而变化
        self.content_table.grid(row=1, column=2, columnspan=2, sticky=N+S+E+W)

        # 设置y轴的滚动条，并将滚动条与treeview控件联动
        yscrollbar = ttk.Scrollbar(self.content_table_frame, orient='vertical', command=self.content_table.yview())
        yscrollbar.config(command=self.content_table.yview)
        yscrollbar.grid(row=1, column=4, sticky=N+S)
        self.content_table.config(yscrollcommand=yscrollbar.set)

        # 设置x轴的滚动条，并将滚动条与treeview控件联动
        xscrollbar = ttk.Scrollbar(self.content_table_frame, orient='horizontal', command=self.content_table.xview())
        xscrollbar.config(command=self.content_table.xview)
        xscrollbar.grid(row=2, column=2, sticky=W+E)
        self.content_table.config(xscrollcommand=xscrollbar.set)

    def show_more(self, *args):
        self.child_win = ChildWindow(self.tk)
        self.child_win.create_child_main()

    def show_result(self, *args):
        result_data = gbl.service.get("Result")
        if result_data is not None:
            result_win = ResultWindow(self.tk)
            log.info("获取表格数据，{}行 {}列".format(len(result_data), len(result_data[0])))
            table_column = result_data[0]  # 默认第一行为列名
            result_win.create_result_view(table_column)  # 根据实际数据初始化表格
            row_num = 1
            for row in result_data[1:]:
                result_win.result_table.insert('', 'end', value=row)
                row_num += 1
            self.run_button.configure(state='normal')
            gbl.service.set("Result", None)
        else:
            self.run_button.configure(state='disabled')
            self.tk.after(5000, self.show_result)

    def choose_app(self, *args):
        self.application = self.app_combobox.get()
        log.info("应用: {}".format(self.application))

    def choose_env(self, *args):
        self.environment = self.env_combobox.get()
        log.info("环境: {}".format(self.environment))

    def param_check_ok(self, *args):
        message = ""
        if self.app_combobox.get() is None:
            message = "请选择应用"
        elif self.env_combobox.get() is None:
            message = "请选择系统"

        if message:
            tkinter.messagebox.showwarning('警告', message)
            necessary_param_ok = False
        else:
            self.application = self.app_combobox.get()
            self.environment = self.env_combobox.get()
            necessary_param_ok = True
        return necessary_param_ok

    def select_file(self):
        selected_file_path = filedialog.askopenfilename()
        if selected_file_path:
            self.select_path.set(selected_file_path)
        else:
            self.select_path.set(self.view_file_path)
        self.view_file_path = selected_file_path
        self.filename_label['text'] = selected_file_path

    @staticmethod
    def write_text(master, content):
        master.config(state=NORMAL)  # Text可编辑
        master.delete('1.0', 'end')
        master.insert(INSERT, content)
        master.config(state=DISABLED)  # Text只读

    def auto_fresh(self, *args):
        if self.auto_refresh.get():
            self.reload_thread = threading.Thread(target=self.reload_log, args=(self.log_path_entry.get(), 1, 1000))
            # self.reload_thread = threading.Thread(target=self.reload_log2, args=(self.log_path_entry.get(), 10, 3))
            self.reload_thread.setDaemon(True)
            self.reload_thread.start()
            log.info("开启日志自动刷新，线程id: {}".format(self.reload_thread.ident))
        else:
            stop_thread(self.reload_thread)
            log.info("关闭日志自动刷新")

    def clear_log(self, *args):
        self.log_text.config(state=NORMAL)  # Text可编辑
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state=DISABLED)  # Text只读

    def reload_log(self, log_path, interval=5, buffer_size=1000):
        try:
            file_content = ""
            first_line = True
            with open(log_path, 'r', encoding='utf8') as f:
                while True:
                    current_content = f.read(buffer_size)        # 一次读取字符数
                    # if len(current_content) == 0:
                    #     self.auto_refresh.set(False)
                    #     stop_thread(self.reload_thread)     # 停止刷新页面
                    #     break
                    if not file_content and first_line:
                        file_content = str(current_content)
                        first_line = False
                    else:
                        file_content += current_content
                    self.write_text(self.log_text, file_content)
                    self.log_text.see(END)  # 展示末尾
                    sleep(interval)
        except FileNotFoundError as e:
            file_content = "日志文件不存在, {}".format(str(e))
            self.write_text(self.log_text, file_content)
            self.log_text.see(END)  # 展示末尾
            self.auto_refresh.set(False)
            stop_thread(self.reload_thread)  # 停止刷新页面

    def quit(self):
        # 退出按钮
        self.tk.destroy()

    def show_file(self):
        """
        页面默认展示文本框，当文件路径为空、文本格式文件、无后缀文件时，展示文本，否则展示表格
        """
        # 重新获取选择文件框内容
        selected_file_path = self.file_entry.get()
        log.info("文件路径: {}".format(selected_file_path))

        # 更新顶部文件名
        if selected_file_path:
            self.file_name = selected_file_path.split("/")[-1]
            self.display_content_text()
        else:
            self.file_name = ""     # 设置为None无法更新text
            self.display_content_text()
            self.content_text.delete('1.0', 'end')
            file_content = "请先选择文件再预览！"
            self.write_text(self.content_text, file_content)
            return

        # 判断文件类型
        if self.file_name.find(".") == -1:
            show_type = "text"
        else:
            file_suffix = self.file_name.split(".")[-1]
            if file_suffix in ['xls', 'xlsx']:
                show_type = "table"
            else:
                show_type = "text"

        # 根据文件类型选择不同的展示方式，文本或表格
        file_content = read_file(selected_file_path)
        if show_type == "text":  # 文本
            self.display_content_text()
            self.write_text(self.content_text, file_content)
        else:  # 表格
            # if isinstance(file_content, list):
            #     table_data = read_file(selected_file_path)
            #     log.info("获取表格数据，{}行 {}列".format(len(table_data), len(table_data[0])))
            #     self.display_ui_table(table_data)
            if isinstance(file_content, list):
                table_data = read_file(selected_file_path)
                log.info("获取表格数据，{}行 {}列".format(len(table_data), len(table_data[0])))
                table_column = table_data[0]    # 默认第一行为列名
                table_column.insert(0, '序号')
                self.display_content_table(table_column)      # 根据实际数据初始化表格
                row_num = 1
                for row in table_data[1:]:
                    row.insert(0, row_num)
                    self.content_table.insert('', 'end', value=row)
                    row_num += 1
            else:
                self.display_content_text()
                self.write_text(self.content_text, file_content)

    @staticmethod
    def run_api():
        if not gbl.service.get("ApiRun"):
            from src.main.interface.routes import app
            app.run(host='0.0.0.0', port=8098, debug=True, use_reloader=False)
            gbl.service.set("ApiRun", True)

    def start_test(self):

        # 必选参数检查
        if not self.param_check_ok():
            return

        file_begin = self.file_begin_entry.get()
        case_begin = self.case_begin_entry.get()
        # log_path = self.log_path_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        param = {
            "application": self.application,
            "environment": self.environment,
            "file_begin": file_begin,
            # "log_path": log_path,
            "case_begin": case_begin,
            "username": username,
            "password": password,
            "callback_url": gbl.service.get("callbackUrl")
        }
        log.info(param)
        if self.child_win:
            thread1 = threading.Thread(target=request_server, args=(param, self.child_win.files))
        else:
            thread1 = threading.Thread(target=request_server, args=(param,))
        thread2 = threading.Thread(target=self.run_api, args=())
        thread1.setDaemon(True)
        thread2.setDaemon(True)
        thread1.start()     # 启用线程请求测试
        thread2.start()     # 启用线程开启flask接口，用于接收测试结果
        # thread1.join()
        # thread2.join()
        log.info("开启请求测试，线程id: {}".format(thread1.ident))
        log.info("开启api接口，线程id: {}".format(thread2.ident))
        if gbl.service.get("Result") is None:
            self.run_button.configure(state='disabled')
        self.tk.after(5000, self.show_result)


if __name__ == "__main__":
    # 加载配置文件
    config.load_properties()
    app = Application()
    app.create_main_page()
    app.tk.mainloop()
