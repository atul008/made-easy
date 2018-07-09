"""
 * @author Atul Kumar , Date : 08/07/18

"""

import logging
import time
from logging.handlers import RotatingFileHandler

from flask import Flask, request, jsonify, current_app as app, g
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

import Utils
from Client import Tracer
from DataAggregator import DataAggregator

app = Flask(__name__)
db = SQLAlchemy(app)
ma = Marshmallow(app)


class IdempotencyRequestDetails(db.Model):
    """ Where to regression data from """
    __bind_key__ = "prod_slave_db"

    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.String)
    request_id = db.Column(db.String)
    status = db.Column(db.String)

    def __init__(self, id, entity_id, request_id, status):
        self.id = id
        entity_id = entity_id
        self.request_id = request_id
        self.status = status


class IdempotencyRequestDetailsSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'entity_id', 'request_id', 'status')


class OutboundMessages(db.Model):
    """ Where to pick outbound messages from """
    __bind_key__ = "test_mediator_db"

    id = db.Column(db.Integer, primary_key=True)
    correlation_id = db.Column(db.String)
    message = db.Column(db.String)

    def __init__(self, id, correlation_id, message):
        self.id = id
        correlation_id = correlation_id
        self.message = message


class OutboundMessagesSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'correlation_id', 'message')


request_schema = IdempotencyRequestDetailsSchema()
requests_schema = IdempotencyRequestDetailsSchema(many=True)
outbound_schema = OutboundMessagesSchema()
outbounds_schema = OutboundMessagesSchema(many=True)


# ROUTES #

@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    response.headers["X-EXECUTION-TIME"] = time.time() - g.start
    return response


@app.route('/tracer/<bu>/<row_key>')
def get_from_tracer(bu, row_key):
    return jsonify(Tracer.get_row(row_key, bu))


""" Provide BU and list of request Ids for regression """


@app.route('/regress/<bu>', methods=["POST"])
def regression(bu):
    request_ids = request.get_json()
    app.logger.info("Regression started")
    data, tracer_records = DataAggregator.aggregate(bu, request_ids)
    return jsonify(data)


""" Provide BU and number of records for sanity. 
This route doesn't compare tracer data and outbound messages. 
It is used to just check if anything is broken, look for 206 records """


@app.route('/auto_regress/sanity/<bu>/<limit>', methods=["POST"])
def auto_regression(bu, limit):
    with app.app_context():
        return jsonify(auto_regress(bu, limit))


def auto_regress(bu, limit):
    app.logger.info("Auto regression started")
    Utils.validate_params(bu, limit)
    request_ids_result = IdempotencyRequestDetails.query.with_entities(IdempotencyRequestDetails.request_id).order_by(
        IdempotencyRequestDetails.id.desc()).limit(limit).all()
    request_ids = [request[0] for request in request_ids_result]
    return DataAggregator.aggregate(bu, request_ids)


""" Provide BU and number of records for sanity. 
This route compares tracer data and outbound messages and outputs 
the difference in recording outputs in both """


@app.route('/auto_regress/deep/<bu>/<limit>', methods=["POST"])
def auto_regression_deep(bu, limit):
    with app.app_context():
        data = auto_regress(bu, limit)
        for status, records in data.items():
            if status != "ignored":
                for record in records:
                    record["outbound_messages"] = Utils.get_filtered_outbound_data(record)
                    record["tracer_records"] = Utils.get_filtered_tracer_data(record["tracer_records"])
                    cri_in_outbound_messages = set(record["outbound_messages"].keys())
                    cri_in_tracer_records = set(record["tracer_records"].keys())
                    record["test_report"] = {"matching_records": list(cri_in_outbound_messages & cri_in_tracer_records),
                                             "missing_records": list(cri_in_tracer_records - cri_in_outbound_messages),
                                             "extra_records": list(cri_in_outbound_messages - cri_in_tracer_records)}

        return jsonify(data)


# END ROUTES #

def init_app():
    app.url_map.strict_slashes = False
    app.config.from_object("Config.BaseConfig")

    if app.debug is not True:
        file_handler = RotatingFileHandler('made_easy.log', maxBytes=1024 * 1024 * 100, backupCount=20)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


if __name__ == '__main__':
    with app.app_context():
        init_app()
        app.run(port=app.config.get("PORT"))
