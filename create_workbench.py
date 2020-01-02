# from stable_version.workbench import Ui_MainWindow as UI
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType  # 用于动态加载UI
from functools import wraps  # 用于装饰器信息修正
from xlrd import *  # 用于导出Excel
from xlsxwriter import *  # 用于导出Excel
import MySQLdb  # 用于Mysql数据库操作
import time  # 用于对导出记录添加事件戳
import sys  # 用于os操作
import threading  # 用于多线程异步处理数据，防止卡顿


ui, _ = loadUiType('workbench.ui')  # 动态加载ui文件，避免修改后需要重新 generate py文件
login_ui, _ = loadUiType("loginToWorkbench.ui")

# 已完成
# 自动延时清除状态栏功能
# 将该装饰器挂载到有状态栏改变的函数上，time_duration 秒后自动清除状态栏
def delay_seconds_clean_status_bar(time_duration):
    def decorator(func):
        @wraps(func)
        def wrappered_func(window_widget):
            def cleaner():
                window_widget.statusBar().showMessage("")
            ret_value = func(window_widget)
            timer = threading.Timer(time_duration, cleaner)  # 异步延迟，防止GUI密集操作造成的卡顿
            timer.start()
            return ret_value
        return wrappered_func
    return decorator


# 登录到主界面之前的登录界面
class Login(QWidget, login_ui):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)  # 该方法派生自UI类
        # 定义拖拽窗口标记
        self.m_flag = False
        self.m_Position = None
        # 处理按钮逻辑
        self.handle_buttons()
        # 设置程序图标
        self.setWindowIcon(QIcon("media/workbench.ico"))
        # 美化界面，删除原生边框，设置窗口透明度
        self.setFixedSize(self.width(), self.height())  # 禁止拉伸窗口大小
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)  # 禁止最大化按钮
        self.setWindowOpacity(0.95)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        # self.setStyleSheet("background-image: url(media/background.png)")  # 设置窗口背景图片
        # 设置密码输入框
        self.lineEdit_2.setEchoMode(QLineEdit.Password)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))  # 在释放鼠标按键之后恢复为箭头形状的图标

    def handle_buttons(self):
        self.pushButton_2.clicked.connect(self.click_to_login)
        self.pushButton.clicked.connect(self.click_to_close)

    def click_to_close(self):
        self.close()

    def click_to_login(self):
        user_name = self.lineEdit.text()
        user_password = self.lineEdit_2.text()

        if user_name == "" or user_password == "":
            self.label.setText("用户名或密码错误")
            return

        # 连接数据库，查询所有账号和密码并依次比对
        self.db = MySQLdb.connect(host='localhost', user='root', password='toor', db='nuclear')
        self.cur = self.db.cursor()

        sql = ''' SELECT * FROM userstable''';

        self.cur.execute(sql)
        data = self.cur.fetchall()

        # 用于清除提示
        def cleaner():
            self.label.setText("")

        # 登录是否成功标记
        login_succeed = False

        for row in data:
            if user_name == row[0] and user_password == row[1]:
                self.label.setText("登录成功")
                self.db.close()
                self.main_window = WorkbenchMainWindow()
                self.close()
                self.main_window.show()
                login_succeed = True


        if not login_succeed:
            # 密码错误提示
            self.db.close()
            self.label.setText("用户名或密码错误")
            return



