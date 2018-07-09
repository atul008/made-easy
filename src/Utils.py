"""
 * @author Atul Kumar , Date : 09/07/18 
 
"""

from App import OutboundMessages
from flask import json, jsonify


def get_filtered_outbound_data(record):
    outbound_messages_result = OutboundMessages.query.with_entities(OutboundMessages.message).filter_by(
        correlation_id=record["row_key"]).all()
    outbound_messages = {}
    for om in outbound_messages_result:
        message = json.loads(om[0])
        outbound_messages[message["client_ref_id"]] = {"type": message["type"],
                                                       "party_id_from": message["party_id_from"],
                                                       "party_id_to": message["party_id_to"]}

    return outbound_messages


def get_filtered_tracer_data(tracer_records):
    filtered_records = {}
    for record in tracer_records:
        message = record["entityData"]
        filtered_records[message["client_ref_id"]] = {"type": message["type"],
                                                      "party_id_from": message["party_id_from"],
                                                      "party_id_to": message["party_id_to"]}
    return filtered_records


def validate_params(bu, limit):
    if int(limit) > 1000:
        response = jsonify("Limit should be less than 1000")
        response.status_code = 400
        return response

    if bu not in ("FKMP", "MPCA"):
        response = jsonify("Invalid BU")
        response.status_code = 400
        return response
