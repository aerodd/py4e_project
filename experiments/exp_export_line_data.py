import sqlite3
import re

# Connect to SQLite database
conn = sqlite3.connect('footballdata.sqlite')
cur = conn.cursor()

# Get all teams and insert them into a dictionary to hold their league finishes
cur.execute('''
        select name from Clubs
        order by name
        ''')
clubs = cur.fetchall()

club_finishes = dict()
for club in clubs:
    club_finishes[club[0]] = list()

# Create a dictionary to hold season points totals for all teams
club_pointtotals = dict()
for club in clubs:
    club_pointtotals[club[0]] = list()

# Create a list to hold the season years
seasons = list()

# Get all completed competitions
cur.execute('''
        select comp_id, name
        from Competitions
        where completed = True
        ''')
competitions = cur.fetchall()

# Get final table results for each competition
for competition in competitions:
    (comp_id, comp_name) = competition
    seasons.append(re.search(r'[0-9/]+', comp_name).group())

    cur.execute('''
            select row_number () over (order by l.p desc, l.gd desc , l.gf desc) position, c.name, l.p
            from LeagueTable l join clubs c join competitions co
            where l.comp_id = co.comp_id
            and l.club_id = c.club_id
            and l.comp_id = ?
            ''', (comp_id, ))
    table = cur.fetchall()

    #print(comp_name)
    #print(table, '\n')

    # Manipulate the final table results into another form to facilitate generating the lists necessary
    # to graph the data as lines
    ranking = dict()
    for position in table:
        ranking[position[1]] = [position[0], position[2]]

    #print(ranking)

    for club in club_finishes:
        if club in ranking:
            club_finishes[club].append(ranking[club][0])
        else:
            club_finishes[club].append(40)

    for club in club_pointtotals:
        if club in ranking:
            club_pointtotals[club].append(ranking[club][1])
        else:
            club_pointtotals[club].append(-50)



#print(seasons)
#print(club_finishes)
#print(club_pointtotals)

# Export data to js files

points_fh = open('gline_points.js', 'w')
finishes_fh = open('gline_finishes.js', 'w')
 
out_string = "gline = [ ['Season'"
for club in clubs:
    out_string = out_string + ", '" + club[0] + "'"
out_string = out_string + '],'

points_fh.write(out_string)
finishes_fh.write(out_string)

for yr in range(len(seasons)):
    points_string = "['" + seasons[yr] + "'"
    finishes_string = points_string

    for club in clubs:
        points_string = points_string + ', ' + str(club_pointtotals[club[0]][yr])
        finishes_string = finishes_string + ', ' + str(club_finishes[club[0]][yr])

    points_string = points_string + ']'
    finishes_string = finishes_string + ']'
    if seasons[yr] != seasons[-1]:
        points_string = points_string + ','
        finishes_string = finishes_string + ','

    points_fh.write(points_string)
    finishes_fh.write(finishes_string)

out_string = '];'
points_fh.write(out_string)
finishes_fh.write(out_string)

points_fh.close()
finishes_fh.close()





conn.close()