# 主界面
class WorkbenchMainWindow(QMainWindow, ui):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)  # 该方法派生自UI类
        # 定义拖拽窗口标记
        self.m_flag = False
        self.m_Position = None
        # 处理UI逻辑
        self.handle_ui_changes()
        # 处理按钮事件
        self.handle_buttons()
        # 展示所有的任务类型
        self.show_job_list()
        # 展示公司名称到所有下拉框
        self.show_company_name_in_combo_box()
        # 设置密码输入框
        self.lineEdit_8.setEchoMode(QLineEdit.Password)
        self.lineEdit_9.setEchoMode(QLineEdit.Password)
        # 动态加载所有用户
        self.show_user_name_in_combo_box()
        # 设置程序图标
        self.setWindowIcon(QIcon("media/workbench.ico"))
        # 美化界面，删除原生边框，设置窗口透明度
        self.setFixedSize(self.width(), self.height())  # 禁止拉伸窗口大小
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)  # 禁止最大化按钮
        self.setWindowOpacity(0.95)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        # self.setStyleSheet("background-image: url(media/background.png)")  # 设置窗口背景图片

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))  # 在释放鼠标按键之后恢复为箭头形状的图标

    # 定义按钮消息相应函数
    def handle_buttons(self):
        # 最小化 和 关闭 窗口
        self.pushButton_20.clicked.connect(self.showMinimized)  # 按下按钮20最小化窗口
        self.pushButton_18.clicked.connect(self.close)  # 按下按钮18关闭窗口

        # 主界面界面切换
        self.pushButton_5.clicked.connect(self.switch_to_logs_panel)  # 按下按钮5切换到日志界面
        self.pushButton_2.clicked.connect(self.switch_to_jobs_panel)  # 按下按钮2切换到任务界面
        self.pushButton_3.clicked.connect(self.switch_to_users_panel)  # 按下按钮3切换到用户界面
        self.pushButton_4.clicked.connect(self.switch_to_export_panel)  # 按下按钮4切换到导出界面
        self.pushButton_6.clicked.connect(self.switch_to_help_panel)  # 按下按钮5切换到帮助界面


        # 日志界面查找按钮
        self.pushButton.clicked.connect(self.search_and_show_with_2_filters)

        ################################
        ###### 用户界面 ################

        # 注册新用户
        self.pushButton_11.clicked.connect(self.register_new_user)

        # 添加单位信息
        self.pushButton_13.clicked.connect(self.register_new_company)

        # 修改单位信息
        self.pushButton_14.clicked.connect(self.change_company_name)

        # 删除单位
        self.pushButton_17.clicked.connect(self.delete_company)

        # 修改用户信息
        self.pushButton_12.clicked.connect(self.change_user_password)

        ################################
        ###### 任务界面 ################

        # 添加新任务
        self.pushButton_8.clicked.connect(self.add_new_job)

        # 查找任务信息
        self.pushButton_7.clicked.connect(self.search_job)

        # 修改任务信息
        self.pushButton_9.clicked.connect(self.modify_job)

        # 删除任务
        self.pushButton_10.clicked.connect(self.delete_job)

        ######################################
        ############ 导出界面 #################

        # 导出指定用户的数据
        self.pushButton_15.clicked.connect(self.export_user_data)

        # 导出所有用户数据
        self.pushButton_16.clicked.connect(self.export_all_data)

        # 导出用户列表
        self.pushButton_22.clicked.connect(self.export_user_info)

        # 导出单位列表
        self.pushButton_21.clicked.connect(self.export_company_list)

    # 定义UI界面切换消息相应函数
    def handle_ui_changes(self):
        self.tabWidget.tabBar().setVisible(False)  # 隐藏tab标签

    # 切换界面到任务界面
    def switch_to_jobs_panel(self):
        self.tabWidget.setCurrentIndex(1)

    # 切换界面到日志界面
    def switch_to_logs_panel(self):
        self.tabWidget.setCurrentIndex(0)

    # 切换界面到用户界面
    def switch_to_users_panel(self):
        self.tabWidget.setCurrentIndex(2)

    # 切换界面到导出界面
    def switch_to_export_panel(self):
        self.tabWidget.setCurrentIndex(3)

    # 切换界面到帮助界面
    def switch_to_help_panel(self):
        self.tabWidget.setCurrentIndex(3)

    ##########################################
    ########  任务面板  #######################
    ## 展示任务 \ 添加任务 \ 修改任务 \ 删除任务

    # 已修改str为result
    # 已完成
    # 任务 -》 任务列表
    # 展示所有任务
    def show_job_list(self):

        def print_result(data):
            if data:
                self.tableWidget_3.setRowCount(0)  # 从头开始绘制
                self.tableWidget_3.insertRow(0)  # 首先插入一个空行
                for row, line in enumerate(data):
                    for column, element in enumerate(line):
                        self.tableWidget_3.setItem(row, column, QTableWidgetItem(str(element)))
                        column += 1
                    row_position = self.tableWidget_3.rowCount()
                    self.tableWidget_3.insertRow(row_position)

        # connect to the database with the host \ username \ password \ schema name
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # 开始查询
        self.cur.execute('''
                          SELECT * FROM jobtypestable;
                        ''',)

        # 获得所有数据，指定的job_id的任务的所有的信息
        data = self.cur.fetchall()

        # 提交请求
        self.db.commit()

        # 检查查询到的数据
        # print(data, type(data))

        # 绘制结果,检查数据逻辑封装在绘制函数中，减少代码量
        print_result(data)

        # 关闭数据库连接，结束查询
        self.db.close()

    # 已经修改str为result
    # 已完成
    # 任务 -》添加任务
    # 添加任务
    @delay_seconds_clean_status_bar(5)
    def add_new_job(self):
        # connect to the database with the host \ username \ password \ schema name
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # console 输出提示信息
        # print("数据库连接成功")

        # 任务名称
        job_name = self.lineEdit_2.text()
        # 任务代码
        job_code = self.lineEdit_3.text()
        # 任务描述
        job_desc = self.plainTextEdit.toPlainText()

        # console 输出提示信息
        # print("任务名称 {0}, 任务代码 {1}, 任务描述 {2}".format(job_name ,job_code, job_desc))

        # 执行sql语句，向表 companiestable 的 companyname 列中写入字符串 company_name
        # 注意在后期开发的时候，写sql语句后面即使只有一个元素，也需要加上','
        # 这关系到python的数据类型("str")和("str")的类型是不一样的
        # ("str") 类型为：str
        # ("str",) 类型为：tuple
        self.cur.execute('''
                    INSERT INTO jobtypestable (jobtype, jobcode, jobdesc) VALUES (%s, %s, %s)
                ''', (job_name, job_code, job_desc))

        # 向数据库提交执行
        self.db.commit()
        self.db.close()

        # console 输出提示信息
        result = "已完成 添加新任务 任务名称 {0}, 任务代码 {1}, 任务描述 {2}".format(job_name, job_code, job_desc)
        # print(result)

        # 状态栏改变
        self.statusBar().showMessage(" " * 5 + result)

        # 清空输入信息
        self.lineEdit_2.setText("")
        self.lineEdit_3.setText("")
        self.plainTextEdit.setPlainText("")

        # 添加完任务重新加载任务表
        self.show_job_list()

    # 已经修改str为result
    # 已完成
    # 根据jobtype或者jobcode查找任务
    # 并将查找的结果写入界面中的相应框中
    # 任务 -》 修改任务
    # 查找任务
    @delay_seconds_clean_status_bar(5)
    def search_job(self):
        # 设计的时候，可以通过jobcode和jobtype两种方式进行查询

        self.lineEdit_6.setText("")
        self.lineEdit_7.setText("")
        self.plainTextEdit_2.setPlainText("")

        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # console 输出提示信息
        # print("数据库连接成功")

        # 获得要查询的任务，首先当作jobtype进行处理
        job_code = self.lineEdit_5.text()

        if job_code == "":
            # print("查询内容不能为空")
            self.db.close()
            return


        # 注意在后期开发的时候，写sql语句后面即使只有一个元素，也需要加上','
        # 这关系到python的数据类型("str")和("str")的类型是不一样的
        # ("str") 类型为：str
        # ("str",) 类型为：tuple
        self.cur.execute('''
                         SELECT * FROM jobtypestable WHERE jobtype=%s or jobcode=%s;             
                        ''', (job_code, job_code))

        result_list = self.cur.fetchall()

        # 如果查询结果不为空

        if len(result_list) != 0:
            self.lineEdit_6.setText(result_list[0][0])
            self.lineEdit_7.setText(result_list[0][1])
            self.plainTextEdit_2.setPlainText(result_list[0][2])


        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

        # 清空输入信息
        self.lineEdit_5.setText("")


        # console 输出提示信息
        result = "已完成 查询 {0} ".format(job_code)

        # 如果查询结果为空，则增加提示
        if len(result_list) == 0:
            result += " 查询结果为空"
        self.statusBar().showMessage(" "*5+result)


    # 已经修改str为result
    # 已完成（含各种异常检查）
    # 根据jobtype修改表jobtypestable中的desc和jobcode
    # 注意这里主键设定的是jobtype，在数据库中，主键是不能修改的
    # 只有添加和删除两个选择
    # 然后更新任务列表
    # 任务 -》 修改任务
    # 修改任务
    @delay_seconds_clean_status_bar(5)
    def modify_job(self):
        # 设计的时候，可以通过jobcode和jobtype两种方式进行查询

        job_type = self.lineEdit_6.text()
        job_code = self.lineEdit_7.text()
        job_desc = self.plainTextEdit_2.toPlainText()

        if (job_type == ""):
            result = "修改失败 任务名不能为空"
            self.statusBar().showMessage(" " * 5 + result)
            return

        if (job_code == ""):
            result = "修改失败 任务代码不能为空"
            self.statusBar().showMessage(" " * 5 + result)
            return

        # 允许任务的描述为空
        # 所以不对任务的描述进行非空性进行检查

        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()


        # 首先检查任务名是否存在
        self.cur.execute('''
                            SELECT * FROM jobtypestable WHERE jobtype=%s;             
                        ''', (job_type,))

        jobs_list = self.cur.fetchall()

        # 向数据库提交执行
        self.db.commit()

        # 输出查结果：
        print("Check Name with Company Info")
        print(jobs_list, type(jobs_list))

        # 该任务名并不存在：
        if len(jobs_list) == 0:
            result = "失败 修改信息 任务 {0} 不存在".format(job_type)

            # 输出最终提示信息
            self.statusBar().showMessage(" " * 5 + result)

            # 关闭数据库连接
            self.db.close()

            # 返回
            return

        # 该任务名存在，可以修改密码
        self.cur.execute('''
                            UPDATE jobtypestable SET jobcode=%s, jobdesc=%s WHERE jobtype=%s;                
                               ''', (job_code, job_desc, job_type))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

        # 清除输入框
        self.lineEdit_6.setText("")
        self.lineEdit_7.setText("")
        self.plainTextEdit_2.setPlainText("")


        # 状态栏输出提示
        result = "已完成 修改任务信息 任务名 {0} 任务代码 {1} 任务描述 略".format(job_type, job_code, job_desc)
        self.statusBar().showMessage(" " * 5 + result)

        # 然后更新任务列表
        self.show_job_list()

    # 已完成
    # 任务 -》 修改任务
    # 删除任务
    # 异常判断
    # 首先根据job_type判断要删除的任务是否存在
    # 如果该任务存在，就删除
    # 否则return
    # 根据
    @delay_seconds_clean_status_bar(5)
    def delete_job(self):

        # 获得要删除的任务名称
        job_name = self.lineEdit_6.text()
        job_code = self.lineEdit_7.text()

        # 如果任务名为空
        if job_name == "" or job_code == "":
            # 状态栏输出提示
            result = "操作无效 任务名 代码 描述 不匹配"
            self.statusBar().showMessage(" " * 5 + result)
            return

        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        self.cur.execute('''
                         DELETE FROM jobtypestable WHERE jobtype=%s and jobcode=%s;                
                        ''', (job_name, job_code))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

        # 清除输入框
        self.lineEdit_6.setText("")
        self.lineEdit_7.setText("")
        self.plainTextEdit_2.setPlainText("")

        # 状态栏输出提示
        result = "已完成 删除任务 任务名 {0} 任务代码 {1}".format(job_name, job_code)
        self.statusBar().showMessage(" " * 5 + result)

        # 更新任务列表
        self.show_job_list()

    #########################################
    ############# 日志面板 ##################
    ## 根据过滤器 ：任务状态 \ 单位 查找所有任务并展示

    # 查询符合两个过滤器的任务并将其在主界面展示出来、
    # 查询的逻辑：
    # 1. 首先判断流水号输入框是否为空
    ##### 2. 如果流水号不为空，直接根据流水号进行查询
    ##### 3. 如果流水号为空，检查用户名称的条件框是否为空
    ########### 4. 如果用户名称的条件框为空，return
    ########### 5. 如果用户名称的条件框不为空，通过and逻辑进行查表
    @delay_seconds_clean_status_bar(5)
    def search_and_show_with_2_filters(self):

        # 首先清空查询结果表
        self.tableWidget.setRowCount(0)
        self.tableWidget.clearContents()

        # connect to the database with the host \ username \ password \ schema name
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # 1. 首先判断流水号输入框是否为空
        job_id = self.lineEdit.text()

        ##### 2. 如果流水号不为空，直接根据流水号进行查询
        if job_id != "":
            # 开始查询
            self.cur.execute('''
                            SELECT * FROM alljobstable WHERE jobid=%s;
                            ''', (job_id,))

            # 获得所有数据，指定的job_id的任务的所有的信息
            data = self.cur.fetchall()

            # 提交请求
            self.db.commit()

            # print(data, type(data))

            # 绘制结果
            # 只能重复写
            if data:
                self.tableWidget.setRowCount(0)  # 从头开始绘制
                self.tableWidget.insertRow(0)  # 首先插入一个空行
                row_position = 1
                # Debug
                # print("Print Out Debug Info")
                for row, line in enumerate(data):
                    # print("in row {0}".format(row))
                    for column, element in enumerate(line):
                        # print("in row {0} col {1}".format(row, column))
                        # if element is not None:
                        # print(element, type(element))
                        self.tableWidget.setItem(row, column, QTableWidgetItem(str(element)))
                    self.tableWidget.insertRow(row_position)
                    row_position = row_position + 1


            # 状态栏输出结果
            result = "查询完成 共查询到 {0} 条结果".format(len(data))
            self.statusBar().showMessage(" " * 5 + result)

            # 关闭数据库连接，结束查询
            self.db.close()

            # 该分支逻辑结束，退出
            return

        ##### 3. 如果流水号为空，检查用户名是否为空
        else:

            if self.comboBox_2.count() == 0:

                # 输出提示信息
                result = "操作无效 用户名为空"

                # 输出最终提示信息
                self.statusBar().showMessage(" " * 5 + result)

                # 关闭数据库连接
                self.db.close()

                # 此时直接返回
                return

            else:

                # 读取任务状态
                job_status = self.comboBox.currentText()

                # 转换为数据库中存储的0/1
                if job_status.endswith("已结束"):
                    job_status = 1

                else:
                    job_status = 0

                # 读取用户名
                user_name = self.comboBox_2.currentText()

                # print("user_name = {0} job_status = {1}".format(user_name, job_status))


                # 此时进行两个信息联合查询
                # 通过 任务的状态和用户名进行查询
                # 开始查询
                self.cur.execute('''
                                 SELECT * FROM alljobstable WHERE jobstatus=%s and username=%s;
                                 ''', (job_status, user_name))

                # 获得所有数据，指定的job_id的任务的所有的信息
                data = self.cur.fetchall()

                # 提交请求
                self.db.commit()

                # print(data, type(data))

                # 绘制结果
                # 只能重复写
                if data:
                    self.tableWidget.setRowCount(0)  # 从头开始绘制
                    self.tableWidget.insertRow(0)  # 首先插入一个空行
                    row_position = 1
                    # Debug
                    # print("Print Out Debug Info")
                    for row, line in enumerate(data):
                        # print("in row {0}".format(row))
                        for column, element in enumerate(line):
                            # print("in row {0} col {1}".format(row, column))
                            # if element is not None:
                            # print(element, type(element))
                            self.tableWidget.setItem(row, column, QTableWidgetItem(str(element)))
                        self.tableWidget.insertRow(row_position)
                        row_position = row_position + 1

                # 输出提示信息
                result = "查询完成 共查询到 {0} 条结果".format(len(data))

                # 输出最终提示信息
                self.statusBar().showMessage(" " * 5 + result)

                # 关闭数据库连接，结束查询
                self.db.close()

                return

        # 不属于以上的任何一种情况，说明出现异常
        # 关闭数据库连接，结束查询
        self.db.close()

        # 结束返回
        return

    #########################################
    ############# 用户面板 ##################

    # 已完成str修改为result
    # 已完成(包含各种异常检测)
    # 空用户名检查
    # 两次密码不相同检查
    # 是否存在用户名检查
    # 不存在给出建议单位信息
    # 用户 -》 用户信息
    # 注册新用户
    @delay_seconds_clean_status_bar(5)
    def register_new_user(self):
        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # console 输出提示信息
        # print("数据库连接成功")

        # 获得: 用户名，公司名，密码，重复密码
        user_name = self.lineEdit_4.text()
        company_name = self.comboBox_3.currentText()
        password = self.lineEdit_8.text()
        repeat_password = self.lineEdit_9.text()

        # 密码为空检查
        if user_name == "":
            result = "操作失败 用户名不能为空"
            self.statusBar().showMessage(" " * 5 + result)
            # 关闭数据库连接
            self.db.close()
            return

        # 两次密码重复检查
        if password  != repeat_password:
            result = "操作失败 创建账号 两次密码不一致"
            self.statusBar().showMessage(" " * 5 + result)
            # 关闭数据库连接
            self.db.close()
            return

        else:
            result = "用户名 {0} 公司名 {1} 密码 {2} 重复密码 {3}".format(user_name, company_name, password, repeat_password)
        # console 输出提示信息
        # print(result)

        # 接着检查 用户名 是否存在
        # 由于用户名设置为主键，所以不能重复，即使是公司名不同也不行
        self.cur.execute('''
                         SELECT username FROM userstable WHERE username=%s;             
                        ''', (user_name, ))

        name_list = self.cur.fetchall()

        # 向数据库提交执行
        self.db.commit()

        # 输出查结果：
        # print(name_list, type(name_list))

        # 该用户名并已经存在：
        if len(name_list) != 0:
            result = "操作失败 用户名 {0} 已注册".format(user_name)
            self.statusBar().showMessage(" " * 5 + result)
            # 关闭数据库连接
            self.db.close()
            return

        # 执行sql语句，向表 companiestable 的 companyname 列中写入字符串 company_name
        # 注意在后期开发的时候，写sql语句后面即使只有一个元素，也需要加上','
        # 这关系到python的数据类型("str")和("str")的类型是不一样的
        # ("str") 类型为：str
        # ("str",) 类型为：tuple
        self.cur.execute('''
                    INSERT INTO userstable (username, password, company) VALUES (%s, %s, %s)
                ''', (user_name, password, company_name))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()
        # print("数据库连接关闭成功")

        # 清空输入信息
        self.lineEdit_4.setText("")
        self.lineEdit_8.setText("")
        self.lineEdit_9.setText("")
        self.comboBox_3.setCurrentIndex(0)

        # console 输出提示信息
        result = "已完成 注册新用户 " + result
        # print(result)
        self.statusBar().showMessage(" " * 5 + result)

        # 动态加载所有用户
        self.show_user_name_in_combo_box()

    # 已完成str修改为result
    # 已完成(包含各种异常检测)
    # 空用户名检查
    # 两次密码不相同检查
    # 是否存在用户名 + 单位检查
    # 不存在（用户名 + 单位）给出建议单位信息
    # 用户 -》 用户信息
    # 修改信息(用户密码)
    @delay_seconds_clean_status_bar(5)
    def change_user_password(self):
        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # 获得要求改的用户名称
        user_name = self.lineEdit_4.text()

        # 获得修改后的用户密码
        new_password = self.lineEdit_8.text()

        # 获得用户修改后的重复输入的密码
        new_repeat_password = self.lineEdit_9.text()

        # 用户两次密码重复检查
        if new_password  != new_repeat_password:
            result = "操作失败 修改信息 两次密码不一致"
            self.statusBar().showMessage(" " * 5 + result)
            # 关闭数据库连接
            self.db.close()
            return

        # 用户名为空检查
        if user_name == "":
            result = "操作失败 修改信息 用户名不能为空"
            self.statusBar().showMessage(" " * 5 + result)
            # 关闭数据库连接
            self.db.close()
            return

        # 获得用户的公司名称
        company_name = self.comboBox_3.currentText()

        # 首先检查用户名是否存在
        self.cur.execute('''
                            SELECT username FROM userstable WHERE company=%s and username=%s;             
                        ''', (company_name, user_name))

        name_list = self.cur.fetchall()

        # 向数据库提交执行
        self.db.commit()

        # 输出查结果：
        # print("Check Name with Company Info")
        # print(name_list, type(name_list))

        # 该用户名并不存在：
        if len(name_list) == 0:
            result = "操作失败 用户名 {0} 单位 {1} 不存在".format(user_name, company_name)



            # 搜索数据库，输出建议结果：
            # 首先检查用户名是否存在
            self.cur.execute('''
                             SELECT * FROM userstable WHERE username=%s;             
                             ''', (user_name, ))

            name_list = self.cur.fetchall()

            # 向数据库提交执行
            self.db.commit()

            # 输出查结果：
            # print(name_list, type(name_list))
            # 输出提示结果
            # print(name_list, type(name_list), len(name_list))

            # 如果能找到ID正确，但是公司不对的就给出建议

            if len(name_list) != 0:
                result += "   可能是指：{0} 来自 {1} ".format(name_list[0][0], name_list[0][2])

            # 输出最终提示信息
            self.statusBar().showMessage(" " * 5 + result)

            # 关闭数据库连接
            self.db.close()

            # 返回
            return

        # 该用户名存在，可以修改密码
        self.cur.execute('''
                            UPDATE userstable SET password=%s WHERE company=%s and username=%s;                
                               ''', (new_password, company_name, user_name))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

        # 清除输入框
        self.lineEdit_4.setText("")
        self.lineEdit_8.setText("")
        self.lineEdit_9.setText("")
        self.comboBox_3.setCurrentIndex(0)

        # 状态栏输出提示
        result = "已完成 修改用户信息 用户新密码 {0}".format(new_password)
        self.statusBar().showMessage(" " * 5 + result)


    # 已完成str修改为result
    # 已完成
    # 用户 -》 单位信息
    # 包含异常处理
    # 1.不允许将名字修改为空的字符串
    # 修改信息 （修改单位名称）
    @delay_seconds_clean_status_bar(5)
    def change_company_name(self):

        # 获得修改后的公司名称
        new_company_name = self.lineEdit_11.text()

        # 检查是否为空的字符串
        if new_company_name == "":
            # Status Bar 输出提示信息
            result = "操作失败 单位名称 不能为空"
            self.statusBar().showMessage(" " * 5 + result)
            return

        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # 获得要求改的公司名称
        old_company_name = self.comboBox_4.currentText()

        self.cur.execute('''
                            UPDATE companiestable SET companyname=%s WHERE companyname=%s;                
                        ''', (new_company_name, old_company_name))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

        # 清除输入框
        self.lineEdit_11.setText("")

        # 状态栏输出提示
        result = "已完成 修改单位名称 原名称 {0}， 新名称 {1}".format(old_company_name, new_company_name)
        self.statusBar().showMessage(" " * 5 + result)

        # 更新所有公司名称下拉框
        self.show_company_name_in_combo_box()

    # 已完成str修改为result
    # 已完成
    # 用户 -》 单位信息
    # 注册单位
    # 包含异常处理
    # 1. 空的单位名称不能注册
    # 2. 已经存在的公司名称不能重复注册
    @delay_seconds_clean_status_bar(5)
    def register_new_company(self):

        # 获得要注册的新的公司的名称
        company_name = self.lineEdit_12.text()

        # 检查是否为空的字符串
        if company_name == "":
            # Status Bar 输出提示信息
            result = "操作失败 单位名称 不能为空"
            self.statusBar().showMessage(" " * 5 + result)
            return

        # 首先判断该公司名是否已经存在
        # 此时不需要再次进入数据库查询数据
        # __init__的时候已经将公司名称放到了3个Combo Box中
        # 直接进行字符串比对即可
        is_valid_company_name = True
        for i in range(self.comboBox_4.count()):
            if company_name == self.comboBox_4.itemText(i):
                is_valid_company_name = False
                break

        if  not is_valid_company_name:
            # Status Bar 输出提示信息
            result = "操作失败 单位名称 不能重复"
            self.statusBar().showMessage(" " * 5 + result)
            return

        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # console 输出提示信息
        # print("数据库连接成功")

        # console 输出提示信息
        # print("新公司名称 {0}".format(company_name))


        # 执行sql语句，向表 companiestable 的 companyname 列中写入字符串 company_name
        # 注意在后期开发的时候，写sql语句后面即使只有一个元素，也需要加上','
        # 这关系到python的数据类型("str")和("str")的类型是不一样的
        # ("str") 类型为：str
        # ("str",) 类型为：tuple
        self.cur.execute('''
            INSERT INTO companiestable (companyname) VALUES (%s)
        ''', (company_name, ))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

        # 清空输入信息
        self.lineEdit_12.setText("")

        # console 输出提示信息
        result = "已完成 添加新单位 {0}".format(company_name)
        # print(result)
        self.statusBar().showMessage(" "*5+result)

        # 重新加载Combo Box 列表
        self.show_company_name_in_combo_box()

    # 已完成str修改为result
    # 已完成
    # 用户 -》 单位信息
    # 删除单位
    @delay_seconds_clean_status_bar(5)
    def delete_company(self):
        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        # 获得要求改的公司名称
        old_company_name = self.comboBox_4.currentText()

        self.cur.execute('''
                            DELETE FROM companiestable WHERE companyname=%s;                
                        ''', (old_company_name, ))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

        # 清除输入框
        self.lineEdit_11.setText("")

        # 状态栏输出提示
        result = "已完成 删除单位 原名称 {0} ".format(old_company_name)
        self.statusBar().showMessage(" " * 5 + result)

        # 更新所有公司名称下拉框
        self.show_company_name_in_combo_box()


    # 已完成
    ########## 动态加载所有的下拉框 ########
    ###### Combo Box 下拉框处理逻辑 #######
    #### 共有四个下拉框

    ### 日志面板的第一个下拉框
    ### 任务状态 已处理 / 待处理
    ### 此下拉框不需要从数据库中动态读取
    ### 直接从 UI Designer 中动态读取就可以了


    ### 日志面板的第二个下拉框
    ### 导出面板的用户选择下拉框
    ### 用户名称选择，需要从数据库中动态读取
    def show_user_name_in_combo_box(self):

        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        sql = "SELECT username FROM userstable;"
        self.cur.execute(sql)

        data = self.cur.fetchall()

        # 首先清空所有的Combo Box
        self.comboBox_2.clear()
        self.comboBox_5.clear()

        # 展示所有获得的数据
        # print(data)

        # 向三个Combo Box 中写入数据
        if data:
            for item in data:
                for name in item:
                    self.comboBox_2.addItem(str(name))
                    self.comboBox_5.addItem(str(name))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()

    # 已完成str修改为result
    # 已完成
    # 向2个Combo Box 中写入数据库中读出的公司的列表
    def show_company_name_in_combo_box(self):

        # 连接数据库nuclear
        self.db = MySQLdb.connect(host="localhost", user="root", password="toor", db="nuclear", charset='utf8')
        self.cur = self.db.cursor()

        sql = "SELECT companyname FROM companiestable;"
        self.cur.execute(sql)

        data = self.cur.fetchall()

        # 首先清空所有的Combo Box
        self.comboBox_3.clear()
        self.comboBox_4.clear()

        # 展示所有获得的数据
        # print(data)

        # 向2个Combo Box 中写入数据
        if data:
            for item in data:
                for name in item:
                    self.comboBox_3.addItem(str(name))
                    self.comboBox_4.addItem(str(name))

        # 向数据库提交执行
        self.db.commit()

        # 关闭数据库连接
        self.db.close()



    # 已完成
    ### 用户面板：用户信息：所属单位
    ### 需要动态加载单位，同上

    # 已完成
    ### 用户面板：单位信息：所属单位
    ### 需要动态加载，同上


    ##################################
    ##########数据导出功能#############

    # 已完成
    # 导出指定用户的记录数据
    @delay_seconds_clean_status_bar(5)
    def export_user_data(self):
        user_name = self.comboBox_5.currentText()

        # print("user_name = {}".format(user_name))

        if user_name == "" or self.comboBox_5.count() == 0:
            self.statusBar().showMessage('操作无效 需要先选择用户')
            return


        self.db = MySQLdb.connect(host='localhost', user='root', password='toor', db='nuclear', charset='utf8')
        self.cur = self.db.cursor()



        self.cur.execute(''' 
                    SELECT jobid , receivetime , endtime , jobtype , username, jobstatus FROM alljobstable WHERE username=%s
                ''',(user_name,))

        data = self.cur.fetchall()

        # 如果数据为空
        if len(data) == 0:
            self.db.close()
            self.statusBar().showMessage('用户 {} 记录 导出失败 该用户无有效记录'.format(user_name))
            return

        file_name_raw = './output_data/user_data/{0}_{1}_data.xlsx'.format(time.ctime().replace(' ', '_'), user_name)
        file_name = file_name_raw.replace(':', '_')
        wb = Workbook(file_name)
        sheet1 = wb.add_worksheet()

        sheet1.write(0, 0, '任务编号')
        sheet1.write(0, 1, '接收时间')
        sheet1.write(0, 2, '结束时间')
        sheet1.write(0, 3, '任务类型')
        sheet1.write(0, 4, '提交用户')
        sheet1.write(0, 5, '任务状态')

        row_number = 1
        for row in data:
            column_number = 0
            for item in row:
                if column_number == 5:
                    if str(item) == '1':
                        item = "已完成"
                    else:
                        item = "处理中"
                sheet1.write(row_number, column_number, str(item))
                column_number += 1
            row_number += 1

        wb.close()


        self.db.close()
        self.statusBar().showMessage('用户 {} 记录 导出成功'.format(user_name))

    # 已完成
    # 导出所有的记录数据
    @delay_seconds_clean_status_bar(5)
    def export_all_data(self):

        self.db = MySQLdb.connect(host='localhost', user='root', password='toor', db='nuclear', charset='utf8')
        self.cur = self.db.cursor()

        self.cur.execute(''' 
                            SELECT * FROM alljobstable;
                        ''')

        data = self.cur.fetchall()
        # print(data)

        # 如果数据为空
        if len(data) == 0:
            self.db.close()
            self.statusBar().showMessage('全部记录 导出失败 无有效记录')
            return

        file_name_raw = './output_data/all_data/{0}_all_data.xlsx'.format(time.ctime().replace(' ', '_'))
        file_name = file_name_raw.replace(':', '_')
        wb = Workbook(file_name)
        sheet1 = wb.add_worksheet()

        sheet1.write(0, 0, '任务编号')
        sheet1.write(0, 1, '接收时间')
        sheet1.write(0, 2, '结束时间')
        sheet1.write(0, 3, '任务类型')
        sheet1.write(0, 4, '提交用户')
        sheet1.write(0, 5, '任务状态')
        sheet1.write(0, 6, '文件路径')

        row_number = 1
        for row in data:
            column_number = 0
            for item in row:
                if column_number == 5:
                    if str(item) == '1':
                        item = "已完成"
                    else:
                        item = "处理中"
                sheet1.write(row_number, column_number, str(item))
                column_number += 1
            row_number += 1

        wb.close()

        self.db.close()
        self.statusBar().showMessage('全部记录 导出成功')

    # 已完成
    # 导出用户表（账号密码，单位）
    @delay_seconds_clean_status_bar(5)
    def export_user_info(self):
        self.db = MySQLdb.connect(host='localhost', user='root', password='toor', db='nuclear', charset='utf8')
        self.cur = self.db.cursor()

        self.cur.execute(''' 
                         SELECT * FROM userstable;
                         ''')

        data = self.cur.fetchall()
        # print(data)

        # 如果数据为空
        if len(data) == 0:
            self.db.close()
            self.statusBar().showMessage('用户列表 导出失败 无有效记录')
            return

        file_name_raw = './output_data/user_list_data/{0}_all_user_info.xlsx'.format(time.ctime().replace(' ', '_'))
        file_name = file_name_raw.replace(':', '_')
        wb = Workbook(file_name)
        sheet1 = wb.add_worksheet()

        sheet1.write(0, 0, '账号')
        sheet1.write(0, 1, '密码')
        sheet1.write(0, 2, '单位')

        row_number = 1
        for row in data:
            column_number = 0
            for item in row:
                sheet1.write(row_number, column_number, str(item))
                column_number += 1
            row_number += 1

        wb.close()

        self.db.close()
        self.statusBar().showMessage('用户列表 导出成功')

    # 已完成
    # 导出所有单位（单位名称）
    @delay_seconds_clean_status_bar(5)
    def export_company_list(self):
        self.db = MySQLdb.connect(host='localhost', user='root', password='toor', db='nuclear', charset='utf8')
        self.cur = self.db.cursor()

        self.cur.execute(''' 
                         SELECT * FROM userstable;
                         ''')

        data = self.cur.fetchall()
        # print(data)

        # 如果数据为空
        if len(data) == 0:
            self.db.close()
            self.statusBar().showMessage('单位列表 导出失败 无有效记录')
            return

        file_name_raw = './output_data/company_data/{0}_company_list.xlsx'.format(time.ctime().replace(' ', '_'))
        file_name = file_name_raw.replace(':', '_')
        wb = Workbook(file_name)
        sheet1 = wb.add_worksheet()

        sheet1.write(0, 0, '单位')

        row_number = 1
        for row in data:
            column_number = 0
            for item in row:
                sheet1.write(row_number, column_number, str(item))
                column_number += 1
            row_number += 1

        wb.close()

        self.db.close()
        self.statusBar().showMessage('单位列表 导出成功')








# 已完成
def create_workbench():

    app = QApplication(sys.argv)  # 创建一个QApplication，也就是你要开发的软件app
    main_window = WorkbenchMainWindow()  # ui是Ui_MainWindow()类的实例化对象
    main_window.show()  # 执行QMainWindow的show()方法，显示这个QMainWindow
    sys.exit(app.exec_())  # 使用exit()或者点击关闭按钮退出QApplication

# 已完成
def create_login():

    app = QApplication(sys.argv)  # 创建一个QApplication，也就是你要开发的软件app
    main_window = Login()  # ui是Ui_MainWindow()类的实例化对象
    main_window.show()  # 执行QMainWindow的show()方法，显示这个QMainWindow
    sys.exit(app.exec_())  # 使用exit()或者点击关闭按钮退出QApplication


def main():
    create_login()


if __name__ == "__main__":
    main()