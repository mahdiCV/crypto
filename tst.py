import requests

proxy = {
    "https": "http://127.0.0.1:8889"
}
url = "https://api.binance.com/api/v3/depth"
params = {
    "symbol": "BTCUSDT",
    "limit": 1000
}
data = requests.get(url, proxies=proxy, params=params)

print(data.json())