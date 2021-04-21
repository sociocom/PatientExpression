import sys
sys.path.append('../../')
#print(os.getcwd())
from flask.flask_test import dictionaries, make_advice
from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from datetime import datetime
import hashlib
import re

app = Flask(__name__)
api = Api(app)

query_post_args = reqparse.RequestParser()
query_post_args.add_argument("Form",type=dict)
query_post_args.add_argument("MessageId", type=str)
query_post_args.add_argument("ReplyToken", type=str)
query_post_args.add_argument("Text")
query_post_args.add_argument("Inverted",type=bool,help="逆引き辞書")
query_post_args.add_argument('SequenceCount',type=int)


signeture = hashlib.sha256('sociocom'.encode()).hexdigest()
#bearer_token = hashlib.sha256('NAIST'.encode()).hexdigest()
bearer_token = 'a'
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
        if not request.headers['X-AIHospital-Signature'] == 'a':\
               #hashlib.sha256(request.data.hex().encode()).hexdigest():
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
        with open('log.json', 'a') as f:
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
            gyaku, input_string= make_advice.gyaku_edit(input_text)
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
