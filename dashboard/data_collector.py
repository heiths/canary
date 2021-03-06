import json
import time
import datetime
from collections import deque
import requests


def push_tile(tile_type, tile_key, data):
    tipboard_api_key = "b721f623a67441d68237eb1724f8a3cb"
    tipboard_api_version = "v0.1"
    tipboard_host = "http://localhost:7272"
    tipboard_url = "{0}/api/{1}/{2}/push".format(
        tipboard_host, tipboard_api_version, tipboard_api_key)

    data_to_push = {
        'tile': tile_type,
        'key': tile_key,
        'data': json.dumps(data),
    }

    requests.post(tipboard_url, data=data_to_push)


def run():

    canary_api_host = "http://localhost:8889"
    canary_jobs_path = "/taskflow/jobs/poppy_service_jobs"
    canary_api_url = "{0}/v1.0/jobs?path={1}".format(
        canary_api_host, canary_jobs_path)

    print("Starting Canary Dashboard Data Collector")

    jobcount_series = deque()

    while True:
        # request data from the Canary API
        unclaimed = 0
        claimed = 0
        completed = 0
        total_count = 0

        response = requests.get(canary_api_url)

        jobs = json.loads(response.text)
        jobs_list = []

        if jobs != []:
            jobs_list = jobs[0].get('jobs', [])

            unclaimed = len([
                x for x in jobs_list if x.get('status') == "UNCLAIMED"])
            claimed = len([
                x for x in jobs_list if x.get('status') == "CLAIMED"])
            completed = len([
                x for x in jobs_list if x.get('status') == "COMPLETED"])
            total_count = jobs[0].get('job_count', '0')

        # parse the data for the various supported tiles
        unclaimed_jobs = {
            "title": "Unclaimed Jobs",
            "description": "",
            "just-value": unclaimed
        }

        claimed_jobs = {
            "title": "Claimed Jobs",
            "description": "",
            "just-value": claimed
        }

        completed_jobs = {
            "title": "Completed Jobs",
            "description": "",
            "just-value": completed
        }

        running_jobs = [
            {
                "label": x.get("status"),
                "text": x.get("_name"),
                "description": x.get("_uuid")
            }
            for x in jobs_list]

        jobcount_series.append(
            [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             total_count])

        if len(jobcount_series) > 300:
            jobcount_series.popleft()

        job_series_data = {
            "subtitle": "Jobs Over Time",
            "description": "",
            "series_list": [list(jobcount_series)]
        }

        # post the data to the tipboard api

        push_tile('just_value', "unclaimed_jobs", unclaimed_jobs)
        push_tile('just_value', "claimed_jobs", claimed_jobs)
        push_tile('just_value', "completed_jobs", completed_jobs)
        push_tile('fancy_listing', "running_jobs", running_jobs)
        push_tile('line_chart', "job_series", job_series_data)

        # sleep for interval
        print "Posted Data.  Now Sleep."
        time.sleep(1)

        # loop


if __name__ == '__main__':
    run()
