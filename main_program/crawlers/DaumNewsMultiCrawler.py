# 
# DaumNewsCrawler.py
# Web crawling program for Daum News
# Author : Ji-yong219
# Project Start:: 2021.07.24
# Last Modified from Ji-yong 2021.07.27
#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime
import json

from tqdm import trange

from utils.util import *

from multiprocessing import Process, Manager, cpu_count
import numpy as np


# 기사 링크 수집 메소드
def crawlLinks( search, start_date, end_date, driver_url, chrome_options):
    num_of_cpu = cpu_count()

    manager = Manager()
    url_list = manager.list()
    
    start_date_ = datetime.date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
    end_date_ = datetime.date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:])) + datetime.timedelta(days=1)

    date_list = [i for i in daterange(start_date_, end_date_)]
    date_list = np.array_split(np.array(date_list), num_of_cpu)

    processes = []


    for idx in range(num_of_cpu):
        process = Process(target=crawlLinksProcess,
            args=(
                date_list[idx],
                driver_url,
                chrome_options,
                search,
                url_list
            )
        )
        
        processes.append(process)
        process.start()
        
    
    for process in processes:
        process.join()

    with open(f'result/daum_news/urls_{search}_daum_{start_date}_{end_date}.txt', 'w', encoding='utf8') as f:
        f.writelines('\n'.join(list(set(list(url_list)))))
        
def crawlLinksProcess( date_list, driver_url, chrome_options, search, url_list):
    driver = webdriver.Chrome(driver_url, chrome_options=chrome_options)

    for date_ in date_list:
        url_page_num = 1

        while True:
            date__ = str(date_).replace('-', '')
            url = f'https://search.daum.net/search?w=news&q={search}&DA=STC&sd={date__}000000&ed={date__}235959&period=u&spacing=0&sort=sort&p={url_page_num}'
                
            print(f"다음 링크 크롤링시작 URL:{url}")
            driver.get(url)

            try:
                element = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="newsColl"]/div[1]/ul')) 
                )

            except TimeoutException:
                print("타임아웃")
                
                break

            div, news = None, None

            div = driver.find_element_by_xpath('//*[@id="newsColl"]/div[1]/ul')
            news = div.find_elements_by_css_selector('a[class="tit_main ff_dot"]')
        

            news = list(set(news))

            for i in range(len(news)):
                link = None

                link = news[i].get_attribute('href')

                if link is None or link == "":
                    continue

                link = link.replace('\n', '')
                if ( link.startswith("http://v.media.daum.net/") or link.startswith("https://news.v.daum.net/v/") ) and link not in url_list:
                    print(f'link : {link}')
                    try:
                        pass

                    except ValueError as e:
                        print("value Error", e, link)

                    else:
                        link = link.replace("?f=o", "")
                        url_list.append(link)


            result_count = driver.find_element_by_xpath('//*[@id="resultCntArea"]')
            result_count = result_count.text.split(' ')[0]
            now_count, whole_count = [int(i) for i in result_count.split('-')]

            print(f'now_count : {now_count}\t\twhole_count : {whole_count}')

            if now_count > whole_count:
                break
        
            url_page_num += 1
            
    driver.quit()
    return

