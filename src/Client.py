import requests
from flask import current_app
from Constant import BU


class Mediator:

    @staticmethod
    def process_event(payload, bu):
        current_app.logger.info("Waiting for Mediator ...")
        headers = {}
        headers["X_NO_AUTH"] = "Y"
        headers["event"] = payload["event"]
        headers["X_EVENT_NAME"] = payload["event"]
        headers["X_RESTBUS_GROUP_ID"] = "Y"
        headers["X_CALLBACK_HTTP_URI"] = "Y"
        headers["X_CALLBACK_HTTP_METHOD"] = "Y"
        headers["X_SOURCE"] = "Automation"
        status_code, data = HttpClient.post(BU[bu].mediator_url, payload, headers)
        return status_code


class Tracer:

    @staticmethod
    def get_row(row_key, bu):
        status_code, data = HttpClient.get(BU[bu].tracer_url + row_key)
        return data


class HttpClient:

    @staticmethod
    def get(url, headers={}):
        current_app.logger.info("GET API call :  " + url)
        headers["Content-Type"] = "Application/json"
        response = requests.get(url, headers=headers)
        if not response.content:
            return response.status_code, {}
        else:
            return response.status_code, response.json()

    @staticmethod
    def post(url, payload, headers={}):
        current_app.logger.info("POST API call :  " + url)
        headers["Content-Type"] = "Application/json"
        response = requests.post(url, headers=headers, json=payload)
        if not response.content:
            return response.status_code, {}
        else:
            return response.status_code, response.json()
