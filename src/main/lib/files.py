# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/2/14 下午5:15

import xlrd
import csv
from openpyxl import load_workbook


def read_file(file_name):
    # 判断文件类型
    if file_name.find(".") == -1:
        file_type = "txt"
    else:
        file_suffix = file_name.split(".")[-1]
        if file_suffix in ['xls']:
            file_type = "xls"
        elif file_suffix in ['xlsx']:
            file_type = "xlsx"
        elif file_suffix in ['csv']:
            file_type = "csv"
        else:
            file_type = "txt"

    if file_type == "txt":
        file_content = ""
        first_line = True
        try:
            with open(file_name, 'r', encoding='utf8') as f:
                for line in f.readlines():
                    if not file_content and first_line:
                        file_content = line
                        first_line = False
                    else:
                        file_content = file_content + line
        except FileNotFoundError as e:
            file_content = "文件不存在, {}".format(str(e))
    elif file_type == "xls":
        file_content = []
        try:
            rbook = xlrd.open_workbook(file_name, formatting_info=True)
            sheet1 = rbook.sheet_by_index(0)
            for rows in range(sheet1.nrows):
                file_content.append(sheet1.row_values(rows))
        except FileNotFoundError as e:
            file_content = "文件不存在, {}".format(str(e))
    elif file_type == "csv":
        file_content = ""
        first_line = True
        try:
            with open(file_name, 'r', encoding='gbk') as f:
                for line in csv.reader(f, skipinitialspace=True):
                    if not file_content and first_line:
                        file_content = str(line)
                        first_line = False
                    else:
                        file_content = file_content + '\n' + str(line)
        except FileNotFoundError as e:
            file_content = "文件不存在, {}".format(str(e))
    else:
        file_content = []
        try:
            wb = load_workbook(file_name)
            sheet1 = wb.worksheets[0]
            rows = 0
            for row in sheet1.rows:
                row_data = [col.value for col in row]
                file_content.append(row_data)
                rows += 1
        except FileNotFoundError as e:
            file_content = "文件不存在, {}".format(str(e))
    return file_content
