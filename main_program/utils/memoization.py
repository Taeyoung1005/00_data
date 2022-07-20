from datetime import datetime, timedelta
import pandas as pd

class Memoization():
    def __init__(self,key_word,start_date,end_date):
        self.key_word = key_word
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        self.date_list = self.total_date_list(start,end)

    def total_date_list(self,start,end):
        date_list = [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range((end-start).days+1)]
        return date_list
        


if __name__ == "__main__":
    m = Memoization("20220603","20220705")
