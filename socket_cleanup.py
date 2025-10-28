#!env python

###############################################################################
# Author: Kenneth Kaye
# GitHub username: behobu
# Last Updated: 28-Oct-2025
# Requirements: Python >= 3.10, requests, PyGithub
###############################################################################

import os, requests

from base64 import b64encode
from github import Auth
from github import Github

ghPAT = os.getenv("GH_PAT")
socketPAT = b64encode((os.getenv("SOCKET_PAT") + ':').encode('utf-8')).decode()
targetSlug = 'JupiterOne'

ghClient = Github(auth=Auth.Token(ghPAT))
ghOrg = ghClient.get_organization(targetSlug)
ghRepoList = []
print(f'Retrieving list of repositories that belong to the GitHub organization {targetSlug}')
for repo in ghOrg.get_repos(type = 'all', sort = 'full_name'):
    ghRepoList.append(repo.name)
ghClient.close()
print("Retrieved {} repositories".format(len(ghRepoList)))

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
socketDeleteRepoURL = 'https://api.socket.dev/v0/orgs/{targetslug}/repos/{reponame}'
print(f'Deleting repos from Socket that are not active in the {targetSlug} GitHub Organization')
count = 0
for repoName in socketRepoNameList:
    if repoName not in ghRepoList:
        # if it is, then use the Socket API to delete the repo from Socket
        response = requests.delete(socketDeleteRepoURL.format(targetslug = targetSlug, reponame = repoName), headers = socketHeaders)
        if response.status_code != 200:
            print(f"Error deleting {repoName} from Socket")
        else:
            print(f"{repoName} successfully deleted from Socket")
            count += 1
print(f"Deleted {count} repositories from Socket")