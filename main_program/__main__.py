from flask import Flask, request, render_template
import threading
import start
from datetime import datetime
import json
app = Flask(__name__)
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import random
import os, glob, time
import start
from tqdm import tqdm
from matplotlib import font_manager, rc 
import numpy as np
fn_name = font_manager.FontProperties(fname='c:/Windows/Fonts/malgun.ttf').get_name()
rc('font',family=fn_name)
import csv
import comment_txt
from openpyxl import Workbook

from utils.predict import Predict

#누적 그래프 결과 페이지
@app.route('/resultPage', methods=['GET', 'POST'])
def result() :
    if request.method == 'GET':
        l = []
        
        # csv파일 읽어서 html로 값 전송
        with open(f'../main_program/static/search.csv', 'r', newline='', encoding='UTF-8') as f:
            re = csv.reader(f)

            for i in re :
                l.append(i[1]+i[2]+i[0])
            l.reverse()
            
            # print(l)
        return render_template("./resultPage.html", search_list = l)
    
    if request.method == 'POST':
        print("POST가 실행 되었습니다. -------------------------")
        search_r = request.form.get('keyword').replace(' ', '+')
        start_date_r = request.form.get('start_date')
        end_date_r = request.form.get('end_date')

        start_date_r = start_date_r[:4] + start_date_r[5:7] + start_date_r[8:]
        end_date_r = end_date_r[:4] + end_date_r[5:7] + end_date_r[8:]

        print("[검색어, 날짜가 입력 되었습니다.]")
        print(search_r, start_date_r, end_date_r)

        threading.Thread(target=start.main, args=(search_r, start_date_r, end_date_r,)).start()

        return render_template("./loding.html", search = search_r ,start_date = start_date_r ,end_date = end_date_r)

#사이트 설명 페이지
@app.route('/guide', methods=['GET', 'POST'])
def guide() :
    if request.method == 'GET':
        return render_template("./guide.html")

