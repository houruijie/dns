export DNS_JUDGE_URL='http://127.0.0.1:5000/'  # 设置环境变量,用户编写的微服务依靠的DNS判断API的服务的URL
a=`lsof -i:5000 | wc -l`        # 检查端口服务是否开启,如果没有开启,需要到指定文件夹下面开启API
if [ "$a" -gt "0" ];then
    cd dns_judge/
    python2 -m pip install -r requirements.txt  # 安装依赖包
    nohup python2 service.py &      # 开启API
#else
#    echo "1" 
fi
cd ../ip_to_dnstype
python3 -m pip install -r requirements.txt
nohup python3 ip_to_dnstype.py &


