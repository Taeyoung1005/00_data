import json
from word_cloud import Word_Cloud

class makeCommentTxt:
    def comment(search, start_date, end_date, color):
        address = "../main_program/WordCloud_txt"

        #json파일 불러오기
        with open(f'../main_program/result/naver_news/news_{search}_naver_{start_date}_{end_date}.json', 'r', encoding='UTF-8') as f:
            json_data = json.load(f)

        list = []

        #json 파일의 comments들 txt파일로 저장    
        for date in json_data.keys():
            for link in json_data[date]:
                try:
                    for comments in json_data[date][link]:
                        for i in json_data[date][link][comments]:
                            list.append(i+"\n")
                except:
                    continue

        with open(f'{address}/{search}_{start_date}_{end_date}.txt', 'w', encoding='UTF-8') as a:
            for comment in list:
                a.write(comment)
        
        # 워드클라우드로 생성
        rank = Word_Cloud.makeWordCloud(address, search, start_date, end_date, color)

        return rank
    # comment("이준석", "20220711", "20220718", "Reds")