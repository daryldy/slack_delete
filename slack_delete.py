# based on: https://gist.github.com/Paradoxis/6ea7b77f5415c7e72a297b1e48cd8be9

import argparse
import requests
import time
import json
import pprint

def main():
    """
    Entry point of the application
    :return: void
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", required=True, help="Specifies the OAuth token used for authentication. This works with legacy tokens (https://api.slack.com/custom-integrations/legacy-token)")
    parser.add_argument("-d", "--days", type=int, default=None, help="Delete files older than x days (optional)")
    parser.add_argument("-c", "--count", type=int, default=1000, help="Max amount of files to delete at once (optional)")
    options = parser.parse_args()

    try:
        print ("[*] Fetching file list..")
        file_ids = list_file_ids(token=options.token, count=options.count, days=options.days)

        file_count = len(file_ids)
        if file_count > 0:
            do_delete = input("\nDo you want to delete %s file%s? (y/[N]) " % (file_count, 'S' if file_count > 1 else ''))
            if do_delete[0:1].upper() == 'Y':
                print ("[*] Deleting files..")
                delete_files(token=options.token, file_ids=file_ids)

                print ("[*] Done")
            else:
                print ("Nothing deleted")
        else:
            print ("Nothing to delete")

    except KeyboardInterrupt:
        print ("\b\b[-] Aborted")
        exit(1)


def calculate_days(days):
    """
    Calculate days to unix time
    :param days: int
    :return: int
    """
    return int(time.time()) - days * 24 * 60 * 60


def list_file_ids(token, count, days=None):
    """
    Get a list of all file id's
    :param token: string
    :param count: int
    :param days: int
    :return: list
    """
    if days:
        params = {'token': token, 'count': count, 'ts_to': calculate_days(days)}
    else:
        params = {'token': token, 'count': count}

    uri = 'https://slack.com/api/files.list'
    response = requests.get(uri, params=params).json()
    files = response['files']
    for f in files:
        print ('(file ID: %s)' % (f['id']), time.ctime(f['timestamp']), f['name'], )
    return [f['id'] for f in files]


def delete_files(token, file_ids):
    """
    Delete a list of files by id
    :param token: string
    :param file_ids: list
    :return: void
    """

    deleted_count = error_count = 0
    num_files = len(file_ids)
    for file_id in file_ids:
        params = {'token': token, 'file': file_id}
        uri = 'https://slack.com/api/files.delete'
        response = json.loads(requests.get(uri, params=params).text)
        if response["ok"]:
            print ("[+] Deleted file id %s" % (file_id))
            deleted_count += 1
        else:
            print ("[!] Unable to delete file id %s (reason: %s)" % (file_id, response["error"]))
            error_count += 1

    if deleted_count > 0:
        print ("Deleted %s file%s" % (deleted_count, 's' if deleted_count > 1 else '' ))
    if error_count > 0:
        print ("Unable to delete %s files" % (error_count))

if __name__ == '__main__':
    main()
