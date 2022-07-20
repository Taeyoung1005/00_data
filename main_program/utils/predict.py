from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from collections import OrderedDict
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

class Predict():
    def __init__(self):
        ## 读入数据
        def read_data(file):
            texts = []
            labels = []
            data = pd.read_excel(file, engine='openpyxl')
            for row in data.itertuples():
                label = getattr(row, 'label')
                review = str(getattr(row, 'review'))[1:-1]
                texts.append(review)
                labels.append(label)
            assert len(texts) == len(labels)
            return texts, labels

        texts, labels = read_data('bert_model/Ko.xlsx')

        self.train_texts, self.val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=43, stratify=labels)

        # ### label和id进行映射
        self.label2id = OrderedDict({item: idx for idx, item in enumerate(set(train_labels + val_labels))})
        self.id2label = OrderedDict({v: k for k, v in self.label2id.items()})

        self.device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')  # 使用cpu或者gpu
        self.model = BertForSequenceClassification.from_pretrained("kykim/bert-kor-base", num_labels=len(self.label2id))
        self.model.to(self.device)
        self.model.train()

        self.tokenizer = BertTokenizer.from_pretrained("bert_model/model_best")
        model = BertForSequenceClassification.from_pretrained(
            "bert_model/model_best", num_labels=len(self.label2id))
        model.to(self.device) 

    def predict(self, text):
            encoding = self.tokenizer(text,
                                return_tensors="pt",
                                max_length=128,
                                truncation=True,
                                padding=True)
            encoding = {k:v.to(self.device) for  k,v in encoding.items()}
            outputs = self.model(**encoding)
            #pred = id2label[torch.argmax(outputs[0], dim=-1).numpy()[0]]
            pred = self.id2label[torch.argmax(outputs[0], dim=-1).cpu().detach().numpy()[0]]
            return pred