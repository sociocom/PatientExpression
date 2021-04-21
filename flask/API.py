# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPDigestAuth, HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import re
import numpy

data_dict = {}
data_list_1 = numpy.array([])
data_list_2 = numpy.array([])
patient_list_1 = numpy.array([])
patient_list_2 = numpy.array([])
data_dict2 = {}
advice_dict = {}
condition_dict = {}
reverse_dict = {}
with open('学ぶくん逆引き.csv', encoding="utf8", errors='ignore') as y:
    for i in y:
        i = i.replace('\n','')
        data = i.split(',')
        if data[0] == '2':
            continue
        else:
            if data[2] in reverse_dict:
                reverse_dict[data[2]].append(data[1])
            else:
                reverse_dict[data[2]] = []
                reverse_dict[data[2]].append(data[1])

with open('学ぶくん.csv', 'r', encoding="utf8", errors='ignore') as f:
    for ind,i in enumerate(f):
        data = i.split(',')
        if len(data) > 4:
            condition_dict[data[0]] = [data[2],data[3:]]
            continue
        data_dict[data[0]] = [data[1],data[2]]
        advice_dict[data[1]] = data[2]

for i in data_dict:
    data_list_1 = numpy.append(data_list_1, i)

with open('new_Data_2.csv', 'r', encoding="utf8", errors='ignore') as z:
    for i in z:
        data = i.split(',')
        data_dict2[data[0]] = [data[1],'']
        if data[1] in reverse_dict:
            reverse_dict[data[1]].append(data[0])
        else:
            reverse_dict[data[1]] = []
            reverse_dict[data[1]].append(data[0])
for i in data_dict2:
    data_list_2 = numpy.append(data_list_2, i)

def edit(text):
    import re
    import Levenshtein
    import unicodedata

    data_leve_1 = numpy.array([])
    data_leve_2 = numpy.array([])
    input_txt = unicodedata.normalize('NFKC',text)
    output_dict = {}

    for i in data_dict:
        if len(i) >= len(input_txt):
            data_leve_1 = numpy.append(data_leve_1, Levenshtein.distance(i, input_txt)/len(i))
        else:
            data_leve_1 = numpy.append(data_leve_1, Levenshtein.distance(i, input_txt)/len(input_txt))


    min = data_leve_1.min()
    if min >= 0.5:
        for k in data_dict2:
            if len(k) >= len(input_txt):
                data_leve_2 = numpy.append(data_leve_2, Levenshtein.distance(k, input_txt) / len(k))
            else:
                data_leve_2 = numpy.append(data_leve_2, Levenshtein.distance(k, input_txt) / len(input_txt))
        min = data_leve_2.min()
        if min == 0:
            min_list = [numpy.argsort(data_leve_2)[0]]
        else:
            min_list = numpy.argsort(data_leve_2)[0:5]
        for loc in min_list:
            if data_leve_2[loc] >= 1:
                continue
            else:
                output_dict[data_dict2[data_list_2[loc]][0]] = [data_dict2[data_list_2[loc]][1],data_list_2[loc],str(data_leve_2[loc])]

    else:
        if min == 0:
            min_list = [numpy.argsort(data_leve_1)[0]]
        else:
            min_list = numpy.argsort(data_leve_1)[0:5]
        for loc in min_list:
            if data_leve_1[loc] >= 1:
                continue
            else:
                output_dict[data_dict[data_list_1[loc]][0]] = [data_dict[data_list_1[loc]][1],data_list_1[loc],str(data_leve_1[loc])]

    return output_dict

def advice(normalized):
    output_dict = {}
    for i in advice_dict:
        if i == normalized:
            output_dict[i] = [advice_dict[i],'']
    return output_dict

def gyaku_edit(text):
    import Levenshtein
    import unicodedata

    data_leve = numpy.array([])
    data_list = []
    input_txt = unicodedata.normalize('NFKC',text)
    output_dict = {}

    for i in reverse_dict:
        if len(i) >= len(input_txt):
            data_leve = numpy.append(data_leve, Levenshtein.distance(i, input_txt)/len(i))
            data_list.append(i)
        else:
            data_leve = numpy.append(data_leve, Levenshtein.distance(i, input_txt)/len(input_txt))
            data_list.append(i)

    min = data_leve.min()
    if min == 0:
        min_list = [numpy.argsort(data_leve)[0]]
    else:
        min_list = numpy.argsort(data_leve)[0:5]
    for loc in min_list:
        if data_leve[loc] >= 1:
            continue
        else:
            output_dict[data_list[loc]] = [data_leve[loc],reverse_dict[data_list[loc]][0:5]]
    if len(output_dict) == 0:
        output_dict['候補が無数にあります，入力文を変更してください'] = ['',['']]
    return output_dict

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'a'

query_post_args = reqparse.RequestParser()
query_post_args.add_argument("text",type=str, help="検索したい症状を入力してください",)
query_post_args.add_argument("place",type=str, help="place")


reply_post_args = reqparse.RequestParser()
output_dict = {}
users = {
    "token-1" : "1234"
}

class Hello(Resource):
    auth = HTTPDigestAuth()
    @auth.get_password
    def get_pw(username):
        if username in users:
            return users.get(username)

    @auth.login_required
    def get(self):
        args = query_post_args.parse_args()
        input_text = args['text']
        return input_text

    @auth.login_required
    def post(self):
        args = query_post_args.parse_args()
        input_text = args['text']
        input_text = input_text.replace('怪我', 'けが').replace('痺れ', 'しびれ').replace('腫れ物', 'はれもの').replace('火傷', 'やけど')
        check = 0
        for label_name in condition_dict:
            if label_name == input_text:
                if '熱' in input_text and bool(re.search(r'\d', input_text)):
                    break
                condition_text = condition_dict[label_name][1]
                question = []
                for each in condition_text:
                    each = each.split('->')
                    if each[0] not in input_text:
                        question.append([each[0], each[1]])
                    else:
                        check = 1
                if check != 1:
                    okewatashi = input_text
                    return question,
        output_dict = edit(args['text'])
        return output_dict

class reply(Resource):
    def get(self):
        return output_dict
    def post(self):
        args = query_post_args.parse_args()
        doko = args['place']
        output = advice(doko)
        return output


api.add_resource(Hello, "/API")
api.add_resource(reply,"/reply")

if __name__ == '__main__':
    app.run(debug=True)
