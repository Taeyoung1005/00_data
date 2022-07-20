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
import datetime
import json

from tqdm import trange

from utils.util import *
from crawlers.BaseCrawler import Crawler

class NaverCrawler(Crawler):
    chrome_options = None
    driver = None
    url_page_num = 0
    url = ''
    news_dic = {}
    news_queue = []

    # 생성자
    def __init__(self, driver_url, chrome_options):
        self.chrome_options = chrome_options
        
        self.driver_url = driver_url

    # 기사 링크 수집 메소드
    def crawlLinks(self, search, start_date, end_date):
        self.news_queue = []
        self.driver = webdriver.Chrome(self.driver_url, chrome_options=self.chrome_options)
        self.url_page_num = 0
        
        start_date_ = datetime.date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
        end_date_ = datetime.date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:])) + datetime.timedelta(days=1)
        for date_ in daterange(start_date_, end_date_):
            self.url_page_num = 1

            while True:
                date__ = str(date_).replace('-', '.')
                date___ = str(date_).replace('-', '')
                self.url = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search}&sort=2&photo=0&field=0&pd=3&ds={date__}&de={date__}&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:from{date___}to{date___},a:all&start={self.url_page_num}'
                
                    
                print(f"크롤링시작 URL:{self.url}")
                self.driver.get(self.url)

                try:
                    element = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="main_pack"]/div[2]'))
                        
                        # class = 'api_noresult_wrap'
                    )

                except TimeoutException:
                    print("타임아웃")
                    
                    break

                div, news = None, None

                div = self.driver.find_element_by_xpath('//*[@id="main_pack"]/div[2]')

                if div.get_attribute('class') == 'api_noresult_wrap':
                    break

                div = self.driver.find_element_by_xpath('//*[@id="main_pack"]/section/div/div[2]/ul')

                news = div.find_elements_by_css_selector('a[class="info"]')

                news = list(set(news))

                for i in range(len(news)):
                    link = None

                    link = news[i].get_attribute('href')

                    if link is None or link == "":
                        continue

                    link = link.replace('\n', '')
                    # if link.startswith("https://news.naver.com/main/") and link not in self.news_queue:
                    if news[i].text == '네이버뉴스' and link not in self.news_queue:
                        print(f'link : {link}')
                        try:
                            pass

                        except ValueError as e:
                            print("value Error", e, link)

                        else:
                            link = link.replace("?f=o", "")
                            self.news_queue.append(link)

                self.url_page_num += 10

        with open(f'result/naver_news/urls_{search}_naver_{start_date}_{end_date}.json.txt', 'w', encoding='utf8') as f:
            f.writelines('\n'.join(self.news_queue))

        self.news_queue = []
        self.driver.close()

    def crawlNews(self, search, start_date, end_date):
        self.news_queue = []
        news_dic = {}

        with open(f'result/naver_news/urls_{search}_naver_{start_date}_{end_date}.json.txt', 'r', encoding='utf8', newline='\n') as f:
            for row in f.readlines():
                row = row.replace('\n', '').replace('\r', '')
                self.news_queue.append(row)

        self.driver = webdriver.Chrome(self.driver_url, chrome_options=self.chrome_options)
        
        

        for url in self.news_queue:
            count = 0
            print(f"네이버뉴스 댓글 크롤링 시작 :{self.url}")

            reply_texts = []

            self.driver.get(url)

            try:
                element = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module"]/div[2]/div[2]/ul/li[1]/span')) 
                )

            except TimeoutException:
                print("타임아웃")
                
                break

            div = self.driver.find_element_by_xpath('//*[@id="cbox_module_wai_u_cbox_content_wrap_tabpanel"]')

            comment_count = self.driver.find_element_by_xpath('//*[@id="cbox_module"]/div[2]/div[2]/ul/li[1]/span')

            if comment_count == '0':
                continue


            # date = self.driver.find_element_by_xpath('//*[@id="main_content"]/div[1]/div[3]/div/span').text[:10].strip().replace('.', '')
            date = self.driver.find_element_by_css_selector('#main_content span[class="t11"]').text[:10].strip().replace('.', '')
            if date not in news_dic.keys():
                news_dic[date] = []

            
            # all_comments_mode = div.find_element_by_xpath('//*[@id="cbox_module_wai_u_cbox_sort_option_tab2"]')
            all_comments_mode = WebDriverWait(div, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module_wai_u_cbox_sort_option_tab2')) )
            all_comments_mode.click()

            safe_bot_mode1 = div.find_element_by_xpath('//*[@id="cbox_module"]/div[2]/div[7]/a')
            safe_bot_mode1.click()
            safe_bot_mode2 = div.find_element_by_xpath('//*[@id="cleanbot_dialog_checkbox_cbox_module"]')
            safe_bot_mode2.click()
            safe_bot_mode3 = div.find_element_by_xpath('/html/body/div[3]/div/div[2]/div[4]/button')
            safe_bot_mode3.click()

            while True:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module"]/div[2]/div[9]/a')) 
                    )
                    
                    more_btn = self.driver.find_element_by_xpath('//*[@id="cbox_module"]/div[2]/div[9]/a')
                    print("댓글 더보기 클릭")
                    more_btn.click()

                except TimeoutException:
                    print("more 버튼 없음 타임아웃")
                    
                    break

                except ElementNotInteractableException:
                    print("more 버튼 없음")
                    
                    break

            try:
                element = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cbox_module"]/div[2]/div[2]/ul/li[1]/span')) 
                )

            except TimeoutException:
                print("타임아웃")
                
                break

            div = self.driver.find_element_by_xpath('//*[@id="cbox_module_wai_u_cbox_content_wrap_tabpanel"]')
        
            # comments = div.find_elements_by_xpath('//li[**starts-with(id,"comment")**]')
            comments = div.find_elements_by_css_selector('ul>li')
            reply_count = 0

            for i in range(len(comments)):
                comment = comments[i]
                this_class = comment.get_attribute('class')

                if "comment_" not in this_class:
                    continue

                this_class = this_class.split(' ')[1]
                # print(f'this_class : {this_class}')

                is_exists_reply = True


                try:
                    element = WebDriverWait(comment, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'a[class="u_cbox_btn_reply"]')) 
                    )
                    reply_count = element.text
                    if element.text == "답글0":
                        is_exists_reply = False

                except TimeoutException:
                    print("답글 버튼 없음 타임아웃")
                    is_exists_reply = False

                
                try:
                    text = WebDriverWait(comment, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR , f'div[class="u_cbox_text_wrap"]'))).text
                    if text != "작성자에 의해 삭제된 댓글입니다.":
                        reply_texts.append( text )
                        count += 1
                        print(f"수집한 댓글 : {count}개\t{text}")
                except:
                    print("댓 못가져와서 패스")
                    continue

                if is_exists_reply:
                    count2 = 0
                    reply_btn = comment.find_element_by_css_selector(f'a[class="u_cbox_btn_reply"]')
                    # reply_btn.click()
                    reply_btn.send_keys(Keys.ENTER)
                    
                    while True:
                        try:
                            element = WebDriverWait(comment, 1).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, f'a[class="u_cbox_btn_more"]')) 
                            )
                            
                            more_btn2 = comment.find_element_by_css_selector(f'a[class="u_cbox_btn_more"]')
                            # print("답글 더보기 클릭")
                            more_btn2.send_keys(Keys.ENTER)

                        except:
                            # print("답글 더보기 버튼 없음 타임아웃")
                            break


                    replys = []
                    try:
                        replys = WebDriverWait(reply, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR , f'li[class="u_cbox_comment"]')))
                    except:
                        pass

                    for reply in replys:
                        try:
                            text = WebDriverWait(reply, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR , 'span[class="u_cbox_contents"] > p'))).text
                            if text != "작성자에 의해 삭제된 댓글입니다.":
                                reply_texts.append( text )
                                count+=1
                                count2+=1
                                print(f"수집한 댓글 : {count}개\t{reply_count}개 중 {count2}개 수집")

                        except:
                            print("답글 못가져와서 패스")
                            continue

                    
                    # reply_btn.send_keys(Keys.ENTER)
            # for i in reply_texts:
            #     print(i)
            print(f'수집한 댓글 : {len(reply_texts)}')
            
            news_dic[date[0:8]].append(
                {
                    url: {
                        'comments': reply_texts,
                        'emotions': []
                    }
                }
            )

        self.driver.close()
        
        with open(f'result/naver_news/news_{search}_naver_{start_date}_{end_date}.json.txt', 'w', encoding='utf8') as f:
            json.dump(news_dic, f, indent=4, sort_keys=True, ensure_ascii=False)