import re
import Levenshtein
import unicodedata
import numpy
import csv

data_dict = {}
data_list = numpy.array([])
data_leve = numpy.array([])
with open('new_Data_2.csv','r',encoding="utf8", errors='ignore') as f:
    for i in f:
        data = i.split(',')
        if len(data) == 2:
            data_dict[data[0]] = data[1]
input_txt = '頭が痛い' #input('ハッシュタグ形式で')
input_txt = unicodedata.normalize('NFKC', input_txt)

for i in data_dict:
    data_list = numpy.append(data_list, data_dict[i])
    data_leve = numpy.append(data_leve, Levenshtein.distance(i, input_txt))

print(numpy.argmin(data_leve))
print(data_leve[numpy.argmin(data_leve)],data_list[numpy.argmin(data_leve)])