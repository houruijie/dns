export DNS_DB_IP='127.0.0.1'              # 设置环境变量,用户编写的微服务依靠的DNS解析API的所依赖的Mysql数据库的IP地址
export DNS_URL="http://127.0.0.1/7777/batch"  # 设置环境变量,用户编写的微服务依靠的DNS解析API的服务的URL
a=`lsof -i:7777 | wc -l`        # 检查端口服务是否开启,如果没有开启,需要到指定文件夹下面开启API
if [ "$a" -gt "0" ];then
    cd dns/
    python2 -m pip install -r requirements.txt  # 安装依赖包
    nohup python2 dns_tool_new.py &      # 开启API
#else
#    echo "1" 
fi
cd ../domain_to_ip
python3 -m pip install -r requirements.txt
nohup python3 domain_to_ip.py &
