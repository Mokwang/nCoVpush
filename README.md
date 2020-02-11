# nCoVpush
抓取丁香园实时疫情信息，通过[server酱](http://sc.ftqq.com/3.version)推送消息到微信

使用方法：
  1. 在[server酱](http://sc.ftqq.com/3.version)上注册，登录，获取seckey, 将sckey写入到`./sckey_file`文件中
  2. 在自己的机器上安装docker
  3. 运行`docker build -t ncovpush:v1 .` build 自己的image
  4. 启动命令：`docker run -d --name=ncovpush -v $SCRIPTPATH:/code/nCoVpush ncovpush:v1`
  
如果不想自己搭建，可以通过以下方法将sckey加入到我的服务器上直接使用
> 使用方法：
>+   在[server酱](http://sc.ftqq.com/3.version)上注册并绑定微信，可以在[发送消息](http://sc.ftqq.com/?c=code)页面填写内容，确认消息能成功推送
>+   访问链接：http://34.92.95.115:8000/sckey/?key=$YOURSECKEY
>+   返回`key save success "$YOURSECKEY"`表示添加成功
  