def crawlNews( search, start_date, end_date, driver_url, chrome_options):
    num_of_cpu = cpu_count()

    manager = Manager()
    # news_dic = manager.dict()

    # start_date_ = datetime.date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
    # end_date_ = datetime.date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:])) + datetime.timedelta(days=1)

    # date_list = [str(i).replace('-', '')[0:8] for i in daterange(start_date_, end_date_)]

    # for date in date_list:
    #     news_dic[date] = manager.dict()

    news_queue = []


    with open(f'result/daum_news/urls_{search}_daum_{start_date}_{end_date}.txt', 'r', encoding='utf8', newline='\n') as f:
        for row in f.readlines():
            row = row.replace('\n', '').replace('\r', '')
            news_queue.append(row)

    news_queue_with_month = {}

    for i in sorted(news_queue):
        month = i[26:32]
        if month in news_queue_with_month.keys():
            news_queue_with_month[month].append(i)
        else:
            news_queue_with_month[month] = []

    split_index_count = 10

    for i in news_queue_with_month.keys():
        
        news_queue_with_month[i] = list(np.array_split(np.array(news_queue_with_month[i]), split_index_count))
        

        news_dic = manager.dict()


        for idx2, j in enumerate(news_queue_with_month[i], 1):
            for jj in j:
                if jj[26:34] not in news_dic.keys():
                    news_dic[jj[26:34]] = manager.dict()

            # title_list = np.array_split(np.array(news_queue), num_of_cpu)
            title_list = manager.Queue()

            [title_list.put(ii) for ii in j]
            
            processes = []
            
            for idx in range(num_of_cpu):
                process = Process(target=crawlNewsProcess,
                    args=(
                        idx,
                        driver_url,
                        chrome_options,
                        title_list,
                        news_dic,
                        i,
                        idx2,
                        split_index_count
                    )
                )
                
                processes.append(process)
                process.start()
                
            
            for process in processes:
                process.join()
                
            for key in news_dic.keys():
                if news_dic[key] != {}:
                    news_dic[key] = dict(news_dic[key])
                else:
                    news_dic[key] = None

        with open(f'result/daum_news/news_{search}_daum_{start_date}_{end_date}__{i}.json', 'w', encoding='utf8') as f:
            json.dump(dict(news_dic), f, indent=4, sort_keys=True, ensure_ascii=False)

