from flask import Flask, request, render_template, session
from flask_restful import Api, Resource, abort, reqparse
from datetime import datetime
import hashlib
import re
import numpy
import random
import json
import string


class dictionaries(object):
    def __init__(self):
        self.data = {}


dictionaries.data_dict = {}
dictionaries.data_list_1 = numpy.array([])
dictionaries.data_list_2 = numpy.array([])
dictionaries.patient_list_1 = numpy.array([])
dictionaries.patient_list_2 = numpy.array([])
dictionaries.data_dict2 = {}
dictionaries.advice_dict = {}
dictionaries.condition_dict = {}
dictionaries.reverse_dict = {}

with open('学ぶくん逆引き.csv', encoding="utf8", errors='ignore') as y:
    for i in y:
        i = i.replace('\n', '')
        data = i.split(',')
        if data[0] == '2':
            continue
        else:
            if data[2] in dictionaries.reverse_dict:
                dictionaries.reverse_dict[data[2]].append(data[1])
            else:
                dictionaries.reverse_dict[data[2]] = []
                dictionaries.reverse_dict[data[2]].append(data[1])

with open('学ぶくん.csv', 'r', encoding="utf8", errors='ignore') as f:
    for ind, i in enumerate(f):
        i = i.replace('\n', '')
        data = i.split(',')
        if len(data) > 4:
            dictionaries.condition_dict[data[0]] = [data[2], data[3:]]
            continue
        dictionaries.data_dict[data[0]] = [data[1], data[2]]
        dictionaries.advice_dict[data[1]] = data[2]

for i in dictionaries.data_dict:
    dictionaries.data_list_1 = numpy.append(dictionaries.data_list_1, i)

with open('new_Data_2.csv', 'r', encoding="utf8", errors='ignore') as z:
    for i in z:
        i = i.replace('\n', '')
        data = i.split(',')
        dictionaries.data_dict2[data[0]] = [data[1], '']
        if data[1] in dictionaries.reverse_dict:
            dictionaries.reverse_dict[data[1]].append(data[0])
        else:
            dictionaries.reverse_dict[data[1]] = []
            dictionaries.reverse_dict[data[1]].append(data[0])
for i in dictionaries.data_dict2:
    dictionaries.data_list_2 = numpy.append(dictionaries.data_list_2, i)

app = Flask(__name__)

