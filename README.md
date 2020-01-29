# nCoVpush
通过server酱推送消息到微信

使用方法：
  1. 在server酱上注册，登录，获取seckey,将sckey写入到sckeys文件中
  2. 在自己的机器上安装docker
  3. 运行`docker build -t ncovpush:v1 .` build 自己的image
  4. 启动命令：`docker run -d --name=ncovpush -v $SCRIPTPATH:/code/nCoVpush ncovpush:v1`
  
如果不想自己搭建，可以通过以下方法将sckey加入到我的服务器上直接使用
> 使用方法：
>+   在server酱上注册并绑定微信，确认有消息推送
>+   访问链接：http://34.92.95.115:8000/sckey/?key=$YOURSECKEY
>+   返回`key save success`表示添加成功
  
