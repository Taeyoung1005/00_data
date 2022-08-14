from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

from selenium import webdriver
# 싱글프로세싱
# from crawlers.DaumNewsCrawler import DaumCrawler
# from crawlers.NaverNewsCrawler import NaverCrawler

# 멀티프로세싱
# from crawlers.DaumNewsMultiCrawler import crawlLinks as daumCrawlLinks, crawlNews as daumCrawlNews
from crawlers.NaverNewsMultiCrawler import crawlLinks as naverCrawlLinks, crawlNews as naverCrawlNews

from utils.util import *

import json
import datetime

import numpy as np
 
from tqdm import trange
import utils.processing_json as Processing_json

import sys
sys.setrecursionlimit(5000)

import warnings


def info_time(dic, us_news, kr_news):
    dic_key = dic.keys()
    info_term_time = []

    date_dic = {}

    for i in dic_key:
        temp_time = [x.split('.')[1] for x in dic[i]]

        if len(temp_time) > 1:
            temp_time.sort()
            sum_time = 0

            for j in temp_time:
                '''
                j = kr_news[j]['date']
                year_ = int(j[:4])
                mon_ = int(j[4:6])
                day_ = int(j[6:8])
                '''
                hour_ = int(j[8:10])
                min_ = int(j[10:12])
                sec_ = int(j[12:14])
                sum_time += hour_ * 60 * 60 + min_ * 60 + sec_
            avg_time = sum_time / len(temp_time)

            end_year = temp_time[-1][:4]
            end_mon = temp_time[-1][4:6]
            end_day = temp_time[-1][6:8]
            end_hour = temp_time[-1][8:10]
            end_min = temp_time[-1][10:12]
            end_ = ''.join([
                str(i)
                for i in [end_year, end_mon, end_day, end_hour, end_min
            ]])

            start_year = temp_time[0][:4]
            start_mon = temp_time[0][4:6]
            start_day = temp_time[0][6:8]
            start_hour = temp_time[0][8:10]
            start_min = temp_time[0][10:12]
            start_ = ''.join([
                str(i)
                for i in [start_year, start_mon, start_day, start_hour, start_min
            ]])

            diff = (datetime(
                    int(end_year),
                    int(end_mon),
                    int(end_day),
                    int(end_hour),
                    int(end_min)
                )  -  datetime(
                    int(start_year),
                    int(start_mon),
                    int(start_day),
                    int(start_hour),
                    int(start_min)
                )).total_seconds()
            info_term_time.append([
                i,
                us_news[i]['title'],
                us_news[i]['date'],
                start_,
                end_,
                diff,
                avg_time
            ])

            this_date = us_news[i]['date'][:8]

            if this_date in date_dic.keys():
                date_dic[this_date].append(avg_time)
            else:
                date_dic[this_date] = [avg_time]

    for k, v in date_dic.items():
        date_dic[k] = round(np.mean(v)/3600, 1)

    return date_dic

    # dataframe = df(info_term_time, columns=['URL', 'Title', '미국기사 시간', '처음 한국기사 시간', '마지막 한국기사 시간', 'diff', '평균'])
    # dataframe.to_csv('Task2.csv', encoding='cp949')

def main(search, start_date, end_date):
    #if __name__ == "__main__":
    # 크롬 드라이버 링크
    warnings.filterwarnings(action='ignore')
    driver_url = './chromedriver.exe'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--privileged')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-dev-shm-usage')

    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument('disable-gpu')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    chrome_options.add_argument('lang=ko_KR')

    # selenium으로 크롤링하여 저 장된 링크를 가지고 requests로 다시 크롤링하여 json으로 저장
    # kr은 requests로 동기식, us는 grequests와 async로 비동기식 (kr은 비동기가 안먹힘(다음뉴스 500 오류))

    #search = search # 검색할 키워드
    #start_date = start_date # 검색 기간 시작 날짜
    #end_date = end_date # 검색 기간 종료 날짜


    """ 싱글 프로세싱 코드

    # # 크롤러 객체 생성
    # daum_crawler = DaumCrawler(driver_url, chrome_options)
    # naver_crawler = NaverCrawler(driver_url, chrome_options)

    # daum_crawler.crawlLinks(search, start_date, end_date) # 링크 크롤링(selenium)
    # daum_crawler.crawlNews(search, start_date, end_date) # 뉴스 크롤링(async+grequest+bs4)
    
    # naver_crawler.crawlLinks(search, start_date, end_date) # 링크 크롤링(selenium)
    # naver_crawler.crawlNews(search, start_date, end_date) # 뉴스 크롤링(async+grequest+bs4)
    """


    # 멀티 프로세싱 코드  
    naverCrawlLinks(search, start_date, end_date, driver_url, chrome_options)
    naverCrawlNews(search, start_date, end_date, driver_url, chrome_options)

    #json 파일 날짜 합치기
    json_data = {}
    for date in range(int(start_date[:6]), int(end_date[:6])+1):
        date = str(date)
        print(date)
        try:
            with open(f'../main_program/result/naver_news/comment_seperate/news_{search}_naver_{start_date}_{end_date}__{date}.json', 'r', encoding='UTF-8') as f:
                json_data.update(json.load(f))
        except:
            continue
    
    #기사없는날 처리
    m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    for date in range(int(start_date), int(end_date)+1):
        date = str(date)
        if date not in json_data:
            if int(date[6:]) < m[int(date[4:6])-1]+1:
                if date[6:] != "00" and date[4:6] != "00":
                    json_data[date] = {}

    json_data = dict(sorted(json_data.items()))
    #이모지 제거
    json_data = Processing_json.dateNList(json_data)

    #이모지 지움으로 인해 빈 댓글 발생 처리
    for date in json_data:
        for url in json_data[date]:
            for comments in json_data[date][url]:
                example = []
                for i in range(len(json_data[date][url][comments])):
                    if len(json_data[date][url][comments][i].strip(" ")) != 0:
                        example.append(json_data[date][url][comments][i])
                json_data[date][url][comments] = example  

    with open(f'../main_program/result/naver_news/news_{search}_naver_{start_date}_{end_date}.json', 'w', encoding='UTF-8') as f:
        json.dump(json_data, f, indent=4, sort_keys=True, ensure_ascii=False)

    dic = {}
    dic2 = {}
        
    start_date_ = datetime.date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
    end_date_ = datetime.date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:])) + datetime.timedelta(days=1)

    date_list = [str(i).replace('-', '')[0:8] for i in daterange(start_date_, end_date_)]


    for date in date_list:
        if date not in dic.keys():
            dic[date] = {}

    all = 0
    for date in dic.keys():
        for company in ["naver"]: #daum은 따로
            with open(f'result/{company}_news/news_{search}_{company}_{start_date}_{end_date}.json', 'r', encoding='UTF-8') as f:
                dic2 = json.load(f)
            try:
                dic[date].update(dic2[date])
            except:
                continue
            
    dic2 = {}
    for date in dic.keys():
        if date[:6] not in dic2.keys():
            dic2[date[:6]] = []

        dic2[date[:6]].append(dic[date])


    all = 0
    for mon in dic2.keys():
        count = 0
        for dic3 in dic2[mon]:
            for url, contain in dic3.items():
                for comment in contain['comments']:
                    count += 1
        all += count
        print(f'{mon} : {count}')
    print(f'all : {all}')

    # with open(f'result/news_{search}_all_{start_date}_{end_date}.json', 'w', encoding='utf8') as f:
    #     json.dump(dict(dic), f, indent=4, sort_keys=True, ensure_ascii=False)
    
    exit()



    