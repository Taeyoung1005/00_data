from wordcloud import WordCloud
from konlpy.tag import Komoran
from collections import Counter
import numpy as np

class Word_Cloud:
    def makeWordCloud(address, search, start_date, end_date, color):
        # open으로 txt파일을 열고 read()를 이용하여 utf-8 읽는다.
        text = open(f"{address}/{search}_{start_date}_{end_date}.txt", encoding='UTF-8').read() 
        
        if len(text) == 0:
            text = "NULL"
        
        # Komoran 함수를 이용해 형태소 분석
        komoran = Komoran()
        line =[]

        line = komoran.pos(text)

        n_adj =[]

        # 명사와 동사만  n_adj에 넣어주기
        for word, tag in line:
            if tag in ['NNG','NNP','NNB','VV','VA']:
                n_adj.append(word)

        #제외할 단어 추가(를과 의를 삭제함)
        stop_words = "를 의 에 의" #추가할 때 띄어쓰기로 추가해주기
        stop_words = set(stop_words.split(' '))
        # 불용어를 제외한 단어만 남기기
        n_adj = [word for word in n_adj if not word in stop_words]

        if text == "NULL":
            tags = [('NULL', 1)]
            tags1 = [('NULL', 1), ('NULL', 1), ('NULL', 1), ('NULL', 1)]
        else:
            #가장 많이 나온 단어 50개 저장
            counts = Counter(n_adj)
            tags = counts.most_common(50)

            #1, 2, 3, 4 순위 저장
            tags1 = counts.most_common(4)

         #원 모형으로 그리기
        x, y = np.ogrid[:600, :600]
        mask = (x - 300) ** 2 + (y - 300) ** 2 > 250 ** 2
        mask = 255 * mask.astype(int)

        # WordCloud를 생성한다.
        # 한글을 분석하기위해 font를 한글로 지정해주어야 된다. macOS는 .otf , window는 .ttf 파일의 위치를
        # 지정해준다. (ex. 'C:\Windows\Fonts\malgunbd.ttf')
    
        wc = WordCloud(font_path='C:/WINDOWS/FONTS/MALGUN.TTF',background_color='white',max_font_size=100, colormap=color, mask=mask)
        cloud = wc.generate_from_frequencies(dict(tags))
        cloud.to_file(f'../main_program/static/images/{search}_{start_date}_{end_date}.jpg')

        return tags1