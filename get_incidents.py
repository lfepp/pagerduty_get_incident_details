#!/usr/bin/env python

import requests
import sys
import json
from datetime import date, timedelta

#Your PagerDuty API key.  A read-only key will work for this.
AUTH_TOKEN = '8tzeUBJzrqC92XHyzcwx'
#The API base url, make sure to include the subdomain
BASE_URL = 'https://api.pagerduty.com'
#The service ID that you would like to query.  You can leave this blank to query all services.
service_id = ""
#The start date that you would like to search.  It's currently setup to start yesterday.
yesterday = date.today() - timedelta(1)
since = yesterday.strftime('%Y-%m-%d')
#The end date that you would like to search.
until = date.today().strftime('%Y-%m-%d')

HEADERS = {
    'Authorization': 'Token token={0}'.format(AUTH_TOKEN),
    'Content-type': 'application/json',
    'Accept': 'application/vnd.pagerduty+json;version=2'
}

def get_incidents(since, until, service_id=None):
    print "since",since
    print "until",until
    file_name = 'pagerduty_export'

    params = {
        'service':service_id,
        'since':since,
        'until':until
    }

    all_incidents = requests.get(
        '{0}/incidents'.format(BASE_URL),
        headers=HEADERS,
        data=json.dumps(params)
    )

    print "Exporting incident data to " + file_name + since
    for incident in all_incidents.json()['incidents']:
        get_incident_details(incident["id"], str(incident["incident_number"]), incident["service"]["summary"], file_name+since+".csv")
    print "Exporting has completed successfully."

def get_incident_details(incident_id, incident_number, service, file_name):
    start_time = ""
    end_time = ""
    summary = ""
    has_details = False
    has_summary = False
    output = incident_number + "," + service + ","

    f = open(file_name,'a')

    log_entries = requests.get(
        '{0}/incidents/{1}/log_entries?include[]=channel'.format(BASE_URL,incident_id),
        headers=HEADERS
    )

    for log_entry in log_entries.json()['log_entries']:
        if log_entry["type"] == "trigger_log_entry" or log_entry["type"] == "trigger_log_entry_reference":
            if log_entry["created_at"] > start_time:
                start_time = log_entry["created_at"]
                if ("summary" in log_entry["channel"]):
                    has_summary = True
                    summary = log_entry["channel"]["summary"]
                if ("details" in log_entry["channel"]):
                    has_details = True
                    details = log_entry["channel"]["details"]
        elif log_entry["type"] == "resolve_log_entry" or log_entry["type"] == "resolve_log_entry_reference":
            end_time = log_entry["created_at"]

    output += start_time + ","
    output += end_time
    if (has_summary):
        output += ",\"" + summary + "\""
    if (has_details):
        output += ",\"" + str(details) + "\""
    output += "\n"
    print output
    f.write(output)

get_incidents(since = since, until = until, service_id = service_id)
