# get metadata on funding for openneuro datasets

import requests
import json

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Origin': 'https://openneuro.org',
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
    pass


metadata_query = '"query { dataset(id: \\"%s\\") { latestSnapshot { id description { Name Funding Acknowledgements }}}}"'

def get_metadata(id):
    # get funding/acknowledgements for a specific dataset
    # 
    data = '{"query": %s}' % (metadata_query % id)
    response = requests.post('https://openneuro.org/crn/graphql', headers=headers, data=data)
    return(response.json())


if __name__ == '__main__':
    dataset_ids = get_dataset_ids()

    metadata = {}

    for id in dataset_ids:
        metadata[id] = get_metadata(id)
        print(metadata[id])

    with open('funding_metadata.json', 'w') as f:
        json.dump(metadata, f)