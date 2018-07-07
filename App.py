from flask import Flask, request, jsonify, g
from Client import Tracer
from Tester import Tester
from logging.handlers import RotatingFileHandler
import logging, time

app = Flask(__name__)


@app.before_request
def before_request():
  g.start = time.time()


@app.after_request
def after_request(response):
    response.headers["X-EXECUTION-TIME"] = time.time() - g.start
    return response


@app.route('/tracer/<bu>/<row_key>')
def get_from_tracer(bu, row_key):
    app.logger.info("Getting data from tracer  for row key " + row_key)
    return jsonify(Tracer.get_row(row_key, bu))


@app.route('/regress/<bu>', methods=["POST"])
def start_regression(bu):
    request_ids = request.get_json()
    app.logger.info("Got request to start regressing for input ")
    return jsonify(Tester.regress(bu, request_ids))


if __name__ == '__main__':
    app.url_map.strict_slashes = False
    app.config.from_object("Config.BaseConfig")
    if app.debug is not True:
        file_handler = RotatingFileHandler('made_easy.log', maxBytes=1024 * 1024 * 100, backupCount=20)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    app.run(port=app.config.get("PORT"))