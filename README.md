# nCoVpush
通过server酱推送消息到微信

使用方法：
  1. 在server酱上注册，登录，获取seckey,将sckey写入到getdata.py中
  2. 在自己的机器上安装docker
  3. 运行`docker build -t ncovpush:v1 .` build 自己的image
  4. 启动命令：`docker run -d --name=ncovpush -v $SCRIPTPATH:/code/nCoVpush` ncovpush:v1
