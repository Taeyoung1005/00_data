# 
# NaverNewsCrawler.py
# Web crawling program for Naver News
# Author : Ji-yong219
# Project Start:: 2021.07.24
# Last Modified from Ji-yong 2021.07.27
#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, StaleElementReferenceException
from bs4 import BeautifulSoup as bs
import grequests
import datetime
import json
import sys
import re

from time import sleep
from tqdm import trange

from utils.util import *
from utils.FeedbackCounter import FeedbackCounter


from multiprocessing import Process, Manager, cpu_count
import numpy as np

import warnings
# 경고메세지 끄기
warnings.filterwarnings(action='ignore')

def crawlLinks( search, start_date, end_date, driver_url, chrome_options):
    num_of_cpu = cpu_count()

    manager = Manager()
    url_list = manager.list()
    
    start_date_ = datetime.date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
    end_date_ = datetime.date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:])) + datetime.timedelta(days=1)

    date_list = [i for i in daterange(start_date_, end_date_)]
    ##이쪽에서 중복 제거
    print(date_list)
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

    with open(f'result/naver_news/txt/urls_{search}_naver_{start_date}_{end_date}.txt', 'w', encoding='UTF-8') as f:
        f.writelines('\n'.join(list(set(list(url_list)))))


# 기사 링크 수집 메소드
def crawlLinksProcess(date_list, driver_url, chrome_options, search, url_list):
    driver = webdriver.Chrome(driver_url, chrome_options=chrome_options)
    url_page_num = 0
    
    for date_ in date_list:
        url_page_num = 1

        for _ in range(2):
            date__ = str(date_).replace('-', '.')
            date___ = str(date_).replace('-', '')
            url = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search}&sort=2&photo=0&field=0&pd=3&ds={date__}&de={date__}&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:from{date___}to{date___},a:all&start={url_page_num}'
            
                
            print(f"크롤링시작 URL:{url}")
            driver.get(url)

            try:
                element = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="main_pack"]/div[2]'))
                    
                    # class = 'api_noresult_wrap'
                )

            except TimeoutException:
                print("타임아웃")
                
                break

            div, news = None, None

            div = driver.find_element(By.XPATH,'//*[@id="main_pack"]/div[2]')

            if div.get_attribute('class') == 'api_noresult_wrap':
                break

            div = driver.find_element(By.XPATH,'//*[@id="main_pack"]/section/div/div[2]/ul')

            news = div.find_elements(By.CSS_SELECTOR,'a[class="info"]')

            news = list(set(news))

            for i in range(len(news)):
                link = None

                link = news[i].get_attribute('href')

                if link is None or link == "":
                    continue

                link = link.replace('\n', '')
                # if link.startswith("https://news.naver.com/main/") and link not in self.news_queue:
                if news[i].text == '네이버뉴스' and link not in url_list:
                    print(f'link : {link}')
                    try:
                        pass

                    except ValueError as e:
                        print("value Error", e, link)

                    else:
                        link = link.replace("?f=o", "")
                        url_list.append(link)

            url_page_num += 10

    driver.quit()
    return


