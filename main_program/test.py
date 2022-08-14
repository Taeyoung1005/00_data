from utils.processing_json import Processing_json
from utils.predict import Predict 
import matplotlib.pyplot as plt
import datetime
import csv
from matplotlib import font_manager, rc 
import numpy as np
fn_name = font_manager.FontProperties(fname='c:/Windows/Fonts/malgun.ttf').get_name()
rc('font',family=fn_name)


search = "윤석열+국정수행"
start_date = "20220701"
end_date =   "20220714"

processing = Processing_json(f'../main_program/result/naver_news/news_{search}_naver_{start_date}_{end_date}.json')
processed_dic = processing.dateNList()

# 전처리 후 예측
def dic_to_result(processed_dic):   
    predict = Predict()

    result_dic = {}
    result_dic2 = {}
    result_happy = []
    result_bad = []

    for key in processed_dic.keys():
        missing_value = False
        positive = 0
        negative = 0
        if len(processed_dic[key]) == 0:
            missing_value = True
        for comment in processed_dic[key]:
            if predict.predict(comment):
                positive +=1
            else:
                negative +=1
        if missing_value:
            result_dic[key] = -1
            result_dic2[key] = -1
        else:
            result_dic[key] = round(positive/(positive+negative)*100)
            result_dic2[key] = round(negative/(positive+negative)*100)
        
        result_happy.append(positive)
        result_bad.append(negative)
    return result_dic,result_happy,result_bad,result_dic2   #ex) {'20220623':70, '20220624':-1(결측값)}

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
plt.plot(resultList, positive_rate, color='blue', linestyle='-')
plt.plot(resultList, negative_rate, color='red', linestyle='-')
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
plt.legend(['긍정','부정'], title_fontsize = 10, loc='upper left')
#plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}graph.jpg')
plt.show()
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
plt.legend(['댓글 총 개수'], title_fontsize = 10, loc='upper left')
#plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}all.jpg')
plt.show()
plt.clf()