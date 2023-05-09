# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2023/2/23 下午5:55

import flask
from werkzeug.routing import BaseConverter
from src.main.lib.globals import gbl
from src.main.lib.logger import log


app = flask.Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


@app.route('/http/web-test/result', methods=['POST'])
def async_result():
    log.info("收到异步返回测试结果")
    log.info("request method: {}".format(flask.request.method))
    log.info("mimetype: {}".format(flask.request.mimetype))
    log.info("data: {}".format(flask.request.get_json()))

    result_list = flask.request.get_json().get("result")
    result_data = [['用例文件名', '成功数', '失败数', '跳过数']]
    for result in result_list:
        for key, value in result.items():
            result_data.append([key, value.get("pass_num"), value.get("fail_num"), value.get("skip_num")])
    log.info(result_data)
    gbl.service.set("Result", result_data)

    return flask.jsonify({"success": True})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8098, debug=True)
