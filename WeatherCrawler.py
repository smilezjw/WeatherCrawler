# coding=utf8

__author__ = 'smilezjw'

import urllib2
import re
import smtplib
from email.mime.text import MIMEText
import time
import sched

scheduler = sched.scheduler(time.time, time.sleep)

class WeatherSpider:
    def __init__(self):
        self.siteURL = 'http://www.weather.com.cn/weather1d/101190101.shtml'

    # 爬取siteURL该页面的内容
    def crawl(self):
        request = urllib2.Request(self.siteURL)
        response = urllib2.urlopen(request)
        content = response.read()
        response.close()
        return content

    # 解析爬取的内容
    # 这里只获取城市、时间以及温度、天气等信息
    def getContents(self):
        html = self.crawl()
        pattern = re.compile('\d+月\d+日\d+时.*C')
        data = re.findall(pattern, html)
        pattern = re.compile('<title>(.*)今天天气预报')
        city = re.findall(pattern, html)
        return city[0] + data[0]

    # 发送邮件
    def sendMail(self):
        scheduler.enterabs(self.everyDayRun(8, 5, 0, True), 1, self.sendMail, ())
        user = 'xxxxxx@xxxx.com'
        pwd = 'xxxxxx'
        to = 'xxxxxx@xxxx.com'
        msg = MIMEText('Good Morning!\r\n' + self.getContents())
        msg['Subject'] = 'Today Weather Forecast'
        msg['From'] = user
        msg['To'] = to
        s = smtplib.SMTP('smtp.qq.com', port=25)  # 注意需要去QQ邮箱设置中开启POP3/SMTP和IMAP/SMTP
        s.login(user, pwd)
        s.sendmail(user, to, msg.as_string())
        s.close()
        print 'Email has been sent!'

    def everyDayRun(self, hour, min, sec, nextDay=True):
        struct = time.localtime()
        if nextDay:
            day = struct.tm_mday + 1
        else:
            day = struct.tm_mday
        hereTime = time.mktime((struct.tm_year, struct.tm_mon, day,
                                hour, min, sec, struct.tm_wday, struct.tm_yday, struct.tm_isdst))
        return hereTime

if __name__ == '__main__':
    spider = WeatherSpider()
    # 启动程序后，先获取今天的数据，这里nextDay设置为False，如果设置为True则无法得到当天的数据了
    # enterabs和enter的区别在于enter中time是相对时间（相对于当前再过多久时间），而enterabs中time是绝对时间
    # 其他3个参数分别为优先级0最高， 需要执行的函数，该函数需要传递的参数元组（这里一定是以元组形式传递进去）
    scheduler.enterabs(spider.everyDayRun(8, 5, 0, False), 1, spider.sendMail, ())
    scheduler.run()
