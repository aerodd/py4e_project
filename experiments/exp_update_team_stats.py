import sqlite3

# Create/Connect to SQLite database to hold data
conn = sqlite3.connect('footballdata.sqlite')
cur = conn.cursor()

# Create a League Table if it does not already exist and empty it's contents
cur.executescript('''
        create table if not exists LeagueTable (
	comp_id integer,
	club_id integer,
	gp integer,
	w integer,
	d integer,
	l integer,
	gf integer,
	ga integer,
	gd integer,
        p integer,
	unique (comp_id, club_id));

        delete from LeagueTable;
	''')

# Select all matches
cur.execute('''
        select team1, team2, team1_score, team2_score, competition
        from Matches
        ''')
matches = cur.fetchall()

# Loop over all matches
for match in matches:

    (team1, team2, team1_score, team2_score, competition) = match

    # Calculate Team 1's Goals For and Goals Against
    team1_gf = team1_score
    team1_ga = team2_score

    # Calculate Team 2's Goals For and Goals Against
    team2_gf = team2_score
    team2_ga = team1_score

    # Initialize Win, Draw, Loss status for both teams
    team1_w, team2_w = [0,0]
    team1_d, team2_d = [0,0]
    team1_l, team2_l = [0,0]

    # Determine Win, Draw, Loss status for both teams
    if team1_score > team2_score:
        team1_w = 1
        team2_l = 1
    elif team2_score > team1_score:
        team2_w = 1
        team1_l = 1
    else:
        team1_d = 1
        team2_d = 1

    # Update the League Table for Team 1
    cur.execute('''
            insert into LeagueTable (comp_id, club_id, gp, w, d, l, gf, ga)
            values(?, ?, ?, ?, ?, ?, ?, ?)
            on conflict (comp_id, club_id)
            do update set
            gp = gp + 1,
            w = w + ?,
            d = d + ?,
            l = l + ?,
            gf = gf + ?,
            ga = ga + ?
            ''', (competition, team1, 1, team1_w, team1_d, team1_l, team1_gf, team1_ga, team1_w, team1_d, team1_l, team1_gf, team1_ga))


    # Update the League Table for Team 2
    cur.execute('''
            insert into LeagueTable (comp_id, club_id, gp, w, d, l, gf, ga)
            values(?, ?, ?, ?, ?, ?, ?, ?)
            on conflict (comp_id, club_id)
            do update set
            gp = gp + 1,
            w = w + ?,
            d = d + ?,
            l = l + ?,
            gf = gf + ?,
            ga = ga + ?
            ''', (competition, team2, 1, team2_w, team2_d, team2_l, team2_gf, team2_ga, team2_w, team2_d, team2_l, team2_gf, team2_ga))

    conn.commit()

conn.close()
