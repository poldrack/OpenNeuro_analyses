# get metadata on funding for openneuro datasets

import requests
import json
import sys

headers = {
#    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Origin': 'https://openneuro.org',
    'accessToken': None
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


def get_snapshots(id):
    snapshot_query = '"query { dataset(id: \\"%s\\") { snapshots {id}}}"'
    data = '{"query": %s}' % (snapshot_query % id)
    response = requests.post('https://openneuro.org/crn/graphql', headers=headers, data=data)
    md = response.json()
    if md['data']['dataset']['snapshots'] is not None:
        return([i['id'] for i in md['data']['dataset']['snapshots']])
    else:
        return([])


def get_metadata(id, verbose=False):
    # get funding/acknowledgements for a specific dataset
    if id.find(':') > -1:
        id, tag = id.split(':')
        metadata_query_tag = '"query { snapshot(datasetId: \\"%s\\", tag:\\"%s\\") { id description { Name Funding Acknowledgements }}}"'
        data = '{"query": %s}' % (metadata_query_tag % (id, tag))
    else:
        tag = None
        metadata_query_latest = '"query { dataset(id: \\"%s\\") { latestSnapshot { id readme description { Name Funding Acknowledgements }}}}"'
        data = '{"query": %s}' % (metadata_query_latest % id)
    if verbose:
        print(data)
    response = requests.post('https://openneuro.org/crn/graphql', headers=headers, data=data)
    return(response.json())


if __name__ == '__main__':
    try:
        with open('api_key.txt') as f:
            headers['accessToken'] = f.readline().strip()
    except FileNotFoundError:
        print("You must first generate an API key at OpenNeuro.org and store it to api_key.txt")
        sys.exit()
    print("getting dataset ids")
    dataset_ids = get_dataset_ids()
    print(f'found {len(dataset_ids)} datasets')
    print('loading metadata')
    metadata = {}
    snapshots = {}
    for id in dataset_ids:
        # there is a bug in graphql such that it won't return readme 
        # for specific snapshots, only for latest
        # so we will load latest and then insert it into the snapshots
        latest_snapshot = get_metadata(id)
        snapshots[id] = get_snapshots(id)
        for s in snapshots[id]:
            try:
                metadata[s] = get_metadata(s)
            except:  # I KNOW BARE EXCEPTS ARE BAD
                # just try again, sometimes randomly fails
                try:
                    print('retrying', s)
                    metadata[s] = get_metadata(s)
                except:
                    metadata[s] = None
                    print('tried twice and failed:', s)
            metadata[s]['readme'] = latest_snapshot[
                'data']['dataset']['latestSnapshot']['readme']
            metadata[s]['latestSnapshot'] = latest_snapshot[
                'data']['dataset']['latestSnapshot']['id']
    with open('../data/openneuro/db_metadata.json', 'w') as f:
        json.dump(metadata, f)
