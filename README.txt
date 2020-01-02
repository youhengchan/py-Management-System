【1】对于有filename.qrc文件的项目需要生成 filename_rc.py
使用命令： pyrcc5 filename.qrc -o filename_rc.py

【2】不要使用str = "a sample line here"来对一个字符串进行赋值
这样会导致代码里面的str(obj)类型转换全部失效，数据库操作也会全部失效
