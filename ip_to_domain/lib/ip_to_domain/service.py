from sanic import Sanic
from sanic.response import json as sjson
import configparser
import traceback
import logging
from cloghandler import ConcurrentRotatingFileHandler
from retrying import retry
import asyncio
import uvloop
import multiprocessing
from multiprocessing import Process
# from pathos.multiprocessing import ProcessingPool as Pool  # 多进程
from multiprocessing import Pool as POOL  # 多进程
from multiprocessing.dummy import Pool as ThreadPool  # 多线程
import signal
import json
import requests
import time
import kafka
import redis
import os
import sys
from functools import partial
import redis


# 设置事件循环策略 使得asyncio.get_event_loop() 返回一个 uvloop 实例
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


# 定义全局变量
KAFKA_IP='127.0.0.1'
KAFKA_PORT=9092

SERVICE_IP = '127.0.0.1'
SERVICE_PORT = 3000
SERVICE_META = {}

HEALTHCHECK_PATH = '/health'
HEALTHCHECK_ARGS = {}

REGISTER_URL = 'https://result.eolinker.com/BuQt7kT3de7f2186783e1777a29045300b7b9b29cc0a49c?uri=/executor/register'

FINISHED_URL = 'http://mock.eolinker.com/BuQt7kT3de7f2186783e1777a29045300b7b9b29cc0a49c?uri=/worker'
RECEIVED_URL = 'http://mock.eolinker.com/BuQt7kT3de7f2186783e1777a29045300b7b9b29cc0a49c?uri=/worker'

REDIS_IP = '127.0.0.1'
REDIS_PORT = 6379

RETRY_TIMES = 3
RETRY_TIME_UNIT = 1000

# 用户在初始化时给定了参数则使用用户定义的
# 没定义则从环境变量中获取
# 环境变量中没有则使用系统默认的