def crawlNewsProcess( idx, driver_url, chrome_options, news_url_list, news_dic, split_date, now_split_index, split_index_count):
    driver = webdriver.Chrome(driver_url, chrome_options=chrome_options)
    count_ = 0
    # for ii, url in enumerate(news_url_list, 1):

    while True:
        try:
            if news_url_list.empty():
                break
                
            url = news_url_list.get()

            count = 0
            count_ += 1
            # print(f"{idx+1}번 프로세스 다음뉴스 댓글 크롤링 시작 :{url}\t{ii}/{len(news_url_list)}")
            print(f"{idx+1}번 프로세스 다음뉴스 댓글 크롤링 시작 :{url}\t{count_}/{news_url_list.qsize()}개남음\t--{split_date} 중 {now_split_index}/{split_index_count}")

            reply_texts = []

            driver.get(url)

            try:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="alex-header"]/em')) 
                )

            except TimeoutException:
                print("타임아웃")
                
                continue

            div = driver.find_element_by_xpath('//*[@id="alex-area"]')

            comment_count = driver.find_element_by_xpath('//*[@id="alex-header"]/em')

            if comment_count == '0':
                continue


            index = url.index("/v/") +3
            date = url[index:index+17]
            # if date[0:8] not in news_dic.keys():
            #     news_dic[date[0:8]] = []

            
            try:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="alex-area"]/div/div/div/div[3]/ul[1]/li[3]/button')) 
                )
                
                all_comments_mode = div.find_element_by_xpath('//*[@id="alex-area"]/div/div/div/div[3]/ul[1]/li[3]/button')
                all_comments_mode.send_keys(Keys.ENTER)

            except TimeoutException:
                # print("타임아웃")
                pass

            try:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="alex-area"]/div/div/div/div[3]/div[1]/button')) 
                )
                
                safe_bot_mode1 = div.find_element_by_xpath('//*[@id="alex-area"]/div/div/div/div[3]/div[1]/button')
                safe_bot_mode1.click()
                safe_bot_mode2 = div.find_element_by_xpath('//*[@id="alex-area"]/div/div/div[2]/div[2]/div/div[2]/dl/dd/button')
                safe_bot_mode2.click()
                safe_bot_mode3 = div.find_element_by_xpath('//*[@id="alex-area"]/div/div/div[2]/div[2]/div/a')
                safe_bot_mode3.click()

            except TimeoutException:
                # print("타임아웃")
                pass



            while True:
                try:
                    element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="alex-area"]/div/div/div/div[3]/div[3]/button')) 
                    )

                except TimeoutException:
                    print("more 버튼 없음 타임아웃")
                    
                    break

                
                more_btn = div.find_element_by_xpath('//*[@id="alex-area"]/div/div/div/div[3]/div[3]/button')
                # print("댓글 더보기 클릭")
                more_btn.click()

        
            # comments = div.find_elements_by_xpath('//li[**starts-with(id,"comment")**]')
            comments = div.find_elements_by_css_selector('li')
            reply_count = 0

            for i in range(len(comments)):
                comment = comments[i]
                this_id = comment.get_attribute('id')

                if not this_id.startswith('comment'):
                    continue

                is_exists_reply = True

                try:
                    element = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, f'//*[@id="{this_id}"]/div/div/span[1]/button/span')) 
                    )
                    reply_count = element.text
                    if element.text == "답글 작성":
                        is_exists_reply = False

                except TimeoutException:
                    print("답글 버튼 없음 타임아웃")

                
                try:
                    text = WebDriverWait(comment, 1).until(EC.presence_of_element_located((By.XPATH , f'//*[@id="{this_id}"]/div/p'))).text
                    reply_texts.append( text )
                    count += 1
                    # print(f"수집한 댓글 : {count}개")
                except:
                    print("댓 못가져와서 패스")
                    continue

                if is_exists_reply:
                    count2 = 0
                    reply_btn = comment.find_element_by_xpath(f'//*[@id="{this_id}"]/div/div/span[1]/button')
                    # reply_btn.click()
                    reply_btn.send_keys(Keys.ENTER)
                    
                    while True:
                        try:
                            element = WebDriverWait(driver, 1).until(
                                EC.presence_of_element_located((By.XPATH, f'//*[@id="{this_id}"]/div/div[2]/div[3]/button')) 
                            )

                        except TimeoutException:
                            # print("답글 더보기 버튼 없음 타임아웃")
                            break
                        
                        more_btn2 = div.find_element_by_xpath(f'//*[@id="{this_id}"]/div/div[2]/div[3]/button')
                        # print("답글 더보기 클릭")
                        more_btn2.click()
                    

                    try:
                        element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, f'//*[@id="{this_id}"]/div/div[2]')) 
                        )

                    except TimeoutException:
                        # print("답글 없음 타임아웃")
                        pass

                    try:
                        element = WebDriverWait(driver, 0.1).until(
                            EC.presence_of_element_located((By.XPATH, f'//*[@id="{this_id}"]/div/div[2]/div[2]/ul[2]')) 
                        )
                        
                        reply_div = div.find_element_by_xpath(f'//*[@id="{this_id}"]/div/div[2]')

                        replys = reply_div.find_elements_by_xpath(f'//*[@id="{this_id}"]/div/div[2]/div[2]/ul[2]/li')

                        for reply in replys:
                            try:
                                text = WebDriverWait(reply, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR , 'div[class="txt_reply"] > p'))).text
                                reply_texts.append( text )
                                count+=1
                                count2+=1
                                # print(f"수집한 댓글 : {count}개\t{reply_count}개 중 {count2}개 수집")

                            except:
                                print("답글 못가져와서 패스")
                                continue

                        
                        reply_btn.send_keys(Keys.ENTER)

                    except TimeoutException:
                        # print("답글 박스 타임아웃")
                        pass

            # for i in reply_texts:
            #     print(i)
            # print(f'수집한 댓글 : {len(reply_texts)}')
            

            news_dic[date[0:8]].update(
                {
                    url: {
                        'comments': reply_texts,
                        'emotions': []
                    }
                }
            )
        except TimeoutException:
            print("하 이타임아웃 또떴네")
            driver.quit()
            continue

    driver.quit()
    return