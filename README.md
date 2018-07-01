[DoubanBookSearch](http://chromedriver.chromium.org/downloads)
======================
#功能说明
想根据评分指导Python书籍选购，在豆瓣读书上搜索python的结果是无序的，而豆瓣未提供按评分排序的功能，
于是自己写了爬虫，抓取并缓存搜索结果，对数据适当清洗后根据评分由高到低排序，存入csv文件。

Python图书评分排行Top10（基于豆瓣读书数据）

书名 | 评分 | 评价人数 | 出版信息 
---- | ----- | -------- | ---- 
Python神经网络编程 | 9.7 | 15 | [英]塔里克·拉希德（TariqRashid）,林赐,人民邮电出版社,2018-4,69.00元
Fluent Python | 9.6 | 196 | LucianoRamalho,O'ReillyMedia,2015-8-20,USD39.99
Data Structures and Algorithms in Python | 9.6 | 44 | MichaelT.Goodrich,RobertoTamassia,MichaelH.Goldwasser,JohnWiley&Sons,2013-7-5,GBP121.23
Django By Example | 9.5 | 24 | AntonioMele,PacktPublishing,2015-11-30,GBP28.99
流畅的Python | 9.4 | 195 | [巴西]LucianoRamalho,安道,吴珂,人民邮电出版社,2017-5-15,139元
Python编程初学者指南 | 9.4 | 20 | [美]MichaelDawson,王金兰,人民邮电出版社,2014-10-1
Hands-On Machine Learning with Scikit-Learn and TensorFlow : Concepts, Tools, and Techniques for Building Intelligent Systems | 9.4 | 177 | AurélienGéron,O'ReillyMedia,2017-1-25,USD49.99
深度学习之TensorFlow：入门、原理与进阶实战 | 9.4 | 16 | 李金洪,2018-2
Python Cookbook 中文版，第 3 版 | 9.3	 | 100 | DavidM.Beazley,BrianK.Jones,陈舸,人民邮电出版社,2015-5-1,108.00元
Python Cookbook | 9.3 | 97 | DavidBeazley,BrianK.Jones,O'ReillyMedia,2013-5-29,USD49.99

#使用说明
运行环境 mac OS 10.14, Python 3.6, Chrome 67, ChromeDriver 2.37

- 安装依赖包 $pip3 install -r requirements.txt
- 下载 [ChromeDriver](http://chromedriver.chromium.org/downloads) 解压后放到 python安装位置/bin 目录
- 编辑book.py将末行 main('python') 的参数改为需要搜索的书籍名称
- 运行 python3 book.py


