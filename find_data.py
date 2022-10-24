from process_data import get_db, get_collection
from datetime import datetime


CODE_NVC = "0001"


def find_road(departure: str, target: str, start_datetime: str):
    db = get_db()
    coll = get_collection(db)

    start_date = start_datetime.split("T")[0]
    start_time = start_datetime.split("T")[1]
    res = coll.aggregate(
        [
            {
                "$match": {
                    "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime": {
                        "$lte": start_datetime
                    }
                }
            },
            {
                "$match": {
                    "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime": {
                        "$gte": start_datetime
                    }
                }
            },
            {
                "$match": {
                    "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": departure
                }
            },
            {
                "$match": {
                    "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": target
                }
            },
            {
                "$match": {
                    "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation.Timing.Time": {
                        "$gte": start_time
                    }
                }
            },
        ]
    )

    for r in res:
        validity_start = r["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"][
            "ValidityPeriod"
        ]["StartDateTime"][:10]
        validity_start = datetime.strptime(validity_start, "%Y-%m-%d")

        # sem treba pozmenit ten datum, ktory budeme dostavat
        act_date = datetime.strptime(start_date, "%Y-%m-%d")
        delta = act_date - validity_start

        if (
            r["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"]["BitmapDays"][
                delta.days
            ]
            == "0"
        ):
            continue

        depart_found = False
        target_found = False
        result_text = ""
        for l in r["CZPTTCISMessage"]["CZPTTInformation"]["CZPTTLocation"]:
            if "TrainActivity" in l:
                if (
                    not depart_found
                    and departure == l["Location"]["PrimaryLocationName"]
                ):
                    depart_found = True
                    result_text += (
                        "######################################################\n"
                    )
                    result_text += (
                        r["CZPTTCISMessage"]["Identifiers"][
                            "PlannedTransportIdentifiers"
                        ][0]["Core"]
                        + "\n"
                    )
                    result_text += (
                        "######################################################\n"
                    )

                if target == l["Location"]["PrimaryLocationName"]:
                    target_found = True
                    if target_found and not depart_found:
                        break

                    found = False
                    if type(l["TrainActivity"]) is dict:
                        if l["TrainActivity"]["TrainActivityType"] == "0001":
                            found = True
                    else:
                        for i in l["TrainActivity"]:
                            if i["TrainActivityType"] == "0001":
                                found = True
                    if not found:
                        break

                if depart_found:
                    # stanice kde je prichod aj odchod
                    if type(l["TimingAtLocation"]["Timing"]) is list:
                        depart_time = l["TimingAtLocation"]["Timing"][1]["Time"]
                    else:  # startovacia a cielova stanica
                        depart_time = l["TimingAtLocation"]["Timing"]["Time"]

                    if type(l["TrainActivity"]) is dict:
                        if l["TrainActivity"]["TrainActivityType"] == "0001":
                            result_text += l["Location"]["PrimaryLocationName"]
                    else:
                        for i in l["TrainActivity"]:
                            if i["TrainActivityType"] == "0001":
                                result_text += l["Location"]["PrimaryLocationName"]
                    result_text += " -- " + depart_time[:8] + "\n"
                    if target_found and depart_found:
                        print(result_text)
                        break