class make_advice():
    def edit(text):
        if isinstance(text,str):
            text = [text]
        input_list = []
        input_list.append(text)
        if len(text) == 2:
            input_list.append([text[1],text[0]])
        elif len(text) == 3:
            input_list.append([text[1], text[0],text[2]])
            input_list.append([text[1], text[2],text[0]])
            input_list.append([text[0], text[2],text[1]])
            input_list.append([text[2], text[0],text[1]])
            input_list.append([text[2], text[1],text[0]])
        elif len(text) > 3:
            for i in range(5):
                input_list.append(random.sample(text,len(text)))

        import Levenshtein
        import unicodedata
        distance = {}
        distance_score = []

        for make_sentence in input_list:
            make_sentence = 'の'.join(make_sentence)
            input_txt = unicodedata.normalize('NFKC',make_sentence)
            data_leve_1 = numpy.array([])
            data_leve_2 = numpy.array([])

            output_dict = {}

            for i in dictionaries.data_dict:
                if len(i) >= len(input_txt):
                    data_leve_1 = numpy.append(data_leve_1, Levenshtein.distance(i, input_txt)/len(i))
                else:
                    data_leve_1 = numpy.append(data_leve_1, Levenshtein.distance(i, input_txt)/len(input_txt))


            min = data_leve_1.min()
            if min >= 0.7:
                for k in dictionaries.data_dict2:
                    if len(k) >= len(input_txt):
                        data_leve_2 = numpy.append(data_leve_2, Levenshtein.distance(k, input_txt) / len(k))
                    else:
                        data_leve_2 = numpy.append(data_leve_2, Levenshtein.distance(k, input_txt) / len(input_txt))
                min = data_leve_2.min()
                if min == 0:
                    min_score = numpy.argsort(data_leve_2)[0]
                    output_dict[dictionaries.data_dict2[dictionaries.data_list_2[min_score]][0]] = \
                        [dictionaries.data_dict2[dictionaries.data_list_2[min_score]][1],
                         dictionaries.data_list_2[min_score], data_leve_2[min_score],make_sentence]
                    distance[data_leve_2[min_score]] = output_dict
                    distance_score.append(data_leve_2[min_score])
                else:
                    min_score = numpy.argsort(data_leve_2)[0]
                    if data_leve_2[min_score] >= 1:
                        continue
                    else:
                        output_dict[dictionaries.data_dict2[dictionaries.data_list_2[min_score]][0]] =\
                            [dictionaries.data_dict2[dictionaries.data_list_2[min_score]][1],
                             dictionaries.data_list_2[min_score],data_leve_2[min_score],make_sentence]
                    distance[str(numpy.round(data_leve_2[min_score],decimals=5))] = output_dict
                    distance_score.append(numpy.round(data_leve_2[min_score],decimals=5))
            else:
                if min == 0:
                    min_score = numpy.argsort(data_leve_1)[0]
                    output_dict[dictionaries.data_dict[dictionaries.data_list_1[min_score]][0]] =\
                        [dictionaries.data_dict[dictionaries.data_list_1[min_score]][1],
                         dictionaries.data_list_1[min_score],data_leve_1[min_score],make_sentence]
                    return output_dict
                else:
                    min_score = numpy.argsort(data_leve_1)[0]
                if data_leve_1[min_score] >= 1:
                    continue
                else:
                    output_dict[dictionaries.data_dict[dictionaries.data_list_1[min_score]][0]] =\
                        [dictionaries.data_dict[dictionaries.data_list_1[min_score]][1],dictionaries.data_list_1[min_score],str(data_leve_1[min_score]),make_sentence]
                    distance[str(numpy.round(data_leve_1[min_score],decimals=5))] = output_dict
                    distance_score.append(numpy.round(data_leve_1[min_score],decimals=5))
        output_dict = distance[str(numpy.min(distance_score))]
        return output_dict

    def advice(normalized):
        output_dict = {}
        for i in dictionaries.advice_dict:
            if i == normalized:
                output_dict[i] = [dictionaries.advice_dict[i],'']
        return output_dict

    def gyaku_edit(text):
        import Levenshtein
        import unicodedata

        if isinstance(text,list):
            text = ''.join(text)
        data_leve = numpy.array([])
        data_list = []
        input_txt = unicodedata.normalize('NFKC',text)
        output_dict = {}

        for i in dictionaries.reverse_dict:
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
                output_dict[data_list[loc]] = [data_leve[loc],list(set(dictionaries.reverse_dict[data_list[loc]][0:5]))]
        if len(output_dict) == 0:
            output_dict['候補が無数にあります，入力文を変更してください'] = ['',['']]
        return output_dict, input_txt

@app.route('/', methods=['POST','GET'])

