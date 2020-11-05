

import asyncio
from os import sys, path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json
import time
from itertools import groupby
from operator import itemgetter
import csv
from postgres_queries import PG
from virustotal import VT, APIError
import logging

apikey = '6bc85c06f769fe6e606eaa4e47648723bbc5f3e42bb627dc327b867b5c7f014c'


pg = PG()
vt = VT(apikey)
risk_keys = ('malicious', 'suspicious', 'malware')
tresholld = timedelta(seconds=17900) # = 1 seconds


def file_read(filename):
    with open(filename,"r",encoding="utf-8") as file_reader:
        for row in file_reader.read().split():
            yield row



def check_in_database(site_url):
    return pg.from_postges_get_request(site_url)



async def make_request_to_virus_total(request):
    try:
        result = await vt.get_data(request, base_url_type='domains')
        return pars_result(result)
    except ValueError as vex:
        print(vex)
        raise vex
    except APIError as ex:
        #TODO wtite errore to log
        print(ex)
        raise ex



def pars_result(data):
    categories = Counter(data['attributes']['categories'].values())

    last_analysis_stats = data['attributes']['last_analysis_stats']

    total_votes = data['attributes']['total_votes']

    arr = data['attributes']['last_analysis_results'].values()
    voting  = defaultdict(int)
    for result, items in groupby(arr, key=itemgetter('result')):
        voting[result]+= len(list(items))

    risk = 'risk' if sum(voting.get(k, 0) for k in risk_keys) > 0 else 'safe'

    return {
        "classification": json.dumps(categories),
        "total_voting": json.dumps(dict(voting)),
        "risk": risk,
        "request" : data['id'],
        "link": str(f"https://virustotal.com/gui/domain/{data['id']}/detection")
    }


def create_report(type_vt, file_name, content=None, permissions='w'):
    with open(file_name, mode=permissions, newline='') as csv_file:
        fieldnames = [type_vt, 'Site Risk', 'Last Update Date',
                      'Link', 'Total Voting', 'Classification']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()



def write_report(type_vt, file_name, content, permissions='a'):
    with open(file_name, mode=permissions, newline='') as csv_file:
        csv_file.write(content)
        csv_file.write("\n")




def report_line_format(data):
    dt = data['last_updated'].strftime('%Y-%m-%d %H:%M:%S')
    tv = " ".join(
        [f"'{k}': {v}" for k,v in data['total_voting'].items()]
        ) if 'total_voting' in data and data['total_voting'] else ""
    clf = " ".join(
      [f"'{k}': {v}" for k,v in data['classification'].items()]
      ) if 'classification' in data and data['classification'] else ""
    output = f"{data['request']};{data['risk']};{dt};{data['link']};{tv};{clf}"
    return output




def _make_sync(future):

    """Utility function that waits for an async call, making it sync."""
    try:
        event_loop = asyncio.get_event_loop()

    except RuntimeError:
        # Generate an event loop if there isn't any.
        event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    return event_loop.run_until_complete(future)





def task(request):
    print('in task {}'.format(request))

    result = check_in_database(request)

    if(result and
       'last_updated' in result and
       (datetime.utcnow() - result.get('last_updated')) < tresholld):
        return report_line_format(result)
    try:
        data = _make_sync(make_request_to_virus_total(request))
        pg_query = pg.queries.get("query_insert_new_request")
        if result and 'request_id' in result:
            data['request_id'] = result.get('request_id')
            pg_query = pg.queries.get("query_update_request")
        new_result = pg.postges_request(pg_query, data)
        #psult)
        print('done with task {}'.format(request))
        time.sleep(15)
        return report_line_format(new_result)
    except ValueError as vex:
        print(vex)
        time.sleep(15)
    except APIError as ex:
        #TODO wtite errore to log
        print(ex)
        time.sleep(15)
                #data[request_id] = result



def main_task(file_request, file_report):

    print('starting main')
    create_report(type_vt='Domains', file_name=file_report, content=None,
                  permissions='w')
    print('waiting for tasks to complete')
    for request in file_read(file_request):
        answer = task(request)
        print('received answer {!r}'.format(answer))
        write_report(type_vt='Domains', file_name=file_report,
                     content=answer, permissions='a')



def main():
    #file_request = "/home/sopka/sites-storage/requests/computer_pollute_report.txt"
    #file_report = "/home/sopka/sites-storage/reports/computer_pollute_report.csv"
    #file_request = "/home/sopka/sites-storage/requests/request1.csv"
    #file_report = "/home/sopka/sites-storage/reports/request_11.csv"
    file_request = "/home/sopka/sites-storage/requests/global.txt"
    file_report = "/home/sopka/sites-storage/reports/global_2.csv"
    #file_request = "/home/sopka/sites-storage/requests/comps2.csv"
    #file_report = "/home/sopka/sites-storage/reports/comps2-2.csv"
    #create_report(type_vt='Domains', file_name=file_report, content=None, permissions='w')


    #check_list = file_read(file_request)

    main_task(file_request, file_report)


if __name__=="__main__":
    # import sysconfig
    # import doctest
    # doctest.testmod()
    _make_sync(main())
