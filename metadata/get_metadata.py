# get metadata on funding for openneuro datasets

import requests
import json
from simplejson.errors import JSONDecodeError

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Origin': 'https://openneuro.org',
    'accessToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTI0OTc3NC02ZDkxLTQ4MDUtOTY1YS1hODNhNzY1MzYzYTQiLCJlbWFpbCI6InBvbGRyYWNrQGdtYWlsLmNvbSIsInByb3ZpZGVyIjoiZ29vZ2xlIiwibmFtZSI6IlJ1c3MgUG9sZHJhY2siLCJhZG1pbiI6dHJ1ZSwiaWF0IjoxNjIyNjU4NDM1LCJleHAiOjE2NTQxOTQ0MzV9.cuMmSr4VDlSBDdZVKU567t7p_Hxf_nti9hXzOdXEzeA'
}

def get_dataset_ids():
    # get all dataset ids

    data = '{"query":"query testq{datasets {edges {cursor, node {id}}}}"}'
    response = requests.post('https://openneuro.org/crn/graphql', headers=headers, data=data)
    response = response.json()

    dataset_ids = []

    while True:
        for y in response['data']['datasets']['edges']:
            print(y['node']['id'])
            dataset_ids.append(y['node']['id'])
        if len(response['data']['datasets']['edges']) < 25:
            break

        next_cur = y['cursor']
        data = f'{{"query": "query testq{{datasets(after: \\"{next_cur}\\") {{edges {{cursor, node {{id}}}}}}}}"}}'
        response = requests.post('https://openneuro.org/crn/graphql', headers=headers, data=data)
        response = response.json()
    return(dataset_ids)


# may want to use this to get all snapshots
snapshot_query = '"query { dataset(id: \\"%s\\") { snapshots {id}}}"'

def get_snapshots(id):
    data = '{"query": %s}' % (snapshot_query % id)
    response = requests.post('https://openneuro.org/crn/graphql', headers=headers, data=data)
    md = response.json()
    return([i['id'] for i in md['data']['dataset']['snapshots']])


metadata_query_latest = '"query { dataset(id: \\"%s\\") { latestSnapshot { id description { Name Funding Acknowledgements }}}}"'
metadata_query_tag = '"query { snapshot(datasetId: \\"%s\\", tag:\\"%s\\") { id description { Name Funding Acknowledgements }}}"'

def get_metadata(id):
    # get funding/acknowledgements for a specific dataset
    # 
    if id.find(':') > -1:
        id, tag = id.split(':')
        data = '{"query": %s}' % (metadata_query_tag % (id, tag))
    else:
        tag = None
        data = '{"query": %s}' % (metadata_query_latest % id)
    #print(data)
    response = requests.post('https://openneuro.org/crn/graphql', headers=headers, data=data)
    return(response.json())


if __name__ == '__main__':
    print("getting dataset ids")
    dataset_ids = get_dataset_ids()
    print(f'found {len(dataset_ids)} datasets')
    print('loading metadata')
    metadata = {}
    snapshots = {}
    for id in dataset_ids:
        snapshots[id] = get_snapshots(id)
        for s in snapshots[id]:
            try:
                metadata[s] = get_metadata(s)
            except:  # I KNOW THIS IS BAD
                # just try again
                try:
                    print('retrying', s)
                    metadata[s] = get_metadata(s)
                except:
                    metadata[s] = None
                    print('tried twice and failed:', s)
        #print(metadata[s])

    with open('funding_metadata.json', 'w') as f:
        json.dump(metadata, f)