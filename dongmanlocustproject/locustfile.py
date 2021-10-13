import json
import logging
import math
import time
from datetime import datetime
from collections import namedtuple

import yaml
from locust import FastHttpUser, task, between, tag, events, LoadTestShape
from locust.runners import MasterRunner, WorkerRunner

import getkey


@events.quitting.add_listener
def _(environment, **kw):
    if environment.stats.total.fail_ratio > 0.01:
        logging.error("Test failed due to failure ratio > 1%")
        environment.process_exit_code = 1
    elif environment.stats.total.avg_response_time > 200:
        logging.error("Test failed due to average response time ratio > 200 ms")
        environment.process_exit_code = 1
    elif environment.stats.total.get_response_time_percentile(0.95) > 800:
        logging.error("Test failed due to 95th percentile response time > 800 ms")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0


# Fired when the worker receives a message of type 'test_users'
def setup_test_users(environment, msg, **kwargs):
    for user in msg.data:
        print(f"User {user['name']} received")
    environment.runner.send_message('acknowledge_users', f"Thanks for the {len(msg.data)} users!")


# Fired when the master receives a message of type 'acknowledge_users'
def on_acknowledge(msg, **kwargs):
    print(msg.data)


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):
        print("I'm on master node")
    else:
        print("I'm on a worker or standalone node")
    if not isinstance(environment.runner, MasterRunner):
        environment.runner.register_message('test_users', setup_test_users)
    if not isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message('acknowledge_users', on_acknowledge)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("开启测试")
    if not isinstance(environment.runner, MasterRunner):
        users = [
            {"name": "User1"},
            {"name": "User2"},
            {"name": "User3"},
        ]
        environment.runner.send_message('test_users', users)


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
            assert r.status_code == 200
        wait_time = between(1, 10)

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
#     host = "https://qaapis.dongmanmanhua.cn"
#
#     @tag('tag1')
#     @task
#     def test_new(self):
#         message = "/app/episode/list/v4?expires=1634972054459&language=zh-hans&locale=zh_CN&md5=EQAb0BWn7ohgVq" \
#                   "-B_EGz4w&pageSize=214&platform=APP_IPHONE&serviceZone=CHINA&startIndex=0&titleNo=735&v=8 "
#         r = self.client.get(message)
#         print(r.status_code)
#         wait_time = between(1, 5)
#
#     @tag('tag2')
#     @task
#     def test_card4(self):
#         for title_name in yaml.safe_load(open("../dongmanlocustproject/title_name.yml")):
#             message = f"/app/home/card4?expires=1634028869836&language=zh-hans&locale=zh_CN" \
#                       f"&md5=AiUM4xmOUDt5H4YmIdPAWA&platform=APP_IPHONE&serviceZone=CHINA&sortOrder=UPDATE&" \
#                       f"weekday={title_name}&bannerImageType=Default"
#             r = self.client.get(message)
#             assert r.status_code == 200
#         wait_time = between(1, 5)


# class MyCustomShape(LoadTestShape):
#     # time_limit设置时限整个压测过程为60秒
#     time_limit = 600
#     # 设置产生率一次启动10个用户
#     spawn_rate = 1
#
#     def tick(self):
#         """
#         设置 tick()函数
#         并在tick()里面调用 get_run_time()方法
#         """
#         # 调用get_run_time()方法获取压测执行的时间
#         run_time = self.get_run_time()
#         # 运行时间在 time_limit之内，则继续执行
#         if run_time < self.time_limit:
#             # user_count计算每10秒钟增加10个
#             user_count = round(run_time, -1)
#             print(str(user_count) + ">>>>>" + datetime.now().strftime('%Y-%m-%d-%H:%M:%S.%f'))
#             return user_count, self.spawn_rate
#         return None


