import websocket
import json
import requests
import threading
from datetime import datetime
import simulator


class Binance:
    def __init__(self):
        self.order_book = {}
        self.log_file = "log.txt"
        self.u = 0
        self.deposit = 0
        self.buy_price = 0
        self.sell_price = 0
        self.maker_commission = 0.1 / 100
        self.taker_commission = 0.1 / 100
        self.volatility = .1/100
        with open(self.log_file, "w") as f:
            f.write("")
        self.stream()


    def get_snapshot(self):
        proxy = {
            "https": "http://127.0.0.1:8889"
        }
        url = "https://api.binance.com/api/v3/depth"

        params = {
            "symbol": "BTCUSDT",
            "limit": 1000
        }
        data = requests.get(url, proxies=proxy, params=params)
        order_book = data.json()
        bids = []
        for bid in order_book['bids']:
            c_bid = [float(bid[0]), float(bid[1])]
            bids.append(c_bid)

        asks = [[float(ask[0]), float(ask[1])] for ask in order_book['asks']]
        order_book['bids'] = bids
        order_book['asks'] = asks
        return order_book

    def set_order(self, bid, ask):
        # buy_price = (1 - self.volatility) * bid * (1 - self.maker_commission)
        # self.buy_price = round(buy_price, 2)

        buy_price = bid * (1 - self.maker_commission)
        self.buy_price = round(buy_price - 2, 2)

        data = {"action": "sentOrder", "side": "buy", "price": self.buy_price, "deposit": self.deposit}
        self.log(data)
        # sell_price = (1 + self.volatility) * ask * (1 + self.maker_commission)
        # self.sell_price = round(sell_price, 2)

        sell_price = ask * (1 + self.maker_commission)
        self.sell_price = round(sell_price + 2, 2)

        data = {"action": "sentOrder", "side": "sell", "price": self.sell_price, "deposit": self.deposit}
        self.log(data)
        print("ask: {}, sell order price: {}, bid: {}, buy order price: {}".format(ask, self.sell_price, bid,
                                                                                   self.buy_price))


    def stream(self):

        def on_message(ws, msg):
            #print(msg)
            data1 = json.loads(msg)
            if 'e' in data1:
                if data1['e'] == 'depthUpdate':
                    if data1['u'] <= self.order_book['lastUpdateId']:
                        print("do nothing")
                    elif data1['U'] <= self.order_book['lastUpdateId'] + 1 <= data1['u']:
                        print("first event")
                        self.update_order_book(data1)
                        self.u = data1['u']

                    elif data1['U'] == self.u + 1:
                        # print("new event")
                        self.update_order_book(data1)
                        self.u = data1['u']
                    else:
                        self.order_book = self.get_snapshot()
                        print("else")

        def on_open(ws):
            self.order_book = self.get_snapshot()
            print("connection opened")
            subscribe = {
                "method": "SUBSCRIBE",
                "params":
                    [
                        # "btcusdt@aggTrade",
                        "btcusdt@depth"
                    ],
                "id": 1
            }
            ws.send(json.dumps(subscribe))
            # make buy price
            bid = self.order_book['bids'][0][0]
            # make sell price
            ask = self.order_book['asks'][0][0]
            simulator.setup(bid, ask, maker_commission=self.maker_commission)
            self.set_order(bid, ask)

        def on_close(ws):
            print("connection closed")

        def on_error(ws, err):
            print(err)

        websocket.enableTrace(True)
        print("binance opening")
        url = 'wss://stream.binance.com:9443/ws/test'
        ws = websocket.WebSocketApp(url=url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open
                                    )
        thread = threading.Thread(target=ws.run_forever(http_proxy_host="127.0.0.1", http_proxy_port="8889"))
        thread.start()
        #ws.run_forever(http_proxy_host="127.0.0.1", http_proxy_port="8889")
        print("binance running")

    def update_order_book(self, data1):
        # bids
        bids = {}
        for bid in self.order_book['bids']:
            bids[bid[0]] = bid[1]
        for b in data1['b']:
            price = float(b[0])
            volume = float(b[1])
            bids[price] = volume
            if volume == 0:
                del bids[price]
        updated_prices = sorted(bids, reverse=True)
        self.order_book['bids'] = [[price, bids[price]] for price in updated_prices]
        # print(self.order_book['bids'][0])


        # asks
        asks = {}
        for ask in self.order_book['asks']:
            asks[ask[0]] = ask[1]
        for a in data1['a']:
            price = float(a[0])
            volume = float(a[1])
            asks[price] = volume
            if volume == 0:
                del asks[price]
            updated_prices = sorted(asks)
            self.order_book['asks'] = [[price, asks[price]] for price in updated_prices]
            bid = self.order_book['bids'][0][0]
            ask = self.order_book['asks'][0][0]
            print("bids: ", bid, "asks: ", ask)
            self.chek_order(bid, ask)
            simulator.check_orders(bid=bid, ask=ask, maker_commition=self.maker_commission)


    def chek_order(self, bid, ask):
        if bid < self.buy_price:

            net_buy_price = self.buy_price * (1 + self.maker_commission)
            self.deposit -= net_buy_price
            self.set_order(bid=net_buy_price, ask=net_buy_price)
            print("buy order do at : ", self.buy_price, "deposit: ", self.deposit)
            data = {"bid": bid, "ask": ask, "action": "buy", "deposit": self.deposit, "net_trade": net_buy_price}
            self.log(data)
        elif ask > self.sell_price:

            net_sell_price = self.sell_price * (1 - self.maker_commission)
            self.deposit += net_sell_price
            self.set_order(bid=net_sell_price, ask=net_sell_price)
            print("sell order do at: ", self.sell_price, "deposit: ", self.deposit)
            data = {"bid": bid, "ask": ask, "action": "sell", "deposit": self.deposit, "net_trade": net_sell_price}
            self.log(data)
    def log(self, data):
        data["time"] = str(datetime.now())
        with open("log.txt", "a") as f:
            f.write(json.dumps(data)+"\n")
        print("logged")







b = Binance()
# b.order_book = b.get_snapshot()
# print(b.order_book)