#모델 실행이 끝난 후 그래프 보여주는 페이지
@app.route('/graph', methods=['GET', 'POST'])
def graph():
    file = f'../main_program/result/naver_news/news_{search}_naver_{start_date}_{end_date}.json'
    while True :
        if os.path.isfile(file) :
            print("-"*30)
            print("[ json파일이 생성되었습니다. ]")
            print("-"*30)
            print("[ 감성분석을 시작합니다. ]")
            print("-"*30)

            with open(f'result/naver_news/news_{search}_naver_{start_date}_{end_date}.json', 'r', encoding='UTF-8') as f:
                processed_dic = json.load(f)

            # 전처리 후 예측
            def dic_to_result(processed_dic):   
                predict = Predict()

                write_wb = Workbook()
                write_ws = write_wb.create_sheet('버트 전처리')
                write_ws = write_wb.active
                
                result_dic = {}
                result_dic2 = {}
                result_happy = []
                result_bad = []
                number = 1

                for date in processed_dic:
                    link_exitence = True
                    text_exitence = False
                    positive = 0
                    negative = 0
                    if len(processed_dic[date]) == 0: #링크가 없으면 결측값 
                        link_exitence = False
                    else:
                        for url in processed_dic[date]:
                            for comments in processed_dic[date][url]:
                                if len(processed_dic[date][url][comments]) == 0: #링크는 있는데 댓글이 없으면 결측값
                                    if text_exitence != True:
                                        text_exitence = False
                                else:
                                    text_exitence = True
                                    for i in range(len(processed_dic[date][url][comments])):
                                        result = predict.predict(processed_dic[date][url][comments][i])
                                        if result == 1:
                                            positive +=1
                                        else:
                                            negative +=1

                                        write_ws[f'A{number}'] = result
                                        write_ws[f'B{number}'] = processed_dic[date][url][comments][i]
                                        number += 1
                        
                    if link_exitence == False or text_exitence == False:
                        result_dic[date] = -1
                        result_dic2[date] = -1
                    else:
                        result_dic[date] = round(positive/(positive+negative)*100)
                        result_dic2[date] = round(negative/(positive+negative)*100)
                    
                    result_happy.append(positive)
                    result_bad.append(negative)

                write_wb.save(f'../main_program/result/naver_news/bert_result/{search}_naver_{start_date}_{end_date}.xlsx')
                return result_dic, result_happy, result_bad, result_dic2   #ex) {'20220623':70, '20220624':-1(결측값)}

            result,happy_num,bad_num,result2 = dic_to_result(processed_dic)
            all_num = [x+y for x,y in zip(happy_num, bad_num)]

            print("감성분석 결과 입니다.")
            print(result)
            print(happy_num)
            print(bad_num)
            print(all_num)

            positive_rate = []
            negative_rate = []

            for d in result.keys():
                if result[str(d)] == -1 :
                    positive_rate.append(0)
                else :
                    positive_rate.append(result[str(d)])

            for d in result2.keys():
                if result2[str(d)] == -1 :
                    negative_rate.append(0)
                else :
                    negative_rate.append(result2[str(d)])


            print(positive_rate)
            print(negative_rate)

            # 그래프 그리기--------------------------------------------

            syear = start_date[0:4]
            smonth = start_date[4:6]
            sday = start_date[6:]
            strStartDate = syear + "-" + smonth + "-" + sday

            lyear = end_date[0:4]
            lmonth = end_date[4:6]
            lday = end_date[6:]
            strLastDate = lyear + "-" + lmonth + "-" + lday

            dateStartDate = np.array(strStartDate, dtype=np.datetime64)
            dateLastDate = np.array(strLastDate, dtype=np.datetime64)
            c = dateLastDate - dateStartDate

            tempList = [dateStartDate + np.arange(c + 1)]
            resultList = tempList[0]
            resultList = resultList.tolist()

            all_n = all_num
            search_day = start_date + end_date + search 
            
            print(resultList)

            #csv저장 = DB역할 
            with open(f'../main_program/static/search.csv', 'a', newline='', encoding='UTF-8') as f:
                wr = csv.writer(f)
                wr.writerow([search,start_date,end_date])
            
            #그래프 그린후 저장

            plt.clf()
            #그래프
            plt.plot(resultList, positive_rate, color='blue', linestyle='-', marker='o')
            plt.plot(resultList, negative_rate, color='red', linestyle='-', marker='o')
            #plt.plot(resultList,bad,color='red',linestyle='-',marker='o')
            #resultList = [i for i in resultList[1:len(resultList)] if int(i)%2 == 0]
            plt.xticks(resultList, rotation='70')  # x축 라벨의 이름 pow지움
            plt.ylim([0,100])
            #plt.title(f'{search} 일별 동향 그래프', )  # 그래프 제목 설정
            #plt.ylabel('퍼센트',)  # y축에 설명 추가
            plt.tight_layout()
            plt.gca().spines['right'].set_visible(False) #오른쪽 테두리 제거
            plt.gca().spines['top'].set_visible(False) #위 테두리 제거
            plt.gca().spines['left'].set_visible(False) #왼쪽 테두리 제거
            plt.gca().spines['bottom'].set_color('#00517C') #x축 색상
            #plt.gca().set_facecolor('#E6F0F8') #배경색
            plt.legend(['긍정률','부정률'], title_fontsize = 10, loc='upper left')
            plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}graph.jpg')
            plt.clf()
            # 관심도 그래프
            plt.plot(resultList, all_n,color='green', linestyle='-')
            plt.xticks(resultList, rotation='70')  # x축 라벨의 이름 pow지움
            #plt.title(f'{search} 일별 관심도 그래프', )  # 그래프 제목 설정
            plt.ylim([0,max(all_n)])
            plt.tight_layout()
            plt.gca().spines['right'].set_visible(False) #오른쪽 테두리 제거
            plt.gca().spines['top'].set_visible(False) #위 테두리 제거
            plt.gca().spines['left'].set_visible(False) #왼쪽 테두리 제거
            plt.gca().spines['bottom'].set_color('#00517C') #x축 색상
            plt.legend(['관심도'], title_fontsize = 10, loc='upper left')
            plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}all.jpg')
            plt.clf()
            
            h = 0
            b = 0
            
            for i in happy_num :
                h += i
            for i in bad_num :
                b += i

            color = "prism"
            #원형 그래프 생성
            if len(all_n) != 0 and h != 0 and b != 0:
                plt.figure(dpi=200)
                circle_happy = h/(h + b) * 100 
                circle_bad = b/(h + b) * 100
                c_list = []
                l_list = ["긍정","부정"]
                colors = ['#288BAB','#ff9999']
                explode = [0.1,0.1]
            
                c_list.append(circle_happy)
                c_list.append(circle_bad)
                
                plt.pie(c_list, labels=l_list, colors=colors, autopct='%.1f%%', startangle=260, counterclock=False, shadow=True, explode=explode, textprops={'size':18}) 
                plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}circle.jpg')
                plt.clf()

                # 긍정이 많은지 부정이 많은지 확인 => 워드 클라우드에 사용
                if circle_happy > circle_bad :
                    color = "Blues"
                elif circle_happy < circle_bad:
                    color = "Reds"
                else:
                    color = "prism"
            
            #워드 클라우드 생성
            rank = comment_txt.makeCommentTxt.comment(search, start_date, end_date, color)
            print(rank)
            return render_template("./graph_page.html", value = result,happy_value = happy_num,bad_value = bad_num, value_search = search, search_day = search_day, start_date = start_date, end_date = end_date, rank = rank)

