import os
import sys
import time
import random
import csv
from selenium import webdriver
from pyquery import PyQuery as Pq

"""
ajax
根据关键字搜索豆瓣图书，并按评分排序给出结果
并且加入了缓存页面功能
再也不用重复请求了(网络请求很浪费时间)
这样做有两个好处
    1, 增加新内容(比如增加评论人数)的时候不用重复请求网络
    2, 出错的时候有原始数据对照
"""

user_agent_list = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
]


class Model():
    """
    基类, 用来显示类的信息
<Book
  name=(python机器学习)
  score=(7.8)
  evaluate=((19人评价))
  meta=(Sebastian Raschka / 高明 / 机械工业出版社 / 2017-3-15 / 79)
  cover_url=(https://img1.doubanio.com/view/subject/l/public/s29407827.jpg)>,
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Book(Model):
    """
    存储图书信息
    """

    def __init__(self):
        # 名称 评分 打分人数 作者及出版信息 主页链接 封面图片链接
        self.name = ''
        self.score = 0
        self.evaluate = ''
        self.meta = ''
        self.url = ''
        self.cover_url = ''


def cached_url(driver, url):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    filename = url.split('=')[-1] + '.html'
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        # print('正在从缓存中读取')
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            print('正在下载并缓存')
            os.makedirs(folder)
        # # 发送网络请求, 把结果写入到文件夹中
        # # 随机选择一个user_agent
        # # user_agent = random.choice(user_agent_list)
        # user_agent = user_agent_list[0]
        # # 传递给header
        # headers = {'User-Agent': user_agent,
        #            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #            'Accept-Encoding': 'gzip,deflate,br',
        #            'Accept-Language': 'zh-CN,zh; q=0.9,en-US; q=0.8,en; q=0.7',
        #            'Host': 'book.douban.com',
        #            }
        # r = session.get(url, headers=headers)
        # print(r.status_code)
        driver.get(url)
        content = driver.page_source.encode('UTF-8')
        # sys.exit()
        with open(path, 'wb') as f:
            f.write(content)
        # 每次请求网页后随机暂停几秒
        # 在此处而不是在主程序暂停是为了读缓存时不用等待
        nap = random.random() * 5
        time.sleep(nap)
    return content


def book_from_div(div):
    """
    从一个 div 里面获取到一本书的信息
    """
    e = Pq(div)
    # 小作用域变量用单字符
    b = Book()
    b.name = e('.title').text()
    b.score = e('.rating_nums').text() or '0'
    b.evaluate = e('.pl').text()
    b.meta = e('.abstract').text()
    b.url = e('.title-text').attr('href')
    # xmlns这个属性可能导致pyquery无法如下解析
    b.cover_url = e('.cover').attr('src')
    return b


def books_from_url(url, driver):
    """
    从 url 中下载网页并解析出页面内所有的图书
    """
    page = cached_url(url, driver)
    e = Pq(page)
    items = e('.item-root')
    # 调用 book_from_div
    books = [book_from_div(i) for i in items]
    next_page = e('.thispage').next().text()
    if next_page == '后页':
        next_page = None
    return books, next_page


class Save:
    """
    接收list[books object], 可保存为不同版本的csv
    默认版本 中文版本 有评价版本
    """
    def __init__(self, books, file_name='books'):
        self.books = books
        self.file_name = file_name
        self.fieldnames = ['name', 'score', 'evaluate', 'meta', 'url', 'cover_url']
        self.rows = []

    @staticmethod
    def has_zh(name):
        """书名是否含有中文
        todo 对繁体中文/日文有误判"""
        for char in name:
            if u'\u4e00' <= char <= u'\u9fff':
                return True
        return False

    def books_to_rows(self):
        """
        对数据进行清洗排序, 生成包含所有行的列表
        """
        # fieldnames = ['name', 'score', 'evaluate', 'price', 'publish_date', 'publish_house', 'authors', 'cover_url']
        for b in self.books:
            name = b.name
            score = b.score or 0
            evaluate = ''.join(filter(str.isdigit, b.evaluate)) or '0'
            meta = ','.join(b.meta.replace(' ', '').split('/'))
            # if len(meta) <= 3: print(meta)
            # price, publish_date, publish_house, authors = meta[-1], meta[-2], meta[-3], ','.join(meta[:-3])
            url = b.url
            cover_url = b.cover_url
            # row = [name, score, evaluate, price, publish_date, publish_house, authors, cover_url]
            row = [name, score, evaluate, meta, url, cover_url]
            self.rows.append(row)

    def rows_to_csv(self):
        """
        生成包含所有行的csv
        """
        # f1 = open(file_name + '_zh.csv')
        #         # w1 = csv.writer(f1)
        #         # f2 = open(file_name + '_evl.csv')
        #         # w2 = csv.writer(f2)
        file_name = self.file_name + '.csv'
        with open(file_name, 'w', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fieldnames)
            for row in self.rows:
                writer.writerow(row)
            print('成功写入文件: ', file_name)

    def rows_to_csv_zh(self):
        """
        名称里有中文的书 写入 _zh.csv
        """
        file_name = self.file_name + '_zh.csv'
        with open(file_name, 'w', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fieldnames)
            for row in self.rows:
                name = row[0]
                if self.has_zh(name):
                    writer.writerow(row)
            print('成功写入文件: ', file_name)

    def rows_to_csv_el(self):
        """评价人数大于0的书 写入 _el.csv"""
        file_name = self.file_name + '_el.csv'
        with open(file_name, 'w', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fieldnames)
            for row in self.rows:
                evaluate = row[2]
                if evaluate.isdigit() and int(evaluate) > 0:
                    writer.writerow(row)
            print('成功写入文件: ', file_name)

    def write(self):
        self.books_to_rows()
        self.rows_to_csv()
        self.rows_to_csv_zh()
        self.rows_to_csv_el()


def main(key):
    next_page = '1'
    driver = webdriver.Chrome()
    begin = 0
    all_books = []
    while next_page:
        url = 'https://book.douban.com/subject_search?search_text={}&cat=1001&start={}'.format(key, begin)
        # 程序出错时自动关闭浏览器
        try:
            # raise TimeoutError('获取数据超时')
            books, next_page = books_from_url(driver, url)
        except Exception as e:
            print(e)
            driver.close()
            sys.exit()
        all_books.extend(books)
        # print('搜索到如下结果: \n', all_books)
        begin += 15
        # break
    all_books.sort(key=lambda x: float(x.score), reverse=True)
    s = Save(all_books)
    s.write()


if __name__ == '__main__':
    main('python')
