from utils.processing_json import Processing_json
from utils.predict import Predict 
import matplotlib.pyplot as plt
import datetime
import csv
from matplotlib import font_manager, rc 
fn_name = font_manager.FontProperties(fname='c:/Windows/Fonts/malgun.ttf').get_name()
rc('font',family=fn_name)


search = "한동훈"
start_date = "20220626"
end_date =   "20220630"

processing = Processing_json(f'../main_program/result/naver_news/news_{search}_naver_{start_date}_{end_date}__{end_date[:6]}.json')
processed_dic = processing.dateNList()

print(processed_dic)

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
        
        positive = 0
        negative = 0
    return result_dic,result_happy,result_bad,result_dic2   #ex) {'20220623':70, '20220624':-1(결측값)}

result,happy_num,bad_num,result2 = dic_to_result(processed_dic)
all_num = [x+y for x,y in zip(happy_num, bad_num)]

print("감성분석 결과 입니다.")
print(result)
print(happy_num)
print(bad_num)
print(all_num)

per = []
per2 = []

for d in result.keys():
    if result[str(d)] == -1 :
        per.append(0)
    else :
        per.append(result[str(d)])

for d in result2.keys():
    if result2[str(d)] == -1 :
        per2.append(0)
    else :
        per2.append(result2[str(d)])


print(per)
print(per2)

# 그래프 그리기--------------------------------------------
startDate = start_date
lastDate = end_date

# 각 날짜를 리스트에 끊어서 저장
# ex) 20220627 = ['2', '0', '2', '2', '0', '6', '2', '7']
start_dateList = []
for y in (startDate):
    start_dateList.append(y)
last_dateList = []
for y in (lastDate):
    last_dateList.append(y)

# string 타입의 리스트를 int 타입으로 변환
start_dateList = list(map(int, start_dateList))
last_dateList = list(map(int, last_dateList))

# 시작 날짜 정리
thousand = start_dateList[0] * 1000
hundred = start_dateList[1] * 100
yten = start_dateList[2] * 10
yone = start_dateList[3]
mten = start_dateList[4] * 10
mone = start_dateList[5]
dten = start_dateList[6] * 10
done = start_dateList[7]
startYear = thousand + hundred + yten + yone
startMonth = mten + mone
startDay = dten + done

# 마지막 날짜 정리
thousand = last_dateList[0] * 1000
hundred = last_dateList[1] * 100
yten = last_dateList[2] * 10
yone = last_dateList[3]
mten = last_dateList[4] * 10
mone = last_dateList[5]
dten = last_dateList[6] * 10
done = last_dateList[7]
lastYear = thousand + hundred + yten + yone
lastMonth = mten + mone
lastDay = dten + done

# datetime으로 적용
startday = datetime.date(startYear, startMonth, startDay)
lastday = datetime.date(lastYear, lastMonth, lastDay)

# 두 날짜간 차이 계산
dateResult = startday - lastday
dateResult = abs(dateResult)

# 날짜형 -> 문자형 변환 후 날짜간 차이를 정수형으로 저장
strDate = str(dateResult)
sstrDate = strDate.split(' ')
intDate = int(sstrDate[0])      # 날짜간 차이(정수형)

monthList = []      # 사용자가 지정한 month의 리스트
dateList = []       # 사용자가 지정한 day의 리스트
yearList = []

#   1월 2월 3월 4월  5월 6월 7월 8월 9월 10월 11월 12월
m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31,  30,  31]

# 같은 달일때
if startMonth == lastMonth and intDate < m[startMonth-1] :
    for i in range(startDay,lastDay+1) :
        dateList.append(i)
        monthList.append(startMonth)
        yearList.append(startYear)
# 다른 달일때
elif startMonth != lastMonth :
    # 다른 연도
    if startYear != lastYear :
        m_m = lastMonth - startMonth
        m_m = abs(abs(m_m)-12)+1
        for i in range(m_m) :
            if i == 0 :
                for j in range(startDay,m[((startMonth-1)+i)-12]+1):
                    dateList.append(j)
                    monthList.append((startMonth-1)+i+1)
                    yearList.append(startYear)

            elif 0<i<m_m-1:
                for j in range(1,m[((startMonth-1)+i)-12]+1):
                    dateList.append(j)
                    monthList.append(i)
                    
                    if ((startMonth-1)+i-12+1) < startMonth :
                        yearList.append(lastYear)
                    

            else :
                for j in range(1,lastDay+1):
                    dateList.append(j)
                    yearList.append(lastYear)
                    monthList.append(i)            
    # 같은 연도
    else :
        m_m = lastMonth - startMonth +1
        for i in range(m_m) :
            if i == 0 :
                for j in range(startDay,m[startMonth-1]+1):
                    dateList.append(j)
                    monthList.append(startMonth)
                    yearList.append(startYear)
            elif 0<i<m_m-1:
                for j in range(1,m[startMonth-1+i]+1):
                    dateList.append(j)
                    monthList.append((startMonth-1)+1)
                    yearList.append(startYear)
            else :
                for j in range(1,lastDay+1):
                    dateList.append(j)
                    monthList.append((lastMonth-1)+1)
                    yearList.append(startYear)

