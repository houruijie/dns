from flask import Flask, request
from detector import judge_DNS
import json
import os

app = Flask(__name__)


@app.route('/',methods=["GET","POST"])
def index():
    ip_list = request.form.get("ip_list")
    ip_list = ip_list.split(',')
    judge_result = judge_DNS(ip_list)
    return json.dumps(judge_result)

@app.route('/test',methods=["GET","POST"])
def hello_world():
    return 'hello world'


if __name__ == '__main__':
    mpid = os.getpid()
    main_process_group_id = os.getpgid(mpid)

    with open('./gid.txt', 'w') as f:
        f.write(str(main_process_group_id))
    app.run(host='0.0.0.0', port=5000)