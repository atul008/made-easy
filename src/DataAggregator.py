"""
 * @author Atul Kumar , Date : 08/07/18

"""

from collections import defaultdict

from flask import current_app as app

from Client import Mediator, Tracer


class DataAggregator:

    @staticmethod
    def aggregate(bu, row_keys):
        result = defaultdict(list)
        tracer_records = {}
        total = len(row_keys)
        for i, row in enumerate(row_keys):
            trace = Tracer.get_row(row, bu)
            record_versions = trace["data"]["record_versions"]
            request_payload = None
            for record in record_versions:
                if len(record["cf_details"]) >= 2:
                    record_type = record["cf_details"][1]["columns"]["status"]
                    if record_type == "RAW_DATA":
                        request_payload = record["cf_details"][0]["columns"]["payload"]
                    elif record_type == "RECORDING_COMPLETE":
                        tracer_records[row] = record["cf_details"][0]["columns"]["payload"]["recorderData"]

            if len(record_versions) < 3:
                app.logger.info("Ignoring  : " + row + "as recording length != 3")
                result["ignored"].append(
                    {"row_key": row, "event": request_payload["event"], "entity_id": request_payload["entity_id"]})
            else:
                status_code = Mediator.process_event(request_payload, bu)
                result[status_code].append(
                    {"row_key": row, "event": request_payload["event"], "entity_id": request_payload["entity_id"],
                        "tracer_records": tracer_records[row]})
            percent_processed = (i / total) * 100
            app.logger.info("Processed : " + str(percent_processed)[:5] + " %")

        return result
