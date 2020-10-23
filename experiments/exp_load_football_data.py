import urllib.request, urllib.parse, urllib.error
import json
import ssl
import re
import sqlite3
import time

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Set github repository directory information
# Reserve URL parts
github_baseurl = 'https://api.github.com'
github_user = 'openfootball'
github_repo = 'football.json'
github_branch = 'master'

# Build URL to retrieve directory contents
url = '/'.join([github_baseurl, 'repos', github_user, github_repo, 'git/trees', github_branch])
url = ''.join([url, '?recursive=1'])

print('\nRetrieving openfootball directory tree from github')
print('Retrieving {}'.format(url))
uh = urllib.request.urlopen(url, context=ctx)
data = uh.read().decode()
print('Retrieved {} characters\n'.format(len(data)))

try:
    js = json.loads(data)
except:
    js = None

if not js or 'tree' not in js:
    print('=== Failure to Retrieve ====')
    print(data)
    exit()

# Save filepaths of files for a specified league
league = input('Enter desired league (ex. en.1):')
if len(league) < 1: league = 'en.1'
league = league.lower()

filepaths = []
for file in js['tree']:
    if file['type'] == 'blob' and re.search(league.replace('.','\.'), file['path']):
        filepaths.append(file['path'])

# Sort files into files with club info and files with results
clubfiles = []
resultfiles = []
for file in filepaths:
    if re.search('clubs',file):
        clubfiles.append(file)
    else:
        resultfiles.append(file)

# Create/Connect to SQLite database to hold data
conn = sqlite3.connect('footballdata.sqlite')
cur = conn.cursor()

cur.executescript('''
        create table if not exists Clubs (
        club_id integer primary key autoincrement, 
        name text unique,
        code text,
        country text );

        create table if not exists Matches (
        match_id integer primary key autoincrement,
        match_date date,
        team1 integer,
        team2 integer,
        team1_score integer,
        team2_score integer,
        competition integer,
        unique(match_date, team1, team2));

        create table if not exists Competitions (
        comp_id integer primary key autoincrement,
        name text unique,
        completed boolean );

        create table if not exists CompetitionClub (
        comp_id integer,
        club_id integer,
        unique(comp_id, club_id));
        ''')

# Load data from files

# Reset github repository directory information
# Reserve URL parts
github_baseurl = 'https://raw.githubusercontent.com'
github_user = 'openfootball'
github_repo = 'football.json'
github_branch = 'master'

# Build URL to retrieve file contents
baseurl = '/'.join([github_baseurl, github_user, github_repo, github_branch])

# Load club data into the database
print('\nLoading club data for {} league'.format(league))

for file in clubfiles:
    print('Retrieving {}'.format(file))
    uh = urllib.request.urlopen('/'.join([baseurl, file]))
    data = uh.read().decode()

    try:
        js = json.loads(data)
    except:
        js = None

    if not js or 'clubs' not in js:
        print('==== Failure to retrieve ====')
        print(data)
        continue

    compname = js['name'].strip()
    print('\tLoading {}'.format(compname))

    cur.execute('''
            insert or ignore into Competitions (name)
            values (?)
            ''', (compname, ))

    cur.execute('''
            select comp_id from Competitions where name = ? limit 1
            ''', (compname, ))
    compid = cur.fetchone()[0]

    for club in js['clubs']:
        name = club['name'].strip()
        if club['code'] == None:
            code = ''
        else:
            code = club['code'].strip()
        country = club['country'].strip()

        #print('{:<35}\t{:<5}\t{:<15}'.format(name, code, country))

        cur.execute('''
                insert or ignore into Clubs (name, code, country)
                values (?, ?, ?)
                ''', (name, code, country))

        cur.execute('''
                select club_id from Clubs where name = ? limit 1
                ''', (name, ))

        clubid = cur.fetchone()[0]

        cur.execute('''
                insert or ignore into CompetitionClub (comp_id, club_id)
                values (?, ?)
                ''', (compid, clubid))

        conn.commit()

# Load match data into the database
print('\nLoading match data for {} league'.format(league))
for file in resultfiles:
    print('Retrieving {}'.format(file))
    uh = urllib.request.urlopen('/'.join([baseurl, file]))
    data = uh.read().decode()

    try:
        js = json.loads(data)
    except:
        js = None

    #if not js or 'rounds' not in js or 'matches' not in js:
    if not js:
        print('==== Failure to retrieve ====')
        print(data)
        continue

    compname = js['name'].strip()
    compcomplete = True
    print('\tLoading {} match data'.format(compname))

    if 'rounds' in js:

        for round in js['rounds']:
            roundname = round['name'].strip()
            #print('\t\tLoading {}'.format(roundname))
            for match in round['matches']:
                matchdate = match['date']
                team1name = match['team1'].strip()
                team2name = match['team2'].strip()
                team1score = match['score']['ft'][0]
                team2score = match['score']['ft'][1]

                #print('{:<35}\t{:<2}:{:>2}\t{:<35}\t{}'.format(team1name, team1score, team2score, team2name, matchdate))
                cur.execute('''
                        select club_id from Clubs
                        where name = ?
                        ''', (team1name, ))
                team1id = cur.fetchone()[0]

                cur.execute('''
                        select club_id from Clubs
                        where name = ?
                        ''', (team2name, ))
                team2id = cur.fetchone()[0]

                cur.execute('''
                        select comp_id from Competitions
                        where name = ?
                        ''', (compname, ))
                compid = cur.fetchone()[0]

                cur.execute('''
                        insert or ignore into Matches (match_date, team1, team2, team1_score, team2_score, competition)
                        values (?, ?, ?, ?, ?, ?)
                        ''', (matchdate, team1id, team2id, team1score, team2score, compid))

                conn.commit()


    if 'matches' in js:

        for match in js['matches']:
            if 'score' in match:
                roundname = match['round'].strip()
                matchdate = match['date']
                team1name = match['team1'].strip()
                team2name = match['team2'].strip()
                team1score = match['score']['ft'][0]
                team2score = match['score']['ft'][1]

                #print('{:<35}\t{:<2}:{:>2}\t{:<35}\t{}'.format(team1name, team1score, team2score, team2name, matchdate))

                cur.execute('''
                        select club_id from Clubs
                        where name = ?
                        ''', (team1name, ))
                team1id = cur.fetchone()[0]

                cur.execute('''
                        select club_id from Clubs
                        where name = ?
                        ''', (team2name, ))
                team2id = cur.fetchone()[0]

                cur.execute('''
                        select comp_id from Competitions
                        where name = ?
                        ''', (compname, ))
                compid = cur.fetchone()[0]

                cur.execute('''
                        insert or ignore into Matches (match_date, team1, team2, team1_score, team2_score, competition)
                        values (?, ?, ?, ?, ?, ?)
                        ''', (matchdate, team1id, team2id, team1score, team2score, compid))

                conn.commit()
            else:
                compcomplete = False

    cur.execute('''
            update Competitions
            set completed = ?
            where comp_id = ?
            ''', (compcomplete, compid ))

    conn.commit()



conn.close()





