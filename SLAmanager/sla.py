from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random

app = Flask(__name__)

PROMETHEUS = "http://localhost:9090"

@app.get("/status/metrics/tbc")
def get_statusMetric_tbc():
    metrica = request.args.get("metrica")
    queries = [
        {'query':"query=dspw_telegram_bot_constructor_msg_start"},
        {'query':"query=dspw_telegram_bot_constructor_msg_listconstraint"},
        {'query':"query=dspw_telegram_bot_constructor_msg_listcommands"},
        {'query':"query=dspw_telegram_bot_constructor_msg_showpossibleconstraint"},
        {'query':"query=dspw_telegram_bot_constructor_msg_addconstraint"},
        {'query':"query=dspw_telegram_bot_constructor_msg_deleteconstraint"},
        {'query':"query=dspw_telegram_bot_constructor_messageConstructor_processing_time"}
    ]

    results = None
    for param in queries:
        response = requests.get(PROMETHEUS + '/api/v1/query', params=param)
        results.append(json.loads(response))
    return make_response(results, 200)

@app.get("/status/metrics/tbw")
def get_statusMetric_tbc():
    metrica = request.args.get("metrica")
    queries = [
        {'query':"query=dspw_telegram_bot_writer_send_processing_time"},
        {'query':"query=dspw_telegram_bot_writer_msg_arrived"},
        {'query':"query=dspw_telegram_bot_writer_msg_sended"},
        {'query':"query=dspw_telegram_bot_writer"}
    ]

    results = None
    for param in queries:
        response = requests.get(PROMETHEUS + '/api/v1/query', params=param)
        results.append(json.loads(response))
    return make_response(results, 200)

if __name__ == '__main__':
    app.run(debug=True)