# 정수형 리스트를 문자열 리스트로 변환
str_month_list = list(map(str, monthList))
str_date_list = list(map(str, dateList))
str_year_list = list(map(str, yearList))

# n월 n일 형태로 출력
listLen = len(str_month_list)
resultList = []
for i in range(listLen):
    if len(str_month_list[i]) != 2 and len(str_date_list[i]) != 2 :
        resultList.append(str_year_list[i]+"0"+str_month_list[i]+ "0"+str_date_list[i])
    elif len(str_month_list[i]) != 2 and len(str_date_list[i]) == 2 :
        resultList.append(str_year_list[i]+"0"+str_month_list[i]+str_date_list[i])
    elif len(str_month_list[i]) == 2 and len(str_date_list[i]) != 2 :
        resultList.append(str_year_list[i]+str_month_list[i]+"0"+str_date_list[i])
    else :
        resultList.append(str_year_list[i]+str_month_list[i]+ str_date_list[i])

#html에 보내줄 값 저장
happy = happy_num
bad = bad_num
all_n = all_num
search_day = start_date + end_date + search 
print(resultList)

#csv저장 = DB역할 
#with open(f'../main_program/static/search.csv', 'a',newline='', encoding='utf8') as f:
#    wr = csv.writer(f)
#    wr.writerow([search,start_date,end_date])

#그래프 그린후 저장
#plt.clf()

#그래프
plt.plot(resultList,per,color='blue',linestyle='-',marker='o')
plt.plot(resultList,per2,color='red',linestyle='-',marker='o')
#plt.plot(resultList,bad,color='red',linestyle='-',marker='o')
#resultList = [i for i in resultList[1:len(resultList)] if int(i)%2 == 0]
plt.xticks(resultList, rotation='70')  # x축 라벨의 이름 pow지움
plt.ylim([0,100])
plt.title(f'{search} 일별 동향 그래프', )  # 그래프 제목 설정
#plt.ylabel('퍼센트',)  # y축에 설명 추가
plt.tight_layout()
plt.gca().spines['right'].set_visible(False) #오른쪽 테두리 제거
plt.gca().spines['top'].set_visible(False) #위 테두리 제거
plt.gca().spines['left'].set_visible(False) #왼쪽 테두리 제거
plt.gca().spines['bottom'].set_color('#00517C') #x축 색상
#plt.gca().set_facecolor('#E6F0F8') #배경색
plt.legend(['긍정','부정'], title_fontsize = 10)
#plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}graph.jpg')
plt.show()
plt.clf()

# 관심도 그래프
plt.plot(resultList,all_n,color='green',linestyle='-',marker='o')
plt.xticks(resultList, rotation='70')  # x축 라벨의 이름 pow지움
plt.ylim([0,len(all_n)])
plt.title(f'{search} 일별 관심도 그래프', )  # 그래프 제목 설정
plt.tight_layout()
plt.gca().spines['right'].set_visible(False) #오른쪽 테두리 제거
plt.gca().spines['top'].set_visible(False) #위 테두리 제거
plt.gca().spines['left'].set_visible(False) #왼쪽 테두리 제거
plt.gca().spines['bottom'].set_color('#00517C') #x축 색상
plt.legend(['댓글 총 개수'], title_fontsize = 10)
#plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}all.jpg')
plt.show()
plt.clf()
'''
plt.clf()
# 부정 그래프
plt.plot(resultList,bad,color='red',linestyle='-',marker='o')
plt.xticks(resultList, rotation='90')  # x축 라벨의 이름 pow지움
plt.title(f'negative graph', )  # 그래프 제목 설정
plt.ylabel('bad_num',)  # y축에 설명 추가
plt.tight_layout()
#plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}bad.jpg')
plt.show()
plt.clf()
# 관심도 그래프
plt.plot(resultList,all_n,color='green',linestyle='-',marker='o')
plt.xticks(resultList, rotation='90')  # x축 라벨의 이름 pow지움
plt.title(f'interest index graph', )  # 그래프 제목 설정
plt.ylabel('interest index',)  # y축에 설명 추가
plt.tight_layout()
#plt.savefig(f'../main_program/static/images/{start_date}{end_date}{search}all.jpg')
plt.show()
plt.clf()
'''