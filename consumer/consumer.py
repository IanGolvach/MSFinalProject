"""Code for a KAFKA consumer container"""
import os
# from flask import jsonify, request, Flask
# from flaskext.mysql import MySQL
import mysql.connector
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
'''
SQL Tables

STOCK
 - Symbol (Primary Key)
 - Name (Unique)

TICKER
 - ID (Primary Key)
 - Symbol (Foreign Key to STOCK)
 - Time
 - Open
 - Close
 - High
 - Low
 - Volume
 - Interval

USAGE
 - ID (Primary Key)
 - Symbol (Foreign Key to STOCK)
 - Selected (JSON list)
 - Date_End
 - Date_Start
 - Timestamp
 - Requestor
 - Type
 - Latency
'''
 # https://stackoverflow.com/questions/1650946/mysql-create-table-if-not-exists-error-1050
 # Inspiration
default_statement = '''
CREATE database if not exists 'stockdb' ';
USE 'stockdb';

CREATE table IF NOT EXISTS 'stock' (
    'symbol' varchar(5) NOT NULL,
    'name' varchar(128) UNIQUE,
    PRIMARY KEY  ('symbol')
);

CREATE table IF NOT EXISTS 'ticker' (
    'ID' int NOT NULL AUTO_INCREMENT,
    'symbol' varchar(5) NOT NULL,
    'time' DATETIME NOT NULL,
    'open' float, 
    'close' float,
    'high' float,
    'low' float,
    'volume' float,
    'interval' varchar(5),
    PRIMARY KEY ('ID'),
    FOREIGN KEY ('symbol') REFERENCES 'stock' ('symbol'),
    UNIQUE KEY 'tick_at_time' ('symbol','time')
);

CREATE table IF NOT EXISTS 'usage' (
    'ID' int NOT NULL AUTO_INCREMENT,
    'symbol' varchar(5) NOT NULL,
    'selected' varchar(512) NOT NULL,
    'date_end' DATETIME NOT NULL,
    'date_start' DATETIME NOT NULL,
    'timestamp' TIMESTAMP NOT NULL,
    'requestor' varchar(50) NOT NULL,
    'type' varchar(10) NOT NULL,
    'latency' float NOT NULL,
    PRIMARY KEY ('ID'),
    FOREIGN KEY ('symbol') REFERENCES 'stock' ('symbol')
);
'''

tickers = ['SPY','GOOG','AAPL','NVDA','MCD','T','MSFT','INTC','BAC','CSCO','GE','QQQ']
names = ['S&P500','Alphabet Inc.','Apple Inc.','Nvidia','McDonalds Corporation','ATT','Microsoft','Intel Corporation','Bank of America','Cisco Systems Inc.','General Electric','Investco QQQ Trust']


stock_setup = """
INSERT IGNORE INTO 'stock' ('symbol', 'name')
VALUES
"""
for i in range(len(tickers)):
    stock_setup = stock_setup + f"('{tickers[i]}','{names[i]}')"
    stock_setup += ',' if i < len(tickers)-1 else ';'

topics = tickers.copy()
topics.append('finapp_usage')

# Set up a callback to handle the '--reset' flag.
def reset_offset(consumer, partitions):
    for p in partitions:
        p.offset = OFFSET_BEGINNING
    consumer.assign(partitions)

def insert_ticker_from_dict(dict):
    return f"""
INSERT IGNORE INTO ticker ('symbol','time','open','close','high','low','volume','interval')
VALUES ({dict['symbol']},{dict['time']},{dict['open']},{dict['close']},{dict['high']},{dict['low']},{dict['volume']},{dict['interval']});
"""

def insert_usage_from_dict(dict):
    return f"""
INSERT IGNORE INTO usage ('symbol','selected','date_end','date_start','timestamp','requestor','type','latency')
VALUES ({dict['symbol']},{dict['selected']},{dict['date_end']},{dict['date_start']},{dict['timestamp']},{dict['requestor']},{dict['type']},{dict['latency']})
"""

if __name__ == '__main__':
    config = {
        'user': 'root',
        'password': os.getenv("db_root_password"),
        'host': os.getenv("MYSQL_SERVICE_HOST"),
        'port': int(os.getenv("MYSQL_SERVICE_PORT")),
        'database': os.getenv("db_name")
    }
    connection = mysql.connector.connect(**config)
    connection.cmd_query(default_statement) # set up DB and tables if not already extant
    connection.cmd_query(stock_setup)
    consumer = Consumer({'bootstrap.servers':'localhost:9092'})
    consumer.subscribe(topics, on_assign=reset_offset)
    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            if msg.error() is None:
                if msg.topic() == 'finapp_usage':
                    # Insert into USAGE
                    # msg key == TIMESTAMP
                    # msg value == dict containing all other info in JSON
                    values = json.loads(msg.value())
                    values['timestamp'] = msg.key()
                    query = insert_usage_from_dict(values)
                    connection.cmd_query(query)
                elif msg.topic() in tickers:
                    # Insert into TICKER
                    # msg key == DATETIME
                    # msg topic == symbol
                    # msg value == dict containing all other info in JSON
                    values = json.loads(msg.value())
                    values['symbol'] = msg.topic()
                    values['time'] = msg.key()
                    query = insert_ticker_from_dict(values)
                    connection.cmd_query(query)
            else:
                pass
                # handle errors





