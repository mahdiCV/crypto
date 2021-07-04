from db import session
from models import Strategy, Order, Portfolio
from sqlalchemy import and_, or_
from datetime import datetime

def setup(bid, ask, maker_commission):
    strategies = session.query(Strategy).all()
    for strategy in strategies:
        strategy_orders = session.query(Order).filter(
             and_(Order.strategy_id == strategy.id, Order.status=='placed'))
        if strategy_orders.count() > 0:
            continue
        send_orders(bid=bid, ask=ask, maker_commition=self.maker_commission, strategy)

def send_orders(bid, ask, maker_commission, strategy):
    buy_price = (1 - strategy.percent) * bid * (1 - maker_commission)
    buy_order = Order(side='buy', price=buy_price, status='placed', volume=1, insert_time=datetime.now(),
                      strategy_id=strategy.id)
    session.add(buy_order)

    sell_price = (1 + strategy.percent) * ask * (1 + maker_commission)
    sell_order = Order(side='sell', price=sell_price, status='placed', volume=1, insert_time=datetime.now(),
                       strategy_id=strategy.id)
    session.add(sell_order)
    session.commit()
def check_orders(bid, ask, maker_commission):
    orders = session.query(Order).filter(Order.status=='placed')
    for order in Order:
        if order.side == 'buy':
            if bid < order.price:
                order.status = 'done'
                order.net_price = order.price * (1 + maker_commission)
                order.update_time = datetime.now()
                sell_order = session.query(Order).filter(
                    and_(Order.status=='placed', Order.strategy_id==order.strategy_id))
                if sell_order.count() > 0:
                    sell_order = sell_order.first()
                    sell_order.status = 'removed'
                    sell_order.update_time = datetime.now()
                strategy = session.query(Strategy).filter(Strategy.id==order.strategy_id).first()
                send_orders(order.net_price, order.net_price, maker_commission, strategy)
                session.commit
        elif order.side == 'sell':
            if ask > order.price:
                order.status = 'done'
                order.net_price = order.price * (1 - maker_commission)
                order.update_time = datetime.now()
                buy_order = session.query(Order).filter(
                    and_(Order.status == 'placed', Order.strategy_id == order.strategy_id))
                if buy_order.count() > 0:
                    buy_order = buy_order.first()
                    buy_order.status = 'removed'
                    buy_order.update_time = datetime.now()
                strategy = session.query(Strategy).get(Strategy.id == order.strategy_id)
                send_orders(order.net_price, order.net_price, maker_commission, strategy)
                session.commit
