from process_data import get_db, get_collection
from datetime import datetime
from time import strptime, strftime

def find_road(departure: str, target: str, start_datetime: str):
    if departure == target:
        print("The departure station is the same as the destination station")
        return
    
    db = get_db()
    coll = get_collection(db)

    start_date, start_time = start_datetime.split("T")
    cursor = coll.aggregate([
        {
            "$match": {
                "$and": [ # Departure and target station are together in the same document
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
            "$project": { # Output only these fields (get rid of unnecessary fields)
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime": 1,
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime": 1,
                "CZPTTCISMessage.CZPTTInformation.PlannedCalendar.BitmapDays": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation": 1,
                "CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TrainActivity": 1,
            }
        },
        {
            "$group": { # Create a new group structe from aggregation with only relevant data
                "_id": "$_id",
                "locations": {
                    "$addToSet": {
                        "names": "$CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName",
                        "times": "$CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation.Timing.Time"
                    },
                },
                "calendar": {
                    "$addToSet": {
                        "valid_start_datetime": "$CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime",
                        "valid_end_datetime": "$CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime",
                        "bitmap": "$CZPTTCISMessage.CZPTTInformation.PlannedCalendar.BitmapDays",
                    }
                },
                "activity": {
                    "$addToSet": {
                        "type": "$CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TrainActivity",
                    }
                }
            }
        }
    ],
    )

    results = []

    for document in cursor:

        validity_start_date, _ = document["calendar"][0]["valid_start_datetime"].split("T")
        validity_start = datetime.strptime(validity_start_date, "%Y-%m-%d")   

        # sem treba pozmenit ten datum, ktory budeme dostavat
        act_date = datetime.strptime(start_date, "%Y-%m-%d")
        delta = act_date - validity_start

        if (document["calendar"][0]["bitmap"][delta.days] == "1"):
            pass
        else: # == "0"
            continue

        locations = document["locations"][0]

        # Filter out routes with opposite direction
        if locations["names"].index(departure) > locations["names"].index(target):
            continue

        station_names = locations["names"]
        station_times = locations["times"]
        station_activity = document["activity"][0]["type"]
        
        remaining_stations = station_names[locations["names"].index(departure):]
        
        # Throw out arrival times - keep only departure times, flatten list and parse times
        remaining_times = station_times[locations["names"].index(departure):]
        remaining_times_fixed = list(
            map(
                lambda x: strptime(x, "%H:%M:%S.0000000%z"), 
                [x[-1] if isinstance(x, list) else x for x in remaining_times]
            )
        )
        # Get info if the train is for normal passangers (type "0001")
        remaining_activity = station_activity[locations["names"].index(departure):]
        remaining_activity_fixed = []
        for x in remaining_activity:
            if isinstance(x, list):
                if len(list(filter(lambda y: y["TrainActivityType"] == "0001", x))) > 0:
                    remaining_activity_fixed.append(True)
                else:
                    remaining_activity_fixed.append(False)
            else:
                if "0001" == x["TrainActivityType"]:
                    remaining_activity_fixed.append(True)
                else:
                    remaining_activity_fixed.append(False)

        # Zip stations and departure times together, add them to results
        results.append(list(zip(remaining_stations, remaining_times_fixed, remaining_activity_fixed)))

    # Remove station stops which are not for passangers
    new_results = []
    for lines in results:
        new_results.append([x for x in lines if x[2] == True])
    results = [x for x in new_results if x != []] # Remove empty lines

    # Sort results by time in tuple
    results = sorted(results, key=lambda x: x[1]) # (station, departure, activity) 

    if len(results) == 0:
        print(f"Date: {start_date}\nTime: {start_time}\nNo results found")
        return
    else:
        print(f"Date: {start_date}\nTime: {start_time}\nSearch results:")

    start_time_ms = datetime.strptime(start_time, "%H:%M:%S").time()

    # Printing of results
    for r in results:
        print_str = ""
        for i, entry in enumerate(r):
            station, dep_time, _ = entry
            # Have to do this because DB aggregation won't couple time with the departure station
            train_time_ms = datetime.strptime(strftime('%H:%M:%S', dep_time), "%H:%M:%S").time()
            if start_time_ms > train_time_ms:
                break

            print_str += station + " (" + strftime("%H:%M", dep_time) + ")"

            if i < len(r) - 1:
                print_str += " --> "

        if train_time_ms and train_time_ms >= start_time_ms:
            print(print_str)
