# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 17:45:04 2017

@author: Administrator
"""

import scrapy
import pymysql

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    start_urls = [
        'http://sou.zhaopin.com/',
        ]
    def parse(self, response):
        main = response.css('div.search_content')   #获取查询主体
        human = main.css('div.clearfixed')          #获取职位名称
        href_all = []                     #所有的待处理url
        for i in range(119):
            hi = human[i].css('a::attr(href)').extract()
            href_all.append(hi)                             #extend和append的区别
        hrefs = []                         #我们要的url
        href_cut = href_all[60:]
        for hh in href_cut:
            flag = False
            for h in hh:
                if flag:
                    hr = 'http://sou.zhaopin.com' + h +'&p='
                    hrefs.append(hr)
                else:
                    flag = True

        position_all = []
        positions = []
        for i in range(119):
            hi = human[i].css('a::text').extract()
            position_all.append(hi) 
        position_cut = position_all[60:]
        for pp in position_cut :
            flag = False
            category = ''
            for p in pp:
                if flag:
                    posi= category + ':'+p
                    positions.append(posi)
                else:
                    category= p
                    flag = True
        dic = zip(positions, hrefs)
        poDict = dict( (position,href) for position,href in dic)
        for position in poDict:
            for i in range(90):
                yield scrapy.Request(str(str(poDict[position])+str(i+1)), meta = { 'href' : poDict[position], 'position': position  }, callback = self.parse_position)

    def parse_position(self, response):
        hrefs = response.css('td.zwmc a::attr(href)').extract()
        position = response.meta["position"]
        print("meta1="+position)
        for href in hrefs:
            yield scrapy.Request(str(href), meta = {'position': position,'href': href}, callback = self.parse_describe)

    def parse_describe(self, response):
        print("parse_describe_3")
        c = response.css('div.tab-cont-box')[0]
        content = c.css('p::text').extract()
        position = response.meta["position"]
        company = response.css('div.fixed-inner-box h2 a::text').extract_first()
        date = response.css('div.terminalpage-left span#span4freshdate::text').extract_first()
        href = response.meta["href"]
        job = response.css('div.fixed-inner-box h1::text').extract()
        print("job = " + job[0])
        require = ''
        for c in content:
            require = require + c.strip()
        print(require)
        #岗位+jd
        fo = open("/usr/local/scrapy/hrjd/jobs_jd.txt", "a")   #追加写入
        fo.write('title='+position+':'+job[0]+ "\r\n")    #通用\r\n在windows中用\r\n来换行，linux中用\r来换行
        fo.write('company='+company+ "\r\n")
        fo.write('date='+date+ "\r\n")
        fo.write('jd='+require + "\r\n")
        fo.write(' ------\r\n')
        fo.close()
