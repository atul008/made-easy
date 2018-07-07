from Client import Mediator, Tracer
from collections import defaultdict
from flask import current_app


class Tester:

    @staticmethod
    def regress(bu, row_keys):
        result = defaultdict(list)
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

            if len(record_versions) < 3:
                current_app.logger.info("Ignoring  : " + row + "as recording length != 3")
                result["ignored"].append({"row_key": row, "event": request_payload["event"],
                    "entity_id": request_payload["entity_id"]})
            else:
                status_code = Mediator.process_event(request_payload, bu)
                result[status_code].append({
                        "row_key": row, "event": request_payload["event"], "entity_id": request_payload["entity_id"]})
            percent_processed = (i / total) * 100
            current_app.logger.info("Processed : " + str(percent_processed)[:5] + " %")

        return result
