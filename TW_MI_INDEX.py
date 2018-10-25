import requests
requests.adapters.DEFAULT_RETRIES = 5  # 增加重連次數
from bs4 import BeautifulSoup as bs
from datetime import date, timedelta
import sqlite3 as lite
import ProcessBar as PB
import time

url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date={0}&type=ALL'
sql = "insert into 每日收盤行情(證券代號, 證券名稱, 日期, 成交股數, 成交筆數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, '漲跌 (+/-)', 漲跌價差, 最後揭示買價, 最後揭示買量, 最後揭示賣價, 最後揭示賣量, 本益比) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

StartDate = date(year=2011, month=8, day=1)  # start at 20110801

DateDelta = (date.today()-StartDate).days
process_bar = PB.ShowProcess(DateDelta, 'Finished') # Bug: 如果超出設定次數，會重跑一次


def money_conversion(input_ele):
    return ''.join(input_ele.split(','))


s = requests.session()
s.keep_alive = False  # 關閉多餘連接

def getTradeValue(cur, TradeDate):
    dt = (''.join(str(TradeDate).split('-')))
    # headers中的Connection默認為keep-alive，即連接一次，傳輸多次。然而在多次訪問後若不能结束並回到連接池中，會導致不能產生新的連接
    # 因此要將header中的Connection一項設置為close
    res = s.get(url.format(dt), headers={'Connection': 'close'}) 
    time.sleep(0.01)

    soup = bs(res.text, features='lxml')
    for tr in soup.select('table')[4].select('tr')[3:]:
        td = tr.select('td')
        ret = [
            td[0].text, td[1].text, TradeDate, money_conversion(td[2].text), 
            money_conversion(td[3].text), money_conversion(td[4].text), money_conversion(td[5].text), money_conversion(td[6].text), 
            money_conversion(td[7].text), money_conversion(td[8].text), td[9].text, money_conversion(td[10].text), 
            money_conversion(td[11].text), money_conversion(td[12].text), money_conversion(td[13].text), money_conversion(td[14].text),
            money_conversion(td[15].text)
            ]
        cur.execute(sql, ret)


con = lite.connect('/Users/ramonliao/Documents/Code/Web_Crawler/TW_MI_INDEX/TW_MI_INDEX.db')
cur = con.cursor()

# con.execute("delete from 每日收盤行情 where 日期")  #擇一column可刪除全部資料；但column=？時，db裡多筆為？的資料卻刪不掉 ; 日期 = '2018-10-01'
# con.commit()
# con.close()
# exit()

today = date.today()
TradeDate = StartDate
while TradeDate < today:
    try:
        getTradeValue(cur, TradeDate)
    except IndexError as inst:
        print('Not trading %s' % str(TradeDate), inst.args)
    except requests.exceptions.ConnectionError:
        print('stops on %s and sleeps for 5 seconds' % str(TradeDate)) #假設超過聯結次數，印出中斷日期，下次從此處繼續
        # con.commit()
        # con.close()
        time.sleep(5)
        continue

    process_bar.show_process()
    TradeDate = TradeDate + timedelta(days=1)

con.commit()
con.close()
