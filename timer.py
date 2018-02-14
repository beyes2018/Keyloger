# coding:utf-8
import time
import ConfigParser
import os, zipfile
from os.path import join
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os.path
import mimetypes
import datetime
import email.MIMEImage  # import MIMEImage
import smtplib

config = ConfigParser.ConfigParser()
count = 0


def getproperties(type, name):
    with open('config.cfg', 'r') as cfgfile:
        config.readfp(cfgfile)
        return config.get(type, name)


msg = MIMEMultipart()

# 输入Email地址和口令:
from_addr = getproperties('email', 'from_addr')
password = getproperties('email', 'password')
# 输入收件人地址:
to_addr = getproperties('email', 'to_addr')
# 输入SMTP服务器地址:
smtp_server = getproperties('email', 'smtp_server')
hour = getproperties('time', 'hour')
minute = getproperties('time', 'minute')
day = getproperties('time', 'day')


def zip_folder(foldername, file_name):
    zip = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(foldername):
        for filename in files:
            zip.write(join(root, filename).encode("gbk"))
        if len(files) == 0:
            zif = zipfile.ZipInfo((root + '/').encode("gbk" + "/"))
            zip.writestr(zif, "")
    zip.close()


def sendemail(file_name, subject):
    # 邮件正文是MIMEText:
    msg.attach(MIMEText(str(datetime.datetime.now()) + file_name + subject, 'plain', 'utf-8'))

    # 添加附件就是加上一个MIMEBase
    # 构造MIMEBase对象做为文件附件内容并附加到根容器
    ctype, encoding = mimetypes.guess_type(file_name)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    file_msg = email.MIMEImage.MIMEImage(open(file_name, 'rb').read(), subtype)

    ## 设置附件头
    basename = os.path.basename(file_name)
    file_msg.add_header('Content-Disposition', 'attachment', filename=basename)  # 修改邮件头
    msg.attach(file_msg)

    # 发送邮箱地址
    msg['From'] = from_addr
    # 收件箱地址
    msg['To'] = to_addr
    # 主题
    msg['Subject'] = subject

    server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


while True:
    i = datetime.datetime.now()
    if str(i.hour) == hour and str(i.minute) == minute:
        folder = getproperties('folder', 'folder')
        filename = folder + '.zip'
        if __name__ == "__main__":
            try:
                zip_folder(folder, filename)
                sendemail(filename, '邮件')
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
    time.sleep(10)
