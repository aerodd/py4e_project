import urllib.request, urllib.parse, urllib.error
import json
import ssl
import re

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get github repository directory
# Reserve URL parts
github_api_baseurl = 'https://api.github.com'
github_user = 'openfootball'
github_repo = 'football.json'
github_branch = 'master'

# Build URL to retrieve directory contents
url = '/'.join([github_api_baseurl, 'repos', github_user, github_repo, 'git/trees', github_branch])
url = ''.join([url, '?recursive=1'])

print('Retrieving {}'.format(url))
uh = urllib.request.urlopen(url, context=ctx)
data = uh.read().decode()
print('Retrieved {} characters'.format(len(data)))

try:
    js = json.loads(data)
except:
    js = None

if not js or 'tree' not in js:
    print('=== Failure to Retrieve ====')
    print(data)
    exit()

# Save filepaths to files for a specified league
league = input('Enter desired league (ex. en.1):')
if len(league) < 1: league = 'en.1'
league = league.lower()

filepaths = []
for file in js['tree']:
    if file['type'] == 'blob' and re.search(league.replace('.','\.'), file['path']):
        filepaths.append(file['path'])

print()
for lcv in filepaths:
    print(lcv)