def html():
    if request.method == 'POST':
        if 'input_text' in request.form:
            Gyaku = request.form.get('radio')
            global input_text
            input_text = str(request.form['input_text'])
            if Gyaku == '逆':
                output = make_advice.gyaku_edit(input_text)
                return render_template('netsu.html',output = output, input_text = input_text)
            else:
                input_text = input_text.replace('怪我','けが').replace('痺れ','しびれ').replace('腫れ物','はれもの').replace('火傷','やけど')
                check = 0
                #if input_text == '便':
                #    condition_text = condition_dict['便'][1]
                #    for each in condition_text:
                #        each = each.split('->')
                for label_name in dictionaries.condition_dict:
                    if label_name == input_text:
                        if '熱' in input_text and bool(re.search(r'\d', input_text)):
                            break
                        condition_text = dictionaries.condition_dict[label_name][1]
                        question = []
                        for each in condition_text:
                            each = each.split('->')
                            if each[0] not in input_text:
                                question.append([each[0],each[1]])
                            else:
                                check = 1
                        if check != 1:
                            return render_template('itami.html',question=question,output_message = dictionaries.condition_dict[label_name][0])

            '''
            if '熱' in input_text and not bool(re.search(r'\d',input_text)):
                return render_template('netsu.html')
            elif '痛' in input_text and not '腹' in input_text and not '頭' in input_text and not '胸' in input_text and not '腕' in input_text and not '足' in input_text:
                #output = edit(input_text)
                return render_template('itami.html',input_text = input_text, output_message = '標準病名は「疼痛」です。')
            '''
            output  = dictionaries.edit(input_text)
            return render_template('hello.html', title='flask test', input_text = input_text, output_message = '入力辞書マッチ：距離：標準病名：アドバイス', output = output)

        else:
            doko = request.form.get('radio')
            #print(doko)
            if doko == '尿の異常' or doko == '排尿時の問題':
                check = 0
                for label_name in dictionaries.condition_dict:
                    if label_name == doko:
                        if '熱' in doko and bool(re.search(r'\d', doko)):
                            break
                        condition_text = dictionaries.condition_dict[label_name][1]
                        question = []
                        for each in condition_text:
                            each = each.split('->')
                            if each[0] not in doko:
                                question.append([each[0], each[1]])
                            else:
                                check = 1
                        if check != 1:
                            return render_template('itami.html', question=question,
                                                   output_message=dictionaries.condition_dict[label_name][0])
            if doko == '血便$黒色便$便色異常$硬便' or doko == '残便感$便通異常$頻便':
                ads = doko.split('$')
                output_dict = {}
                for ad in ads:
                    for i in dictionaries.advice_dict:
                        if i == ad:
                            output_dict[i] = [dictionaries.advice_dict[i], '']
                return render_template('hello.html', title='flask test', input_text=input_text,
                                       output_message='標準病名：アドバイス', output=output_dict)
            output = make_advice.advice(doko)
            return render_template('hello.html', title='flask test', input_text=input_text, output_message = '標準病名：アドバイス',output=output)
    #return name

    #変更
    else:
        return render_template('layout.html',normalized = '',input_text = '', answer_message = '')


api = Api(app)

query_post_args = reqparse.RequestParser()
query_post_args.add_argument("Form",type=dict)
query_post_args.add_argument("MessageId", type=str)
query_post_args.add_argument("ReplyToken", type=str)
query_post_args.add_argument("Text",type=str)
query_post_args.add_argument("Inverted",type=bool,help="逆引き辞書")
query_post_args.add_argument('SequenceCount',type=int)


signeture = hashlib.sha256('sociocom'.encode()).hexdigest()
bearer_token = hashlib.sha256('NAIST'.encode()).hexdigest()
max_time = 120
output_dict = {}
reply_token = {
    "token-1" : "1234"
}

tokens = {
}

