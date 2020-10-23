import urllib.request, urllib.parse, urllib.error
import json
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Reserve parts of github URL
# Raw github files are located with the following pattern:
#	https://raw.githubusercontent.com/<user>/<repository>/<branch>/<path_to>/<filename>
github_base_url = 'https://raw.githubusercontent.com'
github_user = 'openfootball'
github_repo = 'football.json'
github_branch = 'master'

github_filepath = '2010-11'
github_file = 'en.1.clubs.json'

# Build URL to desired file
url = '/'.join([github_base_url, github_user, github_repo, github_branch, github_filepath, github_file]) 

print ('Retrieving {}'.format(url))
uh = urllib.request.urlopen(url, context=ctx)
data = uh.read().decode()
print('Retrieved {} characters'.format(len(data)))

try:
    js = json.loads(data)
except:
    js = None

if not js or 'clubs' not in js:
    print('==== Failure to retrieve ====')
    print(data)
    exit()
    

for club in js['clubs']:
    name = club['name']
    code = club['code']
    if code == None: code = ''
    country = club['country']
    print('{:<30}\t{:<6}\t{:<10}'.format(name, code, country))
