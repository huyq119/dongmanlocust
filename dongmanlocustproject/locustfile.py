import json
import time

import yaml
from locust import FastHttpUser, task, between, tag, events
from locust.runners import MasterRunner

import getkey


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):
        print("I'm on master node")
    else:
        print("I'm on a worker or standalone node")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("开启测试")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("终止测试")


def get_body(neo_id):
    time_ten = int(time.time())
    time_thirteen = int(round(time.time() * 1000))
    dic_body = {'event': {'name': 'ShowRecommendLocation', 'value': [{'bhv_time': '%d' % time_ten, 'bhv_value': '1',
                                                                      'title_No': '0'}]},
                'userBehaviorInfo': {'app_version': '2.6.8_0830', 'device_model': 'MI', 'platform': 'android',
                                     'report_src': '2', 'user_id': '%s' % neo_id},
                'timestamp': '%d' % time_thirteen}
    js_body = json.dumps(dic_body)
    pub_key = "aKSqMq9ZdCDoMAgG"
    body = getkey.encrypt(key=pub_key, content=js_body)
    return body


class RecommendPost(FastHttpUser):
    host = "https://qarec.dongmanmanhua.cn"

    @tag('tag1')
    @task
    def reporting_request_one(self):
        id_list = yaml.safe_load(open("../dongmanlocustproject/neoid.yml"))
        message = "/airec/behavior/data/reporting"
        for neo_id in id_list:
            body_content = get_body(neo_id)
            r = self.client.post(message, json=body_content)
            # print(r.text)
            print("Response status code:", r.status_code)
        wait_time = between(0.5, 10)

    @tag('tag2')
    @task
    def reporting_request_two(self):
        id_list = yaml.safe_load(open("../dongmanlocustproject/neoid.yml"))
        message = "/airec/behavior/data/reporting"
        for neo_id in id_list:
            body_content = get_body(neo_id)
            r = self.client.post(message, json=body_content)
        wait_time = between(0.5, 10)

# class EpisodeList(FastHttpUser):
#     host = "http://qaapis.dongmanmanhua.cn"
#
#     @task
#     def test_new(self):
#         message = "/app/episode/list/v4?expires=1634972054459&language=zh-hans&locale=zh_CN&md5=EQAb0BWn7ohgVq" \
#                   "-B_EGz4w&pageSize=214&platform=APP_IPHONE&serviceZone=CHINA&startIndex=0&titleNo=735&v=8 "
#         r = self.client.get(message)
#         print(r.status_code)
#         wait_time = between(1, 5)