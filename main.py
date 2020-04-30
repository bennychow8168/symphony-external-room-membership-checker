import logging, json, csv
from datetime import datetime
from pytz import timezone
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.clients.stream_client import StreamClient


def configure_logging():
    logging.basicConfig(
            filename='./logs/output.log',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filemode='w', level=logging.DEBUG
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main():
    print('Python Client runs using RSA authentication')

    # Configure log
    configure_logging()

    # RSA Auth flow: pass path to rsa config.json file
    configure = SymConfig('./resources/config.json')
    configure.load_config()
    auth = SymBotRSAAuth(configure)
    print('Start Authenticating..')
    logging.info('Start Authenticating..')
    auth.authenticate()

    # Initialize SymBotClient with auth and configure objects
    bot_client = SymBotClient(auth, configure)
    stream_client = StreamClient(bot_client)

    # Retrieve list of streams
    print('Retrieve All External Active Streams...')
    logging.info('Retrieve All External Active Streams...')

    external_steams = retrieve_active_external_streams(stream_client)

    print(f'Retrieved {str(len(external_steams["streams"]))} streams')
    logging.info(f'Retrieved {str(len(external_steams["streams"]))} streams')


    print('Checking streams for violations...')
    logging.info('Checking streams for violations...')

    violation_streams = []
    for s in external_steams["streams"]:
        stream_id = s['id']

        # Get memberships in each stream
        memberships = get_all_stream_members(bot_client, stream_id)

        # Check if each stream contains at least 2 internal users
        internal_count = 0
        s['internalDisplayNames'] = []
        s['externalCompanyName'] = "N/A"
        s['membersCount'] = len(memberships["members"])
        s['roomCreatorName'] = "N/A"

        for member in memberships["members"]:
            if member['user']['isExternal'] == False:
                internal_count = internal_count + 1
                s['internalDisplayNames'].append(member['user']['displayName'])
            else:
                if 'company' in member['user']:
                    s['externalCompanyName'] = member['user']['company']

            if member['isCreator'] and 'displayName' in member['user']:
                s['roomCreatorName'] = member['user']['displayName']

            # Skip the rest if already found 2 internal users
            if internal_count >= 2 and s['externalCompanyName'] != "N/A" and s['roomCreatorName'] != "N/A":
                logging.debug(f'{stream_id} meets criteria..PASSED!')
                break

        if internal_count < 2:
            logging.debug(f'{stream_id} does not meet criteria..FAILED')
            violation_streams.append(s)

    print(f'Total Violations - {str(len(violation_streams))}')
    logging.info(f'Total Violations - {str(len(violation_streams))}')

    # Print final result
    print(f'Generating Result File...')
    logging.info(f'Generating Result File...')
    print_result(violation_streams)

    return


def print_result(stream_list):
    # Manipulate Create DateTime
    utc = timezone('UTC')
    sydney = timezone('Australia/Sydney')
    file_name = "result_" + datetime.now(sydney).strftime('%Y-%m-%d_%H%M%S') + ".csv"

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Room Name', 'Date Created', 'Room Created By', 'Ext Counterparty Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for s in stream_list:
            create_date = datetime.utcfromtimestamp(s["attributes"]["createdDate"] / 1000)
            create_date = utc.localize(create_date)
            create_date_local = create_date.astimezone(sydney).strftime('%Y-%m-%d %H:%M:%S %Z')
            if s["type"] == "MIM":
                writer.writerow(
                    {'Room Name': 'MIM', 'Date Created': create_date_local, 'Room Created By': s["roomCreatorName"],
                     'Ext Counterparty Name': s["externalCompanyName"]})
            else:
                writer.writerow({'Room Name': s["attributes"]["roomName"], 'Date Created': create_date_local,
                                 'Room Created By': s["roomCreatorName"],
                                 'Ext Counterparty Name': s["externalCompanyName"]})

    return


def retrieve_active_external_streams(stream_client):
    output = json.loads(json.dumps(stream_client.list_streams_enterprise_v2(skip=0, limit=100, streamTypes=[{"type": "MIM"}, {"type": "ROOM"}], scope="EXTERNAL", status="ACTIVE")))
    while len(output["streams"]) < output["count"]:
        next_out = json.loads(json.dumps(stream_client.list_streams_enterprise_v2(skip=int(len(output["streams"])), limit=100, streamTypes=[{"type": "MIM"}, {"type": "ROOM"}], scope="EXTERNAL", status="ACTIVE")))
        for index in range(len(next_out["streams"])): output["streams"].append(next_out["streams"][index])

    return output


def get_all_stream_members(bot_client, stream_id):
    memberships = json.loads(json.dumps(get_stream_members(bot_client, stream_id, skip=0, limit=100)))
    while len(memberships["members"]) < memberships["count"]:
        next_members = json.loads(json.dumps(
            get_stream_members(bot_client, stream_id, skip=int(len(memberships["members"])), limit=100)))
        for index in range(len(next_members["members"])): memberships["members"].append(
            next_members["members"][index])

    return memberships


def get_stream_members(bot_client, stream_id, skip=0, limit=100):
    """
    Returns a list of all the current members of a stream (IM, MIM, or chatroom
    Required Permissions:
    To get the stream membership of any stream in your enterprise, you should
    call this endpoint with a Service User account with the User Provisioning role.
    The Service User does not need to be a member of the stream.
    See Permissions for a list of roles and associated privileges.
    """
    logging.debug('StreamClient/get_stream_members()')
    url = '/pod/v1/admin/stream/{0}/membership/list'.format(stream_id)
    params = {
        'skip': skip,
        'limit': limit
    }
    return bot_client.execute_rest_call('GET', url, params=params)


if __name__ == "__main__":
    main()