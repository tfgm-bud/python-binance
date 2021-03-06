"""
The Purpose of the RoibalBot Python Program is to create an automated trading bot (functionality) on Binance
Utilized Python-Binance ( https://github.com/sammchardy/python-binance )

Created 4/14/2018 by Joaquin Roibal
V 0.01 - Updated 4/20/2018

Licensed under MIT License

Instructional Youtube Video: https://www.youtube.com/watch?v=8AAN03M8QhA

Did you enjoy the functionality of this bot? Tips always appreciated.

BTC:
ETH:

NOTE: All Subsequent Version of Program must contain this message, unmodified, in it's entirety
Copyright (c) 2018 by Joaquin Roibal
"""

from binance.client import Client
import time
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from binance.enums import *
import save_historical_data_Roibal
from BinanceKeys import BinanceKey1

api_key = BinanceKey1['api_key']
api_secret = BinanceKey1['api_secret']

client = Client(api_key, api_secret)

# get a deposit address for BTC
address = client.get_deposit_address(asset='BTC')

def run():
    # get system status
    #Create List of Crypto Pairs to Watch
    list_of_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT','BNBBTC', 'ETHBTC', 'LTCBTC']
    #time_horizon = "Short"
    #Risk = "High"

    #Get Status of Exchange & Account
    try:
        status = client.get_system_status()
        print("\nExchange Status: ", status)

        #Account Withdrawal History Info
        withdraws = client.get_withdraw_history()
        print("\nClient Withdraw History: ", withdraws)

        #get Exchange Info
        info = client.get_exchange_info()
        print("\nExchange Info (Limits): ", info)
    except():
        pass

    # place a test market buy order, to place an actual order use the create_order function
    # if '1000 ms ahead of server time' error encountered, visit https://github.com/sammchardy/python-binance/issues/249
    try:
        order = client.create_test_order(
            symbol='BNBBTC',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=100)
    except:
        print("\n \n \nATTENTION: NON-VALID CONNECTION WITH BINANCE \n \n \n")

    #Get Info about Coins in Watch List
    coin_prices(list_of_symbols)
    coin_tickers(list_of_symbols)
    for symbol in list_of_symbols:
        market_depth(symbol)
    visualize_market_depth()
    #get recent trades
    trades = client.get_recent_trades(symbol='BNBBTC')
    print("\nRecent Trades: ", trades)
    print("Local Time: ", time.localtime())
    print("Recent Trades Time: ", convert_time_binance(trades[0]['time']))

    #get historical trades
    try:
        hist_trades = client.get_historical_trades(symbol='BNBBTC')
        print("\nHistorical Trades: ", hist_trades)
    except:
        print('\n \n \nATTENTION: NON VALID CONNECTION WITH BINANCE \n \n \n')

    #get aggregate trades
    agg_trades = client.get_aggregate_trades(symbol='BNBBTC')
    print("\nAggregate Trades: ", agg_trades)


def convert_time_binance(gt):
    #Converts from Binance Time Format (milliseconds) to time-struct
    #From Binance-Trader Comment Section Code
    #gt = client.get_server_time()
    print("Binance Time: ", gt)
    print(time.localtime())
    aa = str(gt)
    bb = aa.replace("{'serverTime': ","")
    aa = bb.replace("}","")
    gg=int(aa)
    ff=gg-10799260
    uu=ff/1000
    yy=int(uu)
    tt=time.localtime(yy)
    #print(tt)
    return tt


def market_depth(sym, num_entries=20):
    #Get market depth
    #Retrieve and format market depth (order book) including time-stamp
    i=0     #Used as a counter for number of entries
    print("Order Book: ", convert_time_binance(client.get_server_time()))
    depth = client.get_order_book(symbol=sym)
    print(depth)
    print(depth['asks'][0])
    ask_tot=0.0
    ask_price =[]
    ask_quantity = []
    bid_price = []
    bid_quantity = []
    bid_tot = 0.0
    place_order_ask_price = 0
    place_order_bid_price = 0
    max_order_ask = 0
    max_order_bid = 0
    print("\n", sym, "\nDepth     ASKS:\n")
    print("Price     Amount")
    for ask in depth['asks']:
        if i<num_entries:
            if float(ask[1])>float(max_order_ask):
                #Determine Price to place ask order based on highest volume
                max_order_ask=ask[1]
                place_order_ask_price=round(float(ask[0]),5)-0.0001
            #ask_list.append([ask[0], ask[1]])
            ask_price.append(float(ask[0]))
            ask_tot+=float(ask[1])
            ask_quantity.append(ask_tot)
            #print(ask)
            i+=1
    j=0     #Secondary Counter for Bids
    print("\n", sym, "\nDepth     BIDS:\n")
    print("Price     Amount")
    for bid in depth['bids']:
        if j<num_entries:
            if float(bid[1])>float(max_order_bid):
                #Determine Price to place ask order based on highest volume
                max_order_bid=bid[1]
                place_order_bid_price=round(float(bid[0]),5)+0.0001
            bid_price.append(float(bid[0]))
            bid_tot += float(bid[1])
            bid_quantity.append(bid_tot)
            #print(bid)
            j+=1
    return ask_price, ask_quantity, bid_price, bid_quantity, place_order_ask_price, place_order_bid_price
    #Plot Data

