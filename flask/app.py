from pytrends.request import TrendReq
import pandas
import time
# googleに接続
pytrend = TrendReq(hl='ja-jp',tz=540)
datalist = []
with open('学ぶくん逆引き.csv', encoding="utf8", errors='ignore') as y:
    for ind, i in enumerate(y):
        if ind < 1173:
            continue
        kw_list = ['あつい']
        i = i.replace('\n', '')
        data = i.split(',')
        if data[1] == 'あつい':
            continue
        kw_list.append(data[1])
        while True:
            try:
                pytrend.build_payload(kw_list=kw_list, timeframe='2017-04-01 2021-04-01', geo="JP")
                break
            except:
                print('wait')
                time.sleep(60)
        df = pytrend.interest_over_time()
        mean  = df.mean().values
        score = mean[1]/mean[0]
        datalist.append([data[1],data[2],score])
        with open('inverted.csv', 'a') as f:
            f.write(data[1]+','+data[2]+','+str(score)+'\n')
        time.sleep(1)
pandas.DataFrame(datalist).to_excel('inverted.xlsx')
