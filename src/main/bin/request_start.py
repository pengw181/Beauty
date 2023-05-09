# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/2/8 下午6:38

import requests
from src.main.lib.globals import gbl
from src.main.lib.logger import log


def request_server(param, files=None):
    url = gbl.service.get("httpUrl")

    data = {
        "application": param.get("application"),
        "environment": param.get("environment"),
        "begin_file": param.get("file_begin"),
        "begin_case": param.get("case_begin"),
        "username": param.get("username"),
        "password": param.get("password"),
        "callback_url": param.get("callback_url")
    }
    if files:
        req_files = []
        for file_name, file_content in files.items():
            req_files.append(("file", (file_name, file_content.encode(), "application/octet-stream")))
        response = requests.post(url, data=data, files=req_files, verify=False, timeout=60)
    else:
        response = requests.post(url, data=data, verify=False, timeout=60)
    log.info(response.json())
    test_result_dict = response.json().get("data")
    return test_result_dict
