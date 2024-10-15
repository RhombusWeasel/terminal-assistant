from utils.tools import new_tool
from utils.prompt_tools import print_msg
import yfinance as yf
import json

def get_ticker_data(ticker):
  try:
    data = yf.Ticker(ticker)
    # print(json.dumps(data.info, indent=2))
    price_data = {
      'open': data.info['open'],
      'high': data.info['dayHigh'],
      'low': data.info['dayLow'],
      'close': data.info['previousClose'],
      'volume': data.info['volume'],
      'ask': data.info['ask'],
      'bid': data.info['bid'] if 'bid' in data.info else 'Market Closed',
      'year_high': data.info['fiftyTwoWeekHigh'],
      'year_low': data.info['fiftyTwoWeekLow'],
    }
    response = [{'role': 'system', 'content': f"""Gathering data for {ticker}\n\n{json.dumps(price_data, indent=2)}""", 'resend': True}]
    print_msg(response)
    return response
  except Exception as e:
    response = [{'role': 'system', 'content': f'Error getting stock data: {e}'}]
    print_msg(response)
    return response
  
@new_tool('stock_data', {
  'name': 'stock_data',
  'description': 'Gets data on a stock. This data includes information such as the stock\'s name, sector, analyst ratings and more.',
  'parameters': {
    'type': 'object',
    'properties': {
      'ticker': {
        'type': 'string',
        'description': 'The stock ticker to get data on.'
      }
    },
    'required': ['ticker']
  }
})
def stock_data(data):
  ticker = data['ticker']
  return get_ticker_data(ticker)