def visualize_market_depth(wait_time_sec='1', tot_time='1', sym='ICXBNB'):
    cycles = int(tot_time)/int(wait_time_sec)
    start_time = time.asctime()
    fig, ax = plt.subplots()
    for i in range(1,int(cycles)+1):
        ask_pri, ask_quan, bid_pri, bid_quan, ask_order, bid_order = market_depth(sym)

        #print(ask_price)
        plt.plot(ask_pri, ask_quan, color = 'red', label='asks-cycle: {}'.format(i))
        plt.plot(bid_pri, bid_quan, color = 'blue', label = 'bids-cycle: {}'.format(i))

        #ax.plot(depth['bids'][0], depth['bids'][1])
        max_bid = max(bid_pri)
        min_ask = min(ask_pri)
        max_quant = max(ask_quan[-1], bid_quan[-1])
        spread = round(((min_ask-max_bid)/min_ask)*100,5)   #Spread based on market
        proj_order_spread = round(((ask_order-bid_order)/ask_order)*100, 5)
        price=round(((max_bid+min_ask)/2),5)
        plt.plot([price, price],[0, max_quant], color = 'green', label = 'Price - Cycle: {}'.format(i)) #Vertical Line for Price
        plt.plot([ask_order, ask_order],[0, max_quant], color = 'black', label = 'Ask - Cycle: {}'.format(i))
        plt.plot([bid_order, bid_order],[0, max_quant], color = 'black', label = 'Buy - Cycle: {}'.format(i))
        ax.annotate("Max Bid: {} \nMin Ask: {}\nSpread: {} %\nCycle: {}\nPrice: {}"
                    "\nPlace Bid: {} \nPlace Ask: {}\n Projected Spread: {} %".format(max_bid, min_ask, spread, i, price, bid_order, ask_order, proj_order_spread),
                    xy=(max_bid, ask_quan[-1]), xytext=(max_bid, ask_quan[0]))
        if i==(cycles+1):
            break
        else:
            time.sleep(int(wait_time_sec))
    #end_time = time.asctime()
    ax.set(xlabel='Price', ylabel='Quantity',
       title='Binance Order Book: {} \n {}\n Cycle Time: {} seconds - Num Cycles: {}'.format(sym, start_time, wait_time_sec, cycles))
    plt.legend()
    plt.show()


def coin_prices(watch_list):
    #Will print to screen, prices of coins on 'watch list'
    #returns all prices
    prices = client.get_all_tickers()
    print("\nSelected (watch list) Ticker Prices: ")
    for price in prices:
        if price['symbol'] in watch_list:
            print(price)
    return prices


def coin_tickers(watch_list):
    # Prints to screen tickers for 'watch list' coins
    # Returns list of all price tickers
    tickers = client.get_orderbook_tickers()
    print("\nWatch List Order Tickers: \n")
    for tick in tickers:
        if tick['symbol'] in watch_list:
            print(tick)
    return tickers

def portfolio_management(deposit = '10000', withdraw=0, portfolio_amt = '0', portfolio_type='USDT', test_acct='True'):
    """The Portfolio Management Function will be used to track profit/loss of Portfolio in Any Particular Currency (Default: USDT)"""
    #Maintain Portfolio Statistics (Total Profit/Loss) in a file
    pass

def Bollinger_Bands():
    #This Function will calculate Bollinger Bands for Given Time Period
    #EDIT: Will use Crypto-Signal for this functionality
    #https://github.com/CryptoSignal/crypto-signal
    pass

def buy_sell_bot():
    pass

def position_sizing():
    pass

def trailing_stop_loss():
    pass


#Place Limit Order
"""
order = client.order_limit_buy(
    symbol='BNBBTC',
    quantity=100,
    price='0.00001')

order = client.order_limit_sell(
    symbol='BNBBTC',
    quantity=100,
    price='0.00001')
"""




"""
#trade aggregator (generator)
agg_trades = client.aggregate_trade_iter(symbol='ETHBTC', start_str='30 minutes ago UTC')
# iterate over the trade iterator
for trade in agg_trades:
    pass
    #print(trade)
    # do something with the trade data

# convert the iterator to a list
# note: generators can only be iterated over once so we need to call it again
agg_trades = client.aggregate_trade_iter(symbol='ETHBTC', start_str='30 minutes ago UTC')
agg_trade_list = list(agg_trades)

# fetch 30 minute klines for the last month of 2017
klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
#for kline in klines:
    #print(kline)
"""

#place an order on Binance
"""
order = client.create_order(
    symbol='BNBBTC',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price='0.00001')
"""

if __name__ == "__main__":
    run()