class API(Resource):

    def post(self):
        global tokens
        #print(tokens)
        if not request.headers['Authorization'] == 'Bearer '+bearer_token:
            return{'StatusCode':-1}
        if not request.headers['X-AIHospital-Signature'] == hashlib.sha256(request.data.hex().encode()).hexdigest():
            return{'StatusCode':-3}
        tokens_check_dict = {}
        for i in tokens:
            if max_time < (datetime.now().timestamp() -tokens[i][1]):
                continue
            else:
                tokens_check_dict[i] = tokens[i]
        tokens = tokens_check_dict
        #print(tokens)
        args = query_post_args.parse_args()
        user_id = args['Form']['UserId']
        hs = hashlib.sha224(args['MessageId'].encode()).hexdigest()
        with open('log.json','a') as f:
            f.write(request.data.decode() + '\n')
        output_dict = {}
        input_text = request.json['Text']

        if args['ReplyToken']:
            if args['ReplyToken'] in tokens:
                token_data = tokens[args['ReplyToken']]
            else:
                return{'StatusCode':-2}
            if args['SequenceCount']:
                output_dict['SequenceCount'] = args['SequenceCount'] + 1
            else:
                output_dict['SequenceCount'] = 1
            input_text = ''.join(input_text)
            if input_text == '尿の異常' or input_text == '排尿時の問題':
                check = 0
                for label_name in dictionaries.condition_dict:
                    if label_name == input_text:
                        if '熱' in input_text and bool(re.search(r'\d', input_text)):
                            break
                        condition_text = dictionaries.condition_dict[label_name][1]
                        output_dict['Description'] = dictionaries.condition_dict[label_name][0]
                        question = []
                        for each in condition_text:
                            each = each.split('->')
                            if each[0] not in input_text:
                                question.append([each[0], each[1]])
                            else:
                                check = 1
                        if check != 1:
                            tokens[hs] = [user_id, datetime.now().timestamp(),token_data[2] + request.json['Text']]
                            output_dict['InputText'] = input_text
                            output_dict['SequenceText'] = token_data[2] + request.json['Text']
                            output_dict['ReplyToken'] = args['ReplyToken']
                            output_dict['UserId'] = user_id
                            question_list = []
                            for one in question:
                                question_list.append({"Choice":one[0],"ToText":one[1]})
                            output_dict['FurtherQuestion'] = question_list
                            output_dict['StatusCode'] = 2
                            return output_dict
            if input_text == '血便$黒色便$便色異常$硬便' or input_text == '残便感$便通異常$頻便':
                ads = input_text.split('$')
                output_list = []
                output_dict = {}
                for ad in ads:
                    for i in dictionaries.advice_dict:
                        if i == ad:
                            output_list.append({"Sdn":ad,"Advice":dictionaries.advice_dict[i], "Distance":0.0})
                output_dict['SequenceText'] = token_data[2] + request.json['Text']
                output_dict['InputText'] = input_text
                output_dict['UserId'] = user_id
                output_dict['SdnList'] = output_list[0]
                output_dict['StatusCode'] = 1
                return output_dict
            output_dict['UserId'] = user_id
            sdn_list = []
            sdns = make_advice.advice(input_text)
            for sdn in sdns:
                sdn_list.append({"Sdn":sdn,"Advice":sdns[sdn][0],"Distance":0.0})
            output_dict['InputText'] = input_text
            output_dict['SequenceText'] = token_data[2] + request.json['Text']
            output_dict['SdnList'] = sdn_list[0]
            output_dict['StatusCode'] = 1
            return output_dict

        elif args['Inverted']:
            output_dict['UserId'] = user_id
            gyaku, input_string = make_advice.gyaku_edit(input_text)
            gyaku_list = []
            output_dict['InputText'] = input_string
            for gya in gyaku:
                gyaku_list.append({"Sdn":gya,"Distance":gyaku[gya][0],"Expressions":gyaku[gya][1]})
            output_dict['SequenceText'] = request.json['Text']
            output_dict['PatientExpression'] = gyaku_list
            output_dict['StatusCode'] = 3
            return output_dict

        else:
            if len(input_text) == 1:
                input_text = input_text[0]
                input_text = input_text.replace('怪我', 'けが').replace('痺れ', 'しびれ').replace('腫れ物', 'はれもの').replace('火傷', 'やけど')
            check = 0
            for label_name in dictionaries.condition_dict:
                if label_name == input_text:
                    if '熱' in input_text and bool(re.search(r'\d', input_text)):
                        break
                    condition_text = dictionaries.condition_dict[label_name][1]
                    output_dict['Description'] = dictionaries.condition_dict[label_name][0]
                    questions = []
                    for each in condition_text:
                        each = each.split('->')
                        if each[0] not in input_text:
                            questions.append([each[0], each[1]])
                        else:
                            check = 1
                    if check != 1:
                        tokens[hs] = [user_id, datetime.now().timestamp(),request.json['Text']]
                        output_dict['InputText'] = input_text
                        output_dict['SequenceText'] = request.json['Text']
                        output_dict['ReplyToken'] = hs
                        output_dict['UserId'] = user_id
                        question_list = []
                        for one in questions:
                            question_list.append({"Choice": one[0], "ToText": one[1]})
                        output_dict['FurtherQuestion'] = question_list
                        output_dict['StatusCode'] = 2
                        return output_dict

            output_dict['UserId'] = user_id
            output_dict['SequenceCount'] = 1
            output_dict['SequenceText'] = request.json['Text']
            output_dict['InputText'] = input_text
            sdn_list = []
            sdns = make_advice.edit(input_text)
            for sdn in sdns:
                sdn_list.append({"Sdn": sdn,"Advice":sdns[sdn][0],"Distance":sdns[sdn][2]})
                output_dict['InputText'] = sdns[sdn][3]
            output_dict['SdnList'] = sdn_list[0]
            output_dict['StatusCode'] = 1
            return output_dict

api.add_resource(API, "/API")

## おまじない
if __name__ == "__main__":
    app.run(debug=True)
