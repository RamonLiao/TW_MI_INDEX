import requests
# requests.adapters.DEFAULT_RETRIES = 5
from bs4 import BeautifulSoup as bs
from datetime import date, timedelta
import sqlite3 as lite
import ProcessBar as PB
import time

url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date={0}&type=ALL'
sql = "insert into 漲跌證券數合計(類型, 整體市場, 股票, 日期) values(?, ?, ?, ?)"

StartDate = date(year=2018, month=10, day=1) #start at 20110801

DateDelta = (date.today()-StartDate).days
process_bar = PB.ShowProcess(DateDelta, 'Finished')


def money_conversion(input_ele):
    return ''.join(input_ele.split(','))

def getTradeValue(cur, TradeDate):
    dt = (''.join(str(TradeDate).split('-')))
    # headers中的Connection默認為keep-alive，即連接一次，傳輸多次。然而在多次訪問後若不能结束並回到連接池中，會導致不能產生新的連接
    # 因此要將header中的Connection一項設置為close
    res = requests.get(url.format(dt), headers={'Connection': 'close'})
    time.sleep(0.01)

    soup = bs(res.text, features='lxml')
    for tr in soup.select('table')[3].select('tr')[2:]:
        td = tr.select('td')
        ret = [td[0].text, money_conversion(td[1].text), money_conversion(td[2].text), TradeDate]
        cur.execute(sql, ret)

con = lite.connect('/Users/ramonliao/Documents/Code/Web_Crawler/TW_MI_INDEX/漲跌證券數合計.db')
cur = con.cursor()

# con.execute("delete from 漲跌證券數合計 where 日期")  #擇一column可刪除全部資料；但column=？時，db裡多筆為？的資料卻刪不掉
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
    #else: 都沒錯誤會執行
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
