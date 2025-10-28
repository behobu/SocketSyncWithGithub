# SocketSyncWithGithub
This repo contains a script written in Python that will keep the repositories monitored by Socket in sync with those belonging to a GitHub Organization, since Socket doesn't check to see if repositories still exist after their initial ingestion.

# Requirements
#### Python >= 3.10, requests >= 2.32.5, and PyGithub >= 2.8.1

### Socket
A Personal Access Token (PAT) from Socket.dev is required for this script to work properly.  This token must have permissions to list repositories as well as delete them.  By default, this script expects the Socket PAT to be part of the environment variables accessible to the script and named "SOCKET_PAT".  If you would prefer to separate those permissions into separate tokens or already have separate tokens that fulfill those requirements, you may choose to use "SOCKET_PAT_LIST" and "SOCKET_PAT_DEL" instead.

### GitHub
A GitHub (GH) Organization is required for this script to work as-is, but it could easily be modified to do so for a personal GH account also.  A GH PAT is required for this script to work properly, and must have (for granular access tokens) Read access to metadata for all repositories in the organization (make sure to grant the token access to the organization if creating in in a specific user's profile), or the **admin:org** - **read:org** permission for Classic access tokens.  Granular access tokens are preferred.  By default, this script expects the GitHub PAT to be part of the environment variables accessible to the script and named "GH_PAT".

# Running the script
1. If you're on a system that has Python natively installed, don't mess with that version and instead use pyenv (https://github.com/pyenv/pyenv).  It's a good idea to do this regardless honestly.
2. Clone this repository
3. ```pyenv local 3.13.7``` (or whatever version you're using >= 3.10)
4. ```pip install requirements.txt```
5. Set **GH_PAT**=< *your GH PAT* > and **SOCKET_PAT** = < *your Socket PAT* >
5. python socket_cleanup.py --GithubOrgName foo --SocketOrgName bar 