# class DoubleWave(LoadTestShape):
#     """
#     A shape to immitate some specific user behaviour. In this example, midday
#     and evening meal times. First peak of users appear at time_limit/3 and
#     second peak appears at 2*time_limit/3
#     Settings:
#         min_users -- minimum users
#         peak_one_users -- users in first peak
#         peak_two_users -- users in second peak
#         time_limit -- total length of test
#     """
#
#     min_users = 20
#     peak_one_users = 40
#     peak_two_users = 20
#     time_limit = 60
#
#     def tick(self):
#         run_time = round(self.get_run_time())
#
#         if run_time < self.time_limit:
#             user_count = (
#                     (self.peak_one_users - self.min_users)
#                     * math.e ** -(((run_time / (self.time_limit / 10 * 2 / 3)) - 5) ** 2)
#                     + (self.peak_two_users - self.min_users)
#                     * math.e ** -(((run_time / (self.time_limit / 10 * 2 / 3)) - 10) ** 2)
#                     + self.min_users
#             )
#             return round(user_count), round(user_count)
#         else:
#             return None

# class StagesShape(LoadTestShape):
#     """
#     A simply load test shape class that has different user and spawn_rate at
#     different stages.
#     Keyword arguments:
#         stages -- A list of dicts, each representing a stage with the following keys:
#             duration -- When this many seconds pass the test is advanced to the next stage
#             users -- Total user count
#             spawn_rate -- Number of users to start/stop per second
#             stop -- A boolean that can stop that test at a specific stage
#         stop_at_end -- Can be set to stop once all stages have run.
#     """
#
#     stages = [
#         {"duration": 60, "users": 10, "spawn_rate": 10},
#         {"duration": 100, "users": 50, "spawn_rate": 10},
#         {"duration": 180, "users": 100, "spawn_rate": 10},
#         {"duration": 220, "users": 30, "spawn_rate": 10},
#         {"duration": 230, "users": 10, "spawn_rate": 10},
#         {"duration": 240, "users": 1, "spawn_rate": 1},
#     ]
#
#     def tick(self):
#         run_time = self.get_run_time()
#
#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 tick_data = (stage["users"], stage["spawn_rate"])
#                 return tick_data
#
#         return None

# class StepLoadShape(LoadTestShape):
#     """
#     A step load shape
#     Keyword arguments:
#         step_time -- Time between steps
#         step_load -- User increase amount at each step
#         spawn_rate -- Users to stop/start per second at every step
#         time_limit -- Time limit in seconds
#     """
#
#     step_time = 3
#     step_load = 1
#     spawn_rate = 1
#     time_limit = 60
#
#     def tick(self):
#         run_time = self.get_run_time()
#
#         if run_time > self.time_limit:
#             return None
#
#         current_step = math.floor(run_time / self.step_time) + 1
#         return current_step * self.step_load, self.spawn_rate

Step = namedtuple("Step", ["users", "dwell"])


class StepLoadShape(LoadTestShape):
    """
    A step load shape that waits until the target user count has
    been reached before waiting on a per-step timer.
    The purpose here is to ensure that a target number of users is always reached,
    regardless of how slow the user spawn rate is. The dwell time is there to
    observe the steady state at that number of users.
    Keyword arguments:
        targets_with_times -- iterable of 2-tuples, with the desired user count first,
            and the dwell (hold) time with that user count second
    """

    targets_with_times = (Step(5, 10), Step(10, 10), Step(20, 10), Step(30, 10), Step(40, 10), Step(50, 20),
                          Step(40, 10), Step(30, 10), Step(20, 10), Step(10, 10), Step(5, 10))

    def __init__(self, *args, **kwargs):
        self.step = 0
        self.time_active = False
        super(StepLoadShape, self).__init__(*args, **kwargs)

    def tick(self):
        if self.step >= len(self.targets_with_times):
            return None

        target = self.targets_with_times[self.step]
        users = self.get_current_user_count()

        if target.users == users:
            if not self.time_active:
                self.reset_time()
                self.time_active = True
            run_time = self.get_run_time()
            if run_time > target.dwell:
                self.step += 1
                self.time_active = False

        # Spawn rate is the second value here. It is not relevant because we are
        # rate-limited by the User init rate.  We set it arbitrarily high, which
        # means "spawn as fast as you can"
        return target.users, 100