class Service(object):
    def __init__(self, service_type, service_name, **kwargs):
        '''
        Start the service with some configs,service_type and service_name are essential
        :param service_type{string}: the type of service
        :param service_name{string}: the name of service
        :param **kwargs(option){map}: other configs in {'service_ip','kafka_ip','kafka_port,'service_port','service_meta',
                         'healthcheck_args','healthcheck_path','register_url','received_url','finished_url',
                         'redis_ip','redis_port'}
        '''
        try:
            self.kw = kwargs
            self.app = Sanic()
            # 获取调用该库所在代码的位置
            current_dir = os.path.abspath(sys.argv[0])
            self.xd_dir = current_dir[0:current_dir.rfind('/')+1]

            # 日志输出 将级别为warning的输出到控制台，级别为debug及以上的输出到log.txt文件中
            logger = logging.getLogger('Service')
            logger.setLevel(logging.DEBUG)
            # 文件名，写入模式（a表示追加），文件大小（2M），最多保存5个文件
            # ConcurrentRotatingFileHandle能解决多进程日志的文件写入问题
            file_handle = ConcurrentRotatingFileHandler(
                self.xd_dir+"log.txt",  "a", 2*1024*1024, 5)
            cmd_handle = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s")
            file_handle.setFormatter(formatter)
            cmd_handle.setFormatter(formatter)
            logger.addHandler(file_handle)
            logger.addHandler(cmd_handle)
            self.logger = logger

            # 重试的次数和单位时间间隔
            self.retry_times = 3
            self.retry_time_unit = 1000  # ms

            self.service_name = service_name
            self.service_type = service_type

            # 初始化系统的变量
            self._init_variables()

            self.kafka_cluster=[]
            self.kafka_cluster.append(str(self.kafka_ip)+':'+str(self.kafka_port))

            # 构造注册函数请求体
            self.server_register_parameter = {
                "name": self.service_name,
                "type": self.service_type,
                "address": self.service_ip,
                "port": int(self.service_port),
                "meta": {
                    "version":"1.0"
                },
                "check": {
                    "path": self.healthcheck_path
                }
            }

            # 定义数据处理的钩子函数
            self._process_deal_func = None
            self._handle_input_item = None
            self._handle_input_items = None

            # 健康检查的钩子函数
            self._health_check = None

            # 保持一个redis连接
            self.redis_handle = redis.Redis(
                host=self.redis_ip, port=self.redis_port,decode_responses=True)
            
            #依据传入的名称获取定义的处理函数
            self.name_map={
                "default": self.to_next_default,
            }

        except Exception:
            self.logger.info(
                "Errors occured in the process of initializing:  "+traceback.format_exc())
            raise

    def _init_variables(self):
        '''
        Init the config
        '''
        self.kafka_ip = self._get_config(
            config_name='kafka_ip', in_user_name='kafka_ip', in_enviorment_name='KAFKA_IP', in_defalut_name=KAFKA_IP)
        self.kafka_port = self._get_config(
            config_name='kafka_port', in_user_name='kafka_port', in_enviorment_name='KAFKA_PORT', in_defalut_name=KAFKA_PORT)
        self.service_ip = self._get_config(
            'service_ip', 'service_ip', 'SERVICE_IP', SERVICE_IP)
        self.service_port = self._get_config(
            'service_port', 'service_port', 'SERVICE_PORT', SERVICE_PORT)
        self.service_meta = self._get_config(
            'service_meta', 'service_meta', 'SERVICE_META', SERVICE_META)
        self.healthcheck_args = self._get_config(
            'healthcheck_args', 'healthcheck_args', 'HEALTHCHECK_ARGS', HEALTHCHECK_ARGS)
        self.healthcheck_path = self._get_config(
            'healthcheck_path', 'healthcheck_path', 'HEALTHCHECK_PATH', HEALTHCHECK_PATH)
        self.register_url = self._get_config(
            'register_url', 'register_url', 'REGISTER_URL', REGISTER_URL)
        self.finished_url = self._get_config(
            'finished_url', 'finished_url', 'FINISHED_URL', FINISHED_URL)
        self.received_url = self._get_config(
            'received_url', 'received_url', 'RECEIVED_URL', RECEIVED_URL)
        self.redis_ip = self._get_config(
            'redis_ip', 'redis_ip', 'REDIS_IP', REDIS_IP)
        self.redis_port = self._get_config(
            'redis_port', 'redis_port', 'REDIS_PORT', REDIS_PORT)

        self.logger.info("Init the variables successfully!")

    # 依次从用户配置、环境变量和系统默认配置中获取配置
    def _get_config(self, config_name, in_user_name, in_enviorment_name, in_defalut_name):
        '''
        Get config of the service from user and enviorment in order or setting the config in default
        :param config_name{string}: the name of config such as 'kafka_cluster'、'service_ip'、'service_port' and so on
        :param in_user_name{string}: the name of config for user setting
        :param in_enviorment_name{string}: the name of config in enviorment
        :param in_defalut_name{string}: the name of config in default config
        :return: return the config
        '''
        if in_user_name in self.kw:
            temp_config = self.kw[in_user_name]
            self.logger.info("Use the config of " +
                             config_name+" in the input of user")
        elif in_enviorment_name in os.environ and len(os.environ[in_enviorment_name]):
            temp_config = os.environ[in_enviorment_name]
            self.logger.info("Use the config of "+config_name+" in enviorment")
        else:
            temp_config = in_defalut_name
            self.logger.info("Use the config of "+config_name +
                             " in the config of default")
        return temp_config

    def _update_variables(self):
        '''
        Update variables from enviorment
        '''
        if 'finished_url' in os.environ and len(os.environ['finished_url']):
            self.finished_url = os.environ['finished_url']
            self.logger.info("Update finished_url from enviorment")
        if 'received_url' in os.environ and len(os.environ['received_url']):
            self.received_url = os.environ['received_url']
            self.logger.info("Update received_url from enviorment")

    #获取用户定义的对输出数据进行处理的函数名
    def to_next(self,name="default"):
        '''
        The function for handling data which is defined by user
        :param name(optional){string}: the name of the function of handling outputs
        '''
        def wrapper(func):
            if name!= "default":
                self.name_map[name]=func
        return wrapper
    
    #处于中间或者默认的输出数据处理
    def to_next_default(self,pre_data):
        '''
        Making the data to type that the next topic need
        :param pre_data(optional){string}: data need to be dealt
        '''
        return pre_data["output"]
    
    # 使用策略处理单条输入数据

    def handle_input_item(self, strategy=None, pool_size=4, time_out=3):
        '''
        Change the function of user for handling single data to the funtion of the class
        :param strategy(optional){string}: eventlet、thread for handle the list of data
        :param pool_size(optional){int}: the size of thread pool
        :param time_out(optional){float}: the max seconds for waiting the result of the function
        '''
        def wrapper(func):
            self._handle_input_item = func
            # 获取用户对框架的配置
            self.pool_size = pool_size
            self.strategy = strategy
            self.time_out = time_out
        return wrapper

    # 自定义策略处理输入数据
    def handle_input_items(self, time_out=4):
        '''
        Change the function of user for handling the list of data to the funtion of the class
        :param time_out(optional){float}: the max seconds for waiting the result of the funtion
        '''
        def wrapper(func):
            self._handle_input_items = func
            self.mult_time_out = time_out
        return wrapper

    # 定义健康检查的处理函数
    def health_check(self):
        '''
        Change the function of user for checking health to the funtion of the class
        '''
        def wrapper(func):
            self._health_check = func
        return wrapper

    # , retry_on_result=_retry_on_false,

    @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT)
    def _send_message(self, mes, topic):
        '''
        Send the message to next topic
        :param mes{map}: the message need to be sent
        :param topic{string}: the topic of the message
        '''
        self.logger.info(mes)
        self.logger.info(type(mes))
        self.logger.info(topic)


        try:
            mesg = str(json.dumps(mes)).encode('utf-8')
            # mesg = json.dumps(mes)
            producer = kafka.KafkaProducer(
                bootstrap_servers=self.kafka_cluster)  #
            if producer:
                producer.send(topic, mesg)
                self.logger.info("Send the message to next topic successully!")
                producer.close()
        except Exception:
            self.logger.error(
                "Errors occured while sending message to next topic")
            if producer:
                producer.close()
            raise

    # 依据data_list 和 config
    # @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplie=RETRY_TIME_UNIT)
    def _handle_data_message(self, data_list, config):
        '''
        Handle the data of the messaeg using the function of user with different strategy
        :param data_list{list}: the data of message from kafka
        :param config{map}: the config for service
        :return: return the list of map in which showing the situation of handling each single data in data list
        '''

        self.logger.info("Begin to deal data_list with config")
        self.logger.info("Into the function of user")
        config_list = [config for n in range(len(data_list))]
        # 执行策略有："eventlet | thread | process"
        # 执行策略 先判别单个数据的处理是否存在，若存在则使用策略对单条数据处理
        # 若单条数据处理不存在则使用数据集处理函数
        # if self.strategy and self.time_out and self.pool_size:
        #     self.logger.info(str(self.strategy)+"  "+str(self.pool_size)+"   "+str(self.time_out))

        result_list = []

        # 构造传入的数据
        for item in data_list:
            temp_map = {
                "input": item,
                "output": None,
                "error_info": None
            }
            result_list.append(temp_map)

        # 对于没有设定运行策略，单条数据循环执行需要设置等待的时间
        # 不使用单条执行策略，调用用户的集中执行函数也需要设置等待时间
        # 如果接收到超时信号则会raise错误
        def handler(signum, frame):
            raise AssertionError

        # data_list 和 config_list 为两个参数列表
        # 对于单条数据处理的控制，池中的每个协程、线程、进程 等待若干时间没有返回结果就

        try:
            start_time = time.time()
            if self._handle_input_item == None:
                try:
                    signal.signal(signal.SIGALRM, handler)
                    signal.alarm(self.mult_time_out)
                    result_list = self._handle_input_items(result_list, config)
                    signal.alarm(0)
                except AssertionError:
                    for item in result_list:
                        item["error_info"] = "time_out"

            elif self.strategy == "eventlet":
                # 使用协程池 处理输入数据
                # asyncio uvloop
                loop = asyncio.get_event_loop()
                tasks = []
                for item in result_list:
                    coroutine = self._handle_input_item(item, config)
                    c_to_feature = asyncio.ensure_future(coroutine)
                    tasks.append(c_to_feature)
                loop.run_until_complete(asyncio.wait(
                    tasks, timeout=self.time_out*len(data_list)))

                temp_result_list = []

                for i in range(0, len(tasks)):
                    try:
                        temp_result = tasks[i].result()
                        temp_result_list.append(temp_result)
                    except asyncio.InvalidStateError:
                        single_result = {
                            "input": data_list[i],
                            "ouput": None,
                            "error_info": "time_out"
                        }
                        temp_result_list.append(single_result)
                result_list = temp_result_list

            elif self.strategy == "thread":
                # 将配置参数统一设置
                part_func = partial(self._handle_input_item, config=config)
                # 使用多线程来处理输入数据
                pool = ThreadPool(self.pool_size)

                results = []

                for item in result_list:
                    result = pool.apply_async(part_func, args=(item,))
                    results.append(result)

                temp_result_list = []

                for i in range(0, len(results)):
                    try:
                        res = results[i].get(timeout=self.time_out)
                        temp_result_list.append(res)
                    except multiprocessing.TimeoutError:
                        single_result = {
                            "input": data_list[i],
                            "output": None,
                            "error_info": "time_out"
                        }
                        temp_result_list.append(single_result)
                
                result_list = temp_result_list

                pool.close()
                pool.join()
            else:
                self.logger.info("No strategy")
                temp_result_list = []
                for i in range(0, len(result_list)):
                    try:
                        signal.signal(signal.SIGALRM, handler)
                        signal.alarm(self.time_out)
                        single_result= self._handle_input_item(result_list[i], config)
                        temp_result_list.append(single_result)
                        signal.alarm(0)
                    except AssertionError:
                        single_result = {
                            "input": data_list[i],
                            "output": None,
                            "error_info": 'time_out'
                        }
                        temp_result_list.append(single_result)
                result_list = temp_result_list

            end_time = time.time()

            self.logger.info("Time cost: "+str(end_time-start_time)+"s")
            self.logger.info("The result after handling:")
            self.logger.info(result_list)

            return result_list

        except Exception:
            self.logger.error(
                "Something wrong happened while handling the data_list:  "+traceback.format_exc())
            raise

    # 对消息的完整性进行检验
    def _message_check(self, message, message_type):
        '''
        Check the integrity of the message from kafka
        :param message{string}: the message from kafka
        :param message_type{int}: the type of the message,the message for controlling is not supported
        :return: if no error,return (True, "the message is right");else return (False, error information)
        '''

        if message_type == 1:
            try:
                if 'child_id' not in message:
                    return (False, "the child_id is missing")
                else:
                    childid = message.get('child_id', None)
                    if type(childid) != int:
                        return (False, "child_id must be int")

                if 'task_id' not in message:
                    return (False, "the task_id is missing")

                if 'data' not in message:
                    return (False, "the data missing")
                else:
                    data = message.get('data', None)
                    if type(data) != list:
                        return (False, "the data must be list")

                if 'output' not in message:
                    return (False, "the output is missing")
                else:
                    output = message.get('output', None)
                    if type(output) != dict:
                        return (False, "the output must be dict")
                    else:
                        if 'current_stage' not in output:
                            return (False, "the current_stage is missing")

                        if 'current_index' not in output:
                            return (False, "the current_index is missing")
                        else:
                            current_index = output['current_index']
                            if type(current_index) != int:
                                return (False, "the current_index must be int")

                        if 'depth' not in output:
                            return (False, "the depth is missing")
                        else:
                            depth = output['depth']
                            if type(depth) != int:
                                return (False, "the depth must be int")

                        if 'max_depth' not in output:
                            return (False, "the max_depth is missing")
                        else:
                            max_depth = output['max_depth']
                            if type(max_depth) != int:
                                return (False, "the max_depth must be int")

                        if 'stages' not in output:
                            return (False, "the stages is missing")
                        else:
                            stages = output['stages']
                            if type(stages) != dict:
                                return (False, "the stages must be dict")
                            else:
                                for key in stages.keys():
                                    if type(stages[key]) != dict:
                                        return (False, "stage in stages must be dict")
                                    else:
                                        temp = stages[key]

                                        if 'units' not in temp:
                                            return (False, "the units is missing")

                                        if 'next' not in temp:
                                            return (False, "the next is missing")

                return (True, "the message is right")

            except Exception as err:
                self.logger.error(
                    "Some errors occured in the message:   "+traceback.format_exc())
                return (False, "Some errors occured in checking the message")

        else:
            # 预留控制字段信息的检查
            return (False, "Control type is not support now")

    # @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplie=RETRY_TIME_UNIT)
    def _predeal_finished_message(self, message, info):
        '''
        Prepare the finished message need to be sent
        :param message{map}: the message fron kafka
        :param info{string}: the error informatinon after checking the message
        '''

        temp_taskid = message.get('task_id',None)
        temp_childid= message.get('child_id',-1)
        self.error_info={
            "framework":[info],
            "user":[]
        }
        self._send_finished_message(
            0, 0, temp_taskid, temp_childid, "finished")

    @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT)
    def _send_received_message(self, message):
        '''
        Send the information to controller after gaining message from kafka to make sure whether the child task need to be done
        :param message{map}: the message from kafka
        :return: if need to be done,return True;else return False
        '''

        temp_taskid = message.get('task_id',None)
        temp_childid= message.get('child_id',-1)

        send_message = {
            "type": "received",
            "worker_id": self.service_id,
            "worker_type": self.service_type,
            "task_id": temp_taskid,
            "child_id": temp_childid,
            "task_message": message
        }

        parametas = json.dumps(send_message)
        try:
            ret = requests.put(self.received_url, data=parametas, timeout=2)
            temp = ret.json()
            #dict也可以打印
            self.logger.info(temp)

            if not temp['state'] and temp['status'] == "running":
                self.logger.info("The task needs to be done")
                return True
            else:
                self.logger.info("Don't need to do the task")
                return False
        except Exception:
            self.logger.error(
                "Errors occored while sending received message:  "+traceback.format_exc())
            raise

    # 消息获取之后完整性检查及反馈消息的处理
    def _predeal_message(self, message):
        '''
        Send received message and check message after gaining message from kafka
        :param message{map}: the message from kafka
        '''
        try:
            self.logger.info("Sending message back to the controller")
            if self._send_received_message(message):
                self.logger.info("Checking the received message")
                if self._message_check(message, 1)[0]:
                    
                    self._parse_message(
                        message, 1)

                    self.logger.info("One message has been done")
                    
                    # 更新环境变量
                    self._update_variables()

                else:
                    info = self._message_check(
                        message, 1)[1]
                    self.logger.warning(
                        "Errors occored while checking the message: "+info)
                    self._predeal_finished_message(message, info)
            else:
                self.logger.error(
                    "Parameter missed or errors occured or task passed by controller in sending received message")
        except Exception:
            self.logger.error("Errors occured during predealing the message")
            raise

    # kafka消息获取
    def _listen_message(self):
        '''
        Listen the message of kafka from high and lower topic
        '''

        self.logger.info("Start to connect kafka server")
        consumer = kafka.KafkaConsumer(
            group_id=self.task_group_id, bootstrap_servers=self.kafka_cluster)  #,request_timeout_ms=11000,session_timeout_ms=10000
        self.logger.info("high_topic:  "+str(self.service_high_topic))
        self.logger.info("lower_topic:  "+str(self.service_lower_topic))
        try:
            while True:
                self.logger.info("Listening the high topic message")
                consumer.subscribe(topics=[self.service_high_topic])
                message = consumer.poll(timeout_ms=2000, max_records=1)
                if len(message) > 0:
                    for key in message.keys():
                        message = json.loads(
                            message[key][0].value.decode('utf-8'))
                    self.logger.info(
                        "the message received in high topic:"+str(message))
                    self._predeal_message(message)
                    consumer.commit()
                    continue
                consumer.subscribe(
                    topics=[self.service_lower_topic, self.service_high_topic])

                while True:
                    self.logger.info(
                        "Listening the high and lower topic message")
                    message = consumer.poll(timeout_ms=2000, max_records=1)
                    if not len(message):
                        time.sleep(0.5)
                        continue
                    for key in message.keys():
                        message = json.loads(
                            message[key][0].value.decode('utf-8'))
                    self.logger.info(
                        "The message received in higher or lower topic:"+str(message))
                    self._predeal_message(message)
                    consumer.commit()
                    break

        except Exception:
            self.logger.info(
                "Errors occured while polling or handling the message:  "+traceback.format_exc())
            raise

    # 同步服务注册                          之前尝试的次数               可设定的参数，调节等待长短  ms
    # 如果返回false  重试3次 retry时间间隔=2^previous_attempt_number * wait_exponential_multiplier 和 wait_exponential_max 较小值
    @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT)
    def _resigter_service(self):
        '''
        Send the information to the manager of services for registing service
        :return: if sucess,return True;else return False
        '''
        parametas = json.dumps(self.server_register_parameter)
        #print(eval(self.server_register_parameter))
        print(self.server_register_parameter)
		
        try:
            # 设置的超时时间为两秒
            self.logger.info(self.register_url)
            ret = requests.post(self.register_url, data=parametas, timeout=4)
            temp = ret.json()
            self.logger.info(temp)
            self.service_id = temp['id']

            self.service_lower_topic = temp['topic']['low_priority']
            self.service_high_topic = temp['topic']['high_priority']

            self.task_group_id = "task_group"  # 高优先级group
            self.service_state = temp['state']
            if self.service_state is True:
                self.logger.info('Registered service successfully!')
                return True
            else:
                self.logger.error(
                    'Registered service unsuccessfully with the fail of service manager')
                return False
        except Exception:
            self.logger.error('Registered service unsuccessfully   ' +
                              traceback.format_exc())
            raise

    # 默认的健康检查信息
    async def _default_health_check(self, request):
        '''
        The route for checking health for default
        '''
        return sjson({
            "state": "health",
            "info": "service is healthy"
        })

    # 添加健康检查
    def _add_health_check(self):
        '''
        Add the route of checking health for sanic
        '''
        try:
            if self._health_check != None:
                self.app.add_route(self._health_check,
                                   uri=self.healthcheck_path,methods=["GET"])
            else:
                self.logger.warning("Using default health check function")
                self.app.add_route(self._default_health_check,
                                   uri=self.healthcheck_path,methods=["GET"])
        except Exception:
            self.logger.error(
                "Error occored during adding healthcheck route of sanic: "+traceback.format_exc())
            raise
    # 服务运行

    def run(self):
        '''
        Start sanic for checking health, if sucess,registe the service and listen the message from kafka
        '''
        try:
            if self._handle_input_item == None and self._handle_input_items == None:
                self.logger.error("No handling function")
                return
            self.mpid = os.getpid()
            self.main_process_group_id = os.getpgid(self.mpid)
            self.logger.info("ID of main process is:"+str(self.mpid))
            self.logger.info("ID of group of main process is:"+str(self.main_process_group_id))

            with open('./gid.txt', 'w') as f:
                f.write(str(self.main_process_group_id))

            # 健康检查注册路由
            self._add_health_check()

            def _run_err_call(gid):
                self.spid = os.getpid()
                self.sgid = os.getpgid(self.spid)

                self.logger.info("ID of sub process is:"+str(self.spid))
                self.logger.info(
                    "ID of group of sub process is:"+str(self.sgid))
                self.logger.info("Errors melt in running sainc")
                # 子进程及当前主进程均关闭
                # 子进程和主进程属于同一进程组，获取进程组ID之后，向进程组发送kill信号
                os.killpg(gid, signal.SIGKILL)

            # 运行sanic的函数
            def _run_sanic():
                # 单开进程池来运行sanic，单独进程没有error_callback函数
                self.p = POOL(2)
                self.p.apply_async(self.app.run(
                    self.service_ip, self.service_port), args=(), error_callback=_run_err_call(self.main_process_group_id))

            self.process = Process(target=_run_sanic)
            self.process.start()

            subpid = self.process.pid
            subgid = os.getpgid(subpid)
            self.logger.info("ID of sub process is:"+str(subpid))
            self.logger.info("ID of group of sub process is:"+str(subgid))

            # 注册服务,重试的次数最大为3次，返回true才算成功
            if not self._resigter_service():
                self.logger.error(
                    "Fail to register service! Error:unreachable server")
                return
            # 监听消息
            self._listen_message()

        except Exception:
            self.logger.error(
                "Error occored while running the main process:  "+traceback.format_exc())
            os.killpg(self.main_process_group_id, signal.SIGKILL)
            return

    # 终止服务

    def stop():
        '''
        Kill the process group to stop the service
        '''
        # 检查pid是否存在
        def check_pid(pid):
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
                
        # 获取到的gid即为主进程的pid,可以用检查pid的方法检查gid是否存在
        with open('./gid.txt', 'r') as f:
            gid = int(f.read())
            print("Gid in file:"+str(gid))

        if check_pid(gid):
            os.killpg(gid, signal.SIGKILL)
            print("Kill the service sucessully")
        else:
            print("No such process group")

    def _parse_message(self, message, message_type):
        '''
        Logical Control of Message Processing

        :param message{dict}: the message received from kafka
        :param message_type{int}: the type of the message. the value is 0 or 1. 0:control message; 1:general message
        '''

        # 每次处理消息，都需要将error_info字典初始化为空
        self.error_info = {
            "framework": [],
            "user": []
        }

        if message_type == 0:  # to control message handle
            self.handle_control_message(message)
            return

        # 获取变量
        stage = message['output']['current_stage']
        index = message['output']['current_index']
        stages = message['output']['stages']
        next_stages_list = message['output']['stages'][stage]['next']
        service_list = message['output']['stages'][stage]['units']
        task_id = message["task_id"]
        child_id = message["child_id"]
        input_list = message['data']
        topic = message['output']["stages"][stage]["units"][index]["topic"]
        config = message['output']["stages"][stage]["units"][index]["config"]
        depth = message['output']['depth']

        is_final_step = False  # 如果is_final_step为真, 表示这是该stage的最后一个step
        try:

            # 条件成立，表示当前微服务是当前stage的最后一个step，处理完成后需要进行输出
            # 所以，需要查看next列表和store列表，以确定阶段结束后数据的流向
            if index + 1 == len(service_list):
                is_final_step = True

                # 如果next列表和store列表为空，表示数据没有输出，后续过程无意义，结束任务
                if not next_stages_list:
                    self._send_finished_message(0, 0, task_id, child_id, "finished")
                    return
        except :
            error_msg = "something in message need\n%s"%(traceback.format_exc())
            self.logger.error(error_msg)
            self.error_info["framework"].append(error_msg)

        # 进行深度判断，如果当前深度等于最大深度，则结束任务
        if depth == message['output']['max_depth']:
            self._send_finished_message(0, 0, task_id, child_id, "finished")
            return

        self.logger.info("start redis handle")
        set_name = '{task_id}_{topic}'.format(task_id=task_id, topic=topic)
        aid_set_name = '{task_id}_{topic}_aid'.format(task_id=task_id, topic=topic)

        # 通过配置信息，决定是否使用redis．redis存储了该微服务以往执行的历史数据
        framework_config = config.get('framework', None)

        # 框架配置为空，默认使用redis;不为空，根据用户的选择决定是否使用redis
        if framework_config is None:
            redis_config = True
        else:
            redis_config = framework_config.get("redis", True)

        # redis_config为真，则根据历史数据去重之后的数据作为真正的输入；否则，message的输入作为真的输入　　　
        if redis_config:
            valid_data_list = self._calculate_different_set(set(input_list), set_name,aid_set_name)
        else:
            valid_data_list = input_list

        # 如果真输入为空，则该微服务结束,发送结束消息
        if not valid_data_list:
            self._send_finished_message(0, 0, task_id, child_id, "finished")
            return
        self.logger.info("end redis handle")

        # 进行数据转换
        valid_data_list = list(map(type(input_list[0]), valid_data_list))
        self.logger.info(valid_data_list)
        valid_data_length = len(valid_data_list)

        # 进行数据计算
        self.logger.info("start calculate data")
        try:
            result_list = self._handle_data_message(valid_data_list, config.get("service", {}))
        except Exception as e:
            self.logger.error("the function _handle_data_message is wrong")
            raise
        data_to_kafka = []    # 记录正确的结果，准备将消息发送给下一个kafka的topic

        # 对于每一个计算结果，如果；
        # 如果返回的记录为空，那么可能是发生了一个目前未知的错误
        # 否则，结果正确，记录到data_to_kafka中
        # print(result_list)
		
        for result in result_list:
            self.logger.info(result)
            if result['error_info']:
                err_msg = "{input}: the reason is :{error_info}".format(**result)
                self.error_info["user"].append(err_msg)
                self.logger.info(err_msg)
            elif not result['output']:
                err_msg = "{input}: the reason is : no caculating result".format(**result)
                self.error_info["user"].append(err_msg)
                self.logger.info(err_msg)
            else:
                data_to_kafka.append(result['output'])

        # 如果没有正确的数据，结束任务
        if not data_to_kafka:
            self._send_finished_message(len(valid_data_list), 0, task_id, child_id, "finished")
            return
        self.logger.info("end calculate data")

		
		#存储有效的输入输出
        temp_data=[]
        for item in result_list:
            if not (item["output"]== None or len(item["output"])== 0):
                single_temp_data={}
                single_temp_data["input"]=item["input"]
                single_temp_data["output"]=item["output"]
                temp_data.append(single_temp_data)

        #处于stage的最后一个step,向next的stage的第一个topic推相应的数据(不同stage的数据可能不一样)
        if is_final_step:
            #将数据发送给next列表中的所有topic并按照调用相应的输出函数
            self.logger.info("Prepare the message to topic of next list")
            message['output']['depth'] = depth + 1

            flow_state = "finished"     # flow_state 表示当前微服务处理后任务的状态
            next_topic_number = 0
            ###  stage  index  stages
            #将有效输出转为stage中需要的格式
            for next_stage in next_stages_list:
                print(next_stage)
                
                try:
                    temp_output=set()
                    list_output=[]
                    true_output=[]

                    for item in temp_data:
                        temp=self.name_map[stages[stage]["next"][next_stage]](item)
                        if not (type(temp)==list):
                            self.logger.error("The return result must be list")
                        else:
                            list_output=list_output+temp
                    
                    for item in list_output:
                        temp_output.add(item)
                    
                    for item in temp_output:
                        true_output.append(item)
					
                    if not len(true_output):
                        continue
					
                    next_topic_number = next_topic_number + 1
                    flow_state = "running"

                    #检查true_output是否为所需要的类型
                    output_topic=stages[next_stage]["units"][0]["topic"]
                    message["data"]=true_output
                    message["output"]["current_stage"] = next_stage
                    message["output"]["current_index"] = 0
                    message["output"]["pre_unit"]=self.service_type
                    message["child_id"] = "{}_{}".format(message["child_id"], str(next_topic_number))
                    self._send_message(message, output_topic)

                except:
                    error_msg = "kafka error:\n{traceback}".format(traceback=traceback.format_exc())
                    self.logger.error(error_msg)
                    self.error_info["framework"].append(error_msg)
            self._send_finished_message(valid_data_length, len(data_to_kafka), task_id, child_id, flow_state,next_topic_number)

        # 处于stage的中间
        else:
            self.logger.debug("Not the final step in stage")
            self.logger.info("Prepare the message to next topic")
            
            true_output=[]
            temp_output=set()

            for item in temp_data:
                temp=self.to_next_default(item)
                for itema in temp:
                    temp_output.add(itema)
            
            for item in temp_output:
                true_output.append(item)
            
            if not len(true_output):
                self._send_finished_message(len(valid_data_list), 0, task_id, child_id, "finished")
                return
            
            self.logger.info(true_output)
            message["data"]=true_output
            message["output"]["current_index"] = message["output"]["current_index"] + 1
            message["output"]["pre_unit"]=self.service_type
            output_topic=stages[stage]["units"][index+1]["topic"]
            message["child_id"] = "{}_{}".format(message["child_id"], str(1))
            try:
                self._send_message(message, output_topic)
            except Exception as e:
                error_msg = "kafka error:{e}\n{traceback}".format(e=str(e), traceback=traceback.format_exc())
                self.logger.error(error_msg)
                self.error_info["framework"].append(error_msg)
            self._send_finished_message(len(valid_data_list), len(result_list),
                                       task_id, child_id, "running",1)
        self.logger.info("start add data to history set")
        self._store_valid_data(set_name, aid_set_name)
        self.logger.info("end add data to history set")

    def handle_control_message(self, message):
        '''
        handle control message

        :param message{dict}: control message received from kafka
        '''
        print("this is handle_control_message")

    @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT)
    def _send(self, finished_message):
        '''
        send finished message to the finished API and return the response. If error occurs, retry 3 times.

        :param finished_message{dict}: the message which should send to the finished API
        :return: the response body of the finished API
        '''
        resp = requests.put(self.finished_url, data=json.dumps(finished_message), timeout=2)
        return resp.json()

    def _send_finished_message(self, valid_input_length, output_length,
                              task_id, child_id, status, next_topic_number = 0):
        '''
        Logical Processes of send message to finished API

        :param valid_input_length{int}: Length of input data after making a difference with historical data
        :param output_length{int}: number of the correct results
        :param task_id{string}: the task id
        :param child_id{int}: the child id
        :param status{string}: the task state. the type is string, the value is finished or running
        '''
        finished_message = {
            "type": "finished",
            "worker_id": self.service_id,
            "worker_type": self.service_type,
            "valid_input_length": valid_input_length,
            "output_length": output_length,
            "task_id": task_id,
            "child_id": child_id,
            "status": status,
            "error_msg": self.error_info,
			"branch":next_topic_number
        }
        try:
            self.logger.info(finished_message)
            response_dic = self._send(finished_message)
        except:
            self.logger.error("Cannot send message to finished API\n%s"%traceback.format_exc())
            return

        # 对响应中返回的数据进行分析　 0:成功, -2:失败，参数错误
        if response_dic.get("state", -2):
            self.logger.error("Error: exception occur in send_finished_message function. the url or json data is wrong")
        else:
            self.logger.info("send finished message success")
            self.logger.debug(finished_message)

    @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT)
    def get_sub(self, set_name, data_set, aid_set_name):
        '''
        Write data_set into a set named 'set_help' in redis. caculate different set between
        set_help set and historical set.If failed, retry 3 times. Throw an exception after three failed retries.

        :param set_name{string}: historal set name.
        :param data_set{set}: the input data.
        :param aid_set_name{string}: the name of aid set.
        :return: return the result of calculating the difference set
        '''
        try:
            self.redis_handle.delete(aid_set_name)  # 清空辅助redis.set集合

            # 使用pipeline技术将数据批量插入到redis的集合中
            pipe = self.redis_handle.pipeline(transaction=False)
            for value in data_set:
                pipe.sadd(aid_set_name, value)
            pipe.execute()

            # 计算历史数据和输入数据之间的差集
            self.redis_handle.sdiffstore(aid_set_name, aid_set_name, set_name)
            return self.redis_handle.sinter(aid_set_name)

        except Exception as e:

            # 重连redis
            self.redis_handle = redis.Redis(host=self.redis_ip, port=self.redis_port, decode_responses=True)
            pipe = self.redis_handle.pipeline(transaction=False)
            raise

    def _calculate_different_set(self, data_set, set_name, aid_set_name):
        '''
        Obtain the difference set between the input data set and the historical data set by redis.
        If you can't connect to redis, record error messages, print logs, return to the front desk,
        and return the input data set as the valid data set.

        :param data_set{set}: input data set.
        :param set_name{string}: historical set name.
        :param aid_set_name{string}: the name of aid set.
        :return: the different data set between the input set and the historical set. the type is list
        '''
        r_list = list()
        try:
            r_list = list(self.get_sub(set_name, data_set, aid_set_name))
        except:
            r_list = list(data_set)
            err_msg = "redis refused when calculate different set\n%s"%traceback.format_exc()
            self.logger.error(err_msg)
            self.error_info["framework"].append(err_msg)
        finally:
            return r_list

    @retry(stop_max_attempt_number=RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT)
    def _set_union(self, set_name, aid_set_name):
        '''
        Find the union of two redis sets.
        If failed, retry 3 times. Throw an exception after three failed retries.
        :param set_name{string}:　historical data set name.
        :param aid_set_name{string}:　the name of aid set.
        '''

        # 将aid_set_name集合中的数据添加到set_name指定的集合中
        try:
            self.redis_handle.sunionstore(set_name, set_name, aid_set_name)
        except Exception as e:
            self.redis_handle = redis.Redis(host=self.redis_ip, port=self.redis_port, decode_responses=True)
            raise

    def _store_valid_data(self, set_name, aid_set_name):
        '''
        Store data from valid input sets into historical data sets by finding the union of two sets
        If failed, record error messages, print logs, and return to the front desk

        :param set_name{string}: the name of historical data set.
        :param aid_set_name{string}: the name of aid set.
        '''

        try:
            self._set_union(set_name,aid_set_name)
        except Exception as e:
            err_msg = "redis refused when insert data to set\n%s" % traceback.format_exc()
            self.logger.error(err_msg)
            self.error_info["framework"].append(err_msg)