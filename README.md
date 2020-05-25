HITWH_Library_Pending
===========

图书管理系统


## 搭配环境
 * 输入 sudo apt-get install python-virtualenv 安装virtualenv虚拟机
 * 输入 sudo apt-get install sqlite3 安装sqlite3
 * 输入 sqlite3 book.db < book.sql 创建数据库
 * 在项目根目录下执行source env/bin/activate， 开启虚拟机
 * 安装FLask模块 输入pip install Flask
 * 输入deactive, 关闭虚拟机
 * 在虚拟机开启情况下，输入python main.py，然后在浏览器中打开127.0.0.1:5000即可访问

## 导入数据
   在项目根目录 输入sqlite3 book.db
 * 进入sqlite3 shell，输入.separator "|" 后，再输入 .import books.txt books


## 兼容性相关
   由于flask框架在依赖的werkzeug工具包在python3下进行了重写，因此破坏了与python2的兼容性，但这是无奈。
