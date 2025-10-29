#!env python

###############################################################################
# Author: Kenneth Kaye
# GitHub username: behobu
# Last Updated: 28-Oct-2025
# Requirements: Python >= 3.10, requests, PyGithub
###############################################################################

import argparse, os, requests

from base64 import b64encode
from github import Auth
from github import Github

parser = argparse.ArgumentParser(
    prog='Socket Sync Repos With Github',
    description='A script that will sync repositories monitored by Socket with active repositories within a GitHub Organization'
)
parser.add_argument('-g', '--GithubOrgName', required=True, dest='ghSlug')
parser.add_argument('-s', '--SocketOrgName', required=True, dest='socketSlug')


def get_github_repos(targetSlug):
    patName = 'GH_PAT'
    if patName not in os.environ:
        exit(f"Please set an environment variable named {patName} with the value of your GitHub Personal Access Token and then re-run this script.")
    ghPAT = os.getenv(patName)
    ghClient = Github(auth=Auth.Token(ghPAT))
    ghOrg = ghClient.get_organization(targetSlug)
    ghRepoList = []
    print(f'Retrieving list of repositories that belong to the GitHub organization {targetSlug}')
    for repo in ghOrg.get_repos(type = 'all', sort = 'full_name'):
        ghRepoList.append(repo.name)
    ghClient.close()
    print("Retrieved {} repositories".format(len(ghRepoList)))
    return ghRepoList

def get_socket_repos(targetSlug):
    patName = 'SOCKET_PAT'
    if patName not in os.environ:
        if 'SOCKET_PAT_LIST' not in os.environ:
            exit(f"Please set an environment variable named {patName} with the value of your Socket Personal Access Token and then re-run this script.")
        else:
            patName = 'SOCKET_PAT_LIST'
    socketPAT = b64encode((os.getenv(patName) + ':').encode('utf-8')).decode()
    socketListReposURL = f'https://api.socket.dev/v0/orgs/{targetSlug}/repos'
    socketParams = {
        'sort'            : 'created_at', 
        'direction'       : 'desc', 
        'per_page'        : 100, 
        'include_archived': 'false',
        'page'            : 1
    }
    socketRepoList = []
    socketHeaders = {
        'accept': 'application/json',
        'Authorization': f'Basic {socketPAT}'
    }
    socketResponseJSON = {'nextPage': socketParams['page']}
    print('Retrieving list of repositories monitored by Socket')
    while socketResponseJSON['nextPage']:
        socketResponse = requests.get(socketListReposURL, headers = socketHeaders, params = socketParams)
        if socketResponse.status_code != 200:
            exit('Failed to get list of repositories monitored by Socket')
        else:
            socketResponseJSON = socketResponse.json()
            socketRepoList.extend(socketResponseJSON['results'])
            socketParams['page'] = socketResponseJSON['nextPage']
    print("Retrieved {} repositories".format(len(socketRepoList)))
    socketRepoNameList = [repo['name'] for repo in socketRepoList if not repo['name'].startswith('.')]
    socketRepoNameList.sort()
    return socketRepoNameList

def compare_and_remove(ghRepoList, socketRepoList, socketSlug):
    patName = 'SOCKET_PAT'
    if patName not in os.environ:
        if 'SOCKET_PAT_DEL' not in os.environ:
            exit(f"Please set an environment variable named {patName} with the value of your Socket Personal Access Token and then re-run this script.")
        else:
            patName = 'SOCKET_PAT_DEL'
    socketPAT = b64encode((os.getenv(patName) + ':').encode('utf-8')).decode()
    socketHeaders = {
        'accept': 'application/json',
        'Authorization': f'Basic {socketPAT}'
    }
    socketDeleteRepoURL = 'https://api.socket.dev/v0/orgs/{targetslug}/repos/{reponame}'
    print(f'Deleting repos from Socket that are not active in the GitHub Organization')
    count = 0
    for repoName in socketRepoList:
        if repoName not in ghRepoList:
            # if it is not, then use the Socket API to delete the repo from Socket
            response = requests.delete(socketDeleteRepoURL.format(targetslug = socketSlug, reponame = repoName), headers = socketHeaders)
            if response.status_code != 200:
                print(f"Error deleting {repoName} from Socket")
            else:
                #print(f"{repoName} successfully deleted from Socket")
                count += 1
    print(f"Deleted {count} repositories from Socket")


if __name__ == '__main__':
    args = parser.parse_args()
    ghRepoList = get_github_repos(args.ghSlug)
    socketRepoList = get_socket_repos(args.socketSlug)
    compare_and_remove(ghRepoList, socketRepoList, args.socketSlug)