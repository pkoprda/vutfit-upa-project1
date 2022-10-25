from process_data import get_db, get_collection
from datetime import datetime
from time import strptime, strftime
from pprint import pprint


CODE_NVC = "0001"

class SearchResult:
    def __init__(self, ds = None, dt = None, ts = None, tt = None):
        self.departure_station = ds
        self.departure_time = dt
        self.target_station = ts
        self.target_time = tt


def find_road(departure: str, target: str, start_datetime: str):
    db = get_db()
    coll = get_collection(db)

    start_date, start_time = start_datetime.split("T")
    res = coll.aggregate([
        {
            "$match": {
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime": {
                    "$lte": start_datetime
                },
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime": {
                    "$gte": start_datetime
                },
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": departure,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": target,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation.Timing.Time": {
                    "$gte": start_time
                }
            },
        },
        {
            "$project": {
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime": 1,
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime": 1,
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.BitmapDays": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TrainActivity": 1,
            }
        },
    ])
    
    print("Date: %s | time: %s | search results:" % (start_date, start_time))
    output_text = ""
    ###output = []

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
        ###x = SearchResult()

        for l in r["CZPTTCISMessage"]["CZPTTInformation"]["CZPTTLocation"]:
            if "TrainActivity" in l:
                if (
                    not depart_found
                    and departure == l["Location"]["PrimaryLocationName"]
                ):
                    depart_found = True

                if target == l["Location"]["PrimaryLocationName"]:
                    target_found = True
                    if target_found and not depart_found:
                        break

                    found = False
                    if isinstance(l["TrainActivity"], dict):
                        if l["TrainActivity"]["TrainActivityType"] == "0001":
                            found = True
                    else:
                        for i in l["TrainActivity"]:
                            if i["TrainActivityType"] == "0001":
                                found = True
                    if not found:
                        break

                if depart_found and not target_found:
                    result_text += (
                        "######################################################\n"
                    )

                if depart_found:
                    # stanice kde je prichod aj odchod
                    
                    if isinstance(l["TimingAtLocation"]["Timing"], list):
                        depart_time = l["TimingAtLocation"]["Timing"][1]["Time"]
                    else:  # startovacia a cielova stanica
                        depart_time = l["TimingAtLocation"]["Timing"]["Time"]

                    if isinstance(l["TrainActivity"], dict):
                        if l["TrainActivity"]["TrainActivityType"] == "0001":
                            result_text += l["Location"]["PrimaryLocationName"] + ' -- ' + depart_time[:8] + '\n'
                            
                            ###x.ds=l["Location"]["PrimaryLocationName"]
                            ###x.dt=depart_time[:8]
                    
                    else:
                        for i in l["TrainActivity"]:
                            if i["TrainActivityType"] == "0001":
                                result_text += l["Location"]["PrimaryLocationName"] + ' -- ' + depart_time[:8] + '\n'
                    if target_found:
                        
                        #print("%s" % act_date.date())
                        output_text += result_text
                        ###output.append(x)
                        break
    print(output_text)


def find_road2(departure: str, target: str, start_datetime: str):
    db = get_db()
    coll = get_collection(db)

    start_date, start_time = start_datetime.split("T")
    cursor = coll.aggregate([
        {
            "$match": {
                #"CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": departure,
                #"CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": target,

                "$and": [ # TODO: Treba skontrolovat
                    {"CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": departure},
                    {"CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": target},
                ],
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime": {
                    "$lte": start_datetime
                },
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime": {
                    "$gte": start_datetime
                },
                
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation.Timing.Time": {
                    "$gte": start_time
                }
            },
        },
        {
            "$project": {
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime": 1,
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime": 1,
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.BitmapDays": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TrainActivity": 1,
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "locations": {
                    "$addToSet": {
                        "names": "$CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName",
                        "times": "$CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation.Timing.Time"
                    }
                },
            }
        }
    ])

    i = 0
    results = []

    for document in cursor:
        locations = document["locations"][0]

        # Filter out routes with opposite direction
        if locations["names"].index(departure) > locations["names"].index(target):
            continue

        station_names = locations["names"]
        station_times = locations["times"]
        
        remaining_stations = station_names[locations["names"].index(departure):]
        # Throw out arrival times - keep only departure times, flatten list and parse times
        remaining_times = station_times[locations["names"].index(departure):]
        remaining_times_fixed = list(
            map(
                lambda x: strptime(x, "%H:%M:%S.0000000%z"), 
                [x[-1] if isinstance(x, list) else x for x in remaining_times]
            )
        )

        # Zip stations and departure times together, add them to results
        results.append(list(zip(remaining_stations, remaining_times_fixed)))

    # Sort results
    results = sorted(results, key=lambda x: x[1])

    if len(results) == 0:
        print("Date: %s | time: %s | no results")
    else:
        print("Date: %s | time: %s | search results:" % (start_date, start_time))

    # Printing of results
    for r in results:
        print_str = ""
        for i, entry in enumerate(r):
            station, dep_time = entry
            print_str += station + " (" + strftime("%H:%M", dep_time) + ")"

            if i < len(r) - 1:
                print_str += " --> "

        print(print_str)