#중간 로딩 페이지
@app.route('/loding', methods=['GET', 'POST'])
def lode():
    if request.method == 'GET':
        file = f'../main_program/result/naver_news/news_{search}_naver_{start_date}_{end_date}.json'
        while True :
            if os.path.isfile(file) :
                return render_template("./loding2.html")

#처음 시작 페이지
@app.route('/', methods=['GET', 'POST'])
def goo():
    
    if request.method == 'GET':
        return render_template("./index.html")

    elif request.method == 'POST':
        global search
        global start_date
        global end_date
        global file
       
        search = request.form.get('keyword').replace(' ', '+')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        start_date = start_date[:4] + start_date[5:7] + start_date[8:]
        end_date = end_date[:4] + end_date[5:7] + end_date[8:]
        print("[검색어, 날짜가 입력 되었습니다.]")
        print(search, start_date, end_date)

        #검색 횟수 저장 csv (인기검색어) 잠정 보류
        #with open(f'../main_program/static/search_num.csv', 'a',newline='', encoding='utf8') as f:
        #        wr = csv.writer(f)
        #        wr.writerow([search])
        #총 검색 횟수 계산
        #search_num_list = []
        #search_num_list2 = []
        #with open(f'../main_program/static/search_num.csv', 'r',newline='', encoding='utf8') as f:
        #    re = csv.reader(f)
        #    
        #    for i in re :
        #        
        #        search_num_list.append(i[0])

        #        if i[0] not in search_num_list2 :
        #            search_num_list2.append(i[0])
                

        #        #for j in range(len(search_num_list2)) :
        #        if i[0] 
        #        s = str(i[0])+"," + str(search_num_list.count(i[0]))

        #        print(s)
                #for j in range(search_num_list)
                #if i[0] in search_num_list :
                #   s = str(i[0]) + str 
                #print(search_num_list)
                #print(s)
            

        #크롤러 실행 
        file = f'../main_program/result/naver_news/news_{search}_naver_{start_date}_{end_date}.json'
        threading.Thread(target=start.main, args=(search, start_date, end_date,)).start()

        print("[ 스레드 크롤러가 실행 되었습니다. ]")

        return render_template("./loding.html", search = search ,start_date = start_date,end_date = end_date,file = file)

if __name__ == "__main__":
    # from gevent import monkey
    # monkey.patch_all()
    app.run(host="0.0.0.0", port="80",debug=False, threaded=True )