def crawlNews( search, start_date, end_date, driver_url, chrome_options):
    num_of_cpu = cpu_count()

    manager = Manager()

    news_queue = []

    with open(f'result/naver_news/txt/urls_{search}_naver_{start_date}_{end_date}.txt', 'r', encoding='UTF-8', newline='\n') as f:
        for row in f.readlines():
            row = row.replace('\n', '').replace('\r', '')
            news_queue.append(row)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
    
    fbc = FeedbackCounter( len(news_queue) )
    
    rs = (grequests.get(news_queue[i], headers=headers, callback=fbc.feedback) for i in trange(len(news_queue), file=sys.stdout, desc='get Grequest'))
    a = grequests.map(rs)

    news_queue_with_month = {}

    for i in trange(len(a), file=sys.stdout, desc='get html parser from bs4'):
        soup = None

        if a[i] is not None:
            soup = (a[i].url,bs(a[i].content, 'html.parser'))

        if soup is None or len(soup)<2:
            continue

        url, soup = soup

        if soup is None:
            print("soup 없어서 continue")
            continue

        
        try:
            date = soup.select('._ARTICLE_DATE_TIME')[0]
            date_ = date.get_text()
            
            p = re.compile(r"\d+[.]+\d+[.]+\d+[.]")
            m = p.search(date_)
            date__ = m.group(0).replace('.', '')
            month = date__[:6]
            
            if month in news_queue_with_month.keys():
                news_queue_with_month[month].append((date__, url))
            else:
                news_queue_with_month[month] = []

        except:
            continue


    split_index_count = 10
    
    for i in news_queue_with_month.keys():

        news_queue_with_month[i] = list(np.array_split(np.array(news_queue_with_month[i]), split_index_count))
        
        news_dic = manager.dict()

        
        for idx2, j in enumerate(news_queue_with_month[i], 1):
            for date, jj in j:
                if date not in news_dic.keys():
                    news_dic[date] = manager.dict()

            # title_list = np.array_split(np.array(news_queue), num_of_cpu)
            title_list = manager.Queue()

            [title_list.put(ii) for date, ii in j]
            
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
                    continue

        with open(f'result/naver_news/comment_seperate/news_{search}_naver_{start_date}_{end_date}__{i}.json', 'w', encoding='UTF-8') as f:
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
            # print(f"{idx+1}번 프로세스 네이버뉴스 댓글 크롤링 시작 :{url}\t{ii}/{len(news_url_list)}")
            print(f"{idx+1}번 프로세스 네이버 뉴스 댓글 크롤링 시작 :{url}\t{count_}/{news_url_list.qsize()}개남음\t--{split_date} 중 {now_split_index}/{split_index_count}")

            reply_texts = []

            driver.get(url)

            try:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module"]/div[2]/div[2]/ul/li[1]/span')) 
                )

            except TimeoutException:
                print("타임아웃")
                
                continue

            div = driver.find_element(By.XPATH,'//*[@id="cbox_module_wai_u_cbox_content_wrap_tabpanel"]')

            comment_count = driver.find_element(By.XPATH,'//*[@id="cbox_module"]/div[2]/div[2]/ul/li[1]/span')

            if comment_count == '0':
                continue


            date = driver.find_element(By.CSS_SELECTOR,'#ct_wrap ._ARTICLE_DATE_TIME')
            date_ = date.text
            
            p = re.compile(r"\d+[.]+\d+[.]+\d+[.]")
            m = p.search(date_)
            date__ = m.group(0).replace('.', '')
            # if date not in news_dic.keys():
            #     news_dic[date] = []

            
            
            try:
                all_comments_mode = WebDriverWait(div, 2).until(
                    # EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module_wai_u_cbox_sort_option_tab2')) 
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module_wai_u_cbox_content_wrap_tabpanel"]')) 
                )
                all_comments_mode.click()

            except TimeoutException:
                print("타임아웃")
                
                pass

            safe_bot_mode1 = div.find_element(By.XPATH,'//*[@id="cbox_module"]/div[2]/div[7]/a')
            safe_bot_mode1.click()
            safe_bot_mode2 = div.find_element(By.XPATH,'//*[@id="cleanbot_dialog_checkbox_cbox_module"]')
            safe_bot_mode2.click()
            safe_bot_mode3 = div.find_element(By.XPATH,'/html/body/div[2]/div/div[2]/div[4]/button')
            safe_bot_mode3.click()

            #더보기 없애기
            # while True:
            #     try:
            #         element = WebDriverWait(driver, 2).until(
            #             EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module"]/div[2]/div[9]/a')) 
            #         )
                    
            #         more_btn = driver.find_element_by_xpath('//*[@id="cbox_module"]/div[2]/div[9]/a')
            #         print("댓글 더보기 클릭")
            #         # more_btn.click()
            #         more_btn.send_keys(Keys.ENTER)

            #     except TimeoutException:
            #         print("more 버튼 없음 타임아웃")
                    
            #         break

            #     except ElementNotInteractableException:
            #         print("more 버튼 없음")
                    
            #         break

            try:
                element = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module"]/div[2]/div[2]/ul/li[1]/span')) 
                )

            except TimeoutException:
                print("타임아웃")
                
                break

            div = driver.find_element(By.XPATH,'//*[@id="cbox_module_wai_u_cbox_content_wrap_tabpanel"]')
        
            # comments = div.find_elements_by_xpath('//li[**starts-with(id,"comment")**]')
            sleep(3)
            comments = div.find_elements(By.CSS_SELECTOR,'ul>li')
            # sleep(3)
            # reply_count = 0

            for i in range(len(comments)):
                comment = comments[i]
                this_class = comment.get_attribute('class')

                if "comment_" not in this_class:
                    continue

                this_class = this_class.split(' ')[1]
                # print(f'this_class : {this_class}')

                is_exists_reply = True


                # try:
                #     element = WebDriverWait(comment, 1).until(
                #         EC.presence_of_element_located((By.CSS_SELECTOR, f'a[class="u_cbox_btn_reply"]')) 
                #     )
                #     reply_count = element.text
                #     if element.text == "답글0":
                #         is_exists_reply = False

                # except TimeoutException:
                #     print("답글 버튼 없음 타임아웃")
                #     is_exists_reply = False

                
                try:
                    text = WebDriverWait(comment, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR , f'div[class="u_cbox_text_wrap"]'))).text
                    if text != "작성자에 의해 삭제된 댓글입니다." and text != "클린봇이 부적절한 표현을 감지한 댓글입니다." and text != "운영규정 미준수로 인해 삭제된 댓글입니다.":
                        reply_texts.append( text )
                        count += 1
                        # print(f"수집한 댓글 : {count}개\t{text}")
                except:
                    print("댓 못가져와서 패스")
                    continue

                # if is_exists_reply:
                #     count2 = 0
                #     reply_btn = comment.find_element_by_css_selector(f'a[class="u_cbox_btn_reply"]')
                #     # reply_btn.click()
                #     reply_btn.send_keys(Keys.ENTER)
                    
                #     # while True:
                #     #     try:
                #     #         element = WebDriverWait(comment, 1).until(
                #     #             EC.presence_of_element_located((By.CSS_SELECTOR, f'a[class="u_cbox_btn_more"]')) 
                #     #         )
                            
                #     #         more_btn2 = comment.find_element_by_css_selector(f'a[class="u_cbox_btn_more"]')
                #     #         # print("답글 더보기 클릭")
                #     #         more_btn2.send_keys(Keys.ENTER)

                #     #     except:
                #     #         # print("답글 더보기 버튼 없음 타임아웃")
                #     #         break


                # replys = []
                # try:
                #     replys = WebDriverWait(reply, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR , f'li[class="u_cbox_comment"]')))

                #     for reply in replys:
                #         try:
                #             text = WebDriverWait(reply, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR , 'span[class="u_cbox_contents"] > p'))).text
                #             if text != "작성자에 의해 삭제된 댓글입니다." and text != "클린봇이 부적절한 표현을 감지한 댓글입니다." and text != "운영규정 미준수로 인해 삭제된 댓글입니다.":
                #                 reply_texts.append( text )
                #                 count+=1
                #                 count2+=1
                #                 print(f"수집한 댓글 : {count}개\t{reply_count}개 중 {count2}개 수집")

                #         except:
                #             print("답글 못가져와서 패스")
                #             continue
                # except:
                #     pass

                    
                #     # reply_btn.send_keys(Keys.ENTER)
            # for i in reply_texts:
            #     print(i)
            # print(f'수집한 댓글 : {len(reply_texts)}')
            
            news_dic[date__[0:8]].update(
                { ##original
                    url: {
                        'comments': reply_texts,
                        # 'emotions': []
                    }
                }
            )
        except TimeoutException:
            print("하 이타임아웃 또떴네")
            driver.quit()
            continue

    driver.quit()
    return