import sqlite3
from flask import Flask, request, render_template, redirect, url_for

# Initialize Flask application
app = Flask(__name__)

def init_db():
    """
    Initializes the database by creating required tables if they don't exist.
    Creates two separate SQLite databases:
    1. football.db - For storing football player stats
    2. basketball.db - For storing basketball player stats
    """
    # Initialize football database
    conn = sqlite3.connect('football.db')
    cursor = conn.cursor()
    # Create football table with columns for player stats:
    # - id: Unique identifier for each record
    # - team: Team identifier (1 or 2)
    # - player_name: Name of the player
    # - goals: Number of goals scored by the player
    # - penalties: Number of penalties received by the player
    cursor.execute('''CREATE TABLE IF NOT EXISTS football (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        team TEXT,
                        player_name TEXT,
                        goals INTEGER,
                        penalties INTEGER
                    )''')
    conn.commit()
    conn.close()
    
    # Initialize basketball database
    conn = sqlite3.connect('basketball.db')
    cursor = conn.cursor()
    # Create basketball table with columns for player stats:
    # - id: Unique identifier for each record
    # - team: Team identifier (1 or 2)
    # - player_name: Name of the player
    # - points: Total points scored by the player
    # - twoPointers: Number of 2-point shots made
    # - threePointers: Number of 3-point shots made
    # - freeThrows: Number of free throws made
    cursor.execute('''CREATE TABLE IF NOT EXISTS basketball (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        team TEXT,
                        player_name TEXT,
                        points INTEGER,
                        twoPointers INTEGER,
                        threePointers INTEGER,
                        freeThrows INTEGER
                    )''')
    conn.commit()
    conn.close()

# Call init_db() when the application starts to ensure database tables exist
init_db()

# Initialize football game state
# This dictionary stores the current state of a football match including:
# - Teams and their names
# - Player lists for each team
# - Current score for each team
# - Team stats (goals and penalties)
# - Match status (ended or not) and result message
football_games = {
    "team1": {
        "name": "Team 1",
        "players": [],  # Will store player objects with their stats
        "score": 0,     # Team's total score
        "stats": {"goals": 0, "penalties": 0}  # Team-level statistics
    },
    "team2": {
        "name": "Team 2",
        "players": [],
        "score": 0,
        "stats": {"goals": 0, "penalties": 0}
    },
    "match_ended": False,  # Flag to track if the match is over
    "result": ""           # Will store the result message after match ends
}

# Initialize basketball game state
# Similar to football_games, this dictionary stores the current state of a basketball game
basketball_games = {
    "team1": {
        "name": "Team 1",
        "players": [],  # Will store player objects with their stats
        "score": 0      # Team's total score
    },
    "team2": {
        "name": "Team 2",
        "players": [],
        "score": 0
    },
    "match_ended": False,  # Flag to track if the game is over
    "result": ""           # Will store the result message after game ends
}

# ----- FOOTBALL ROUTES -----

@app.route('/football')
def football_index():
    """
    Renders the football.html template with the current game state.
    This is the main page for the football score tracker.
    
    Returns:
        Rendered HTML template with current game state data
    """
    return render_template('football.html', 
                        team1=football_games["team1"], 
                        team2=football_games["team2"], 
                        match_ended=football_games["match_ended"], 
                        result=football_games["result"])

@app.route('/football/add_player', methods=['POST'])
def football_add_player():
    """
    Handles POST requests to add a new player to a football team.
    1. Extracts team and player name from the form data
    2. Inserts the player into the database with initial stats (0)
    3. Adds the player to the in-memory team roster
    4. Redirects back to the football index page
    
    Returns:
        Redirect to the football index page
    """
    # Get form data
    team = request.form['team']
    player_name = request.form['player_name']
    
    try:
        # Connect to the football database
        conn = sqlite3.connect('football.db')
        cursor = conn.cursor()
        # Insert new player with initial stats (0 goals, 0 penalties)
        cursor.execute("INSERT INTO football (team, player_name, goals, penalties) VALUES (?, ?, 0, 0)", (team, player_name))
        conn.commit()
        
        # Add player to the in-memory list for the correct team
        if team == "1":
            football_games["team1"]["players"].append({"name": player_name, "goals": 0, "penalties": 0})
        elif team == "2":
            football_games["team2"]["players"].append({"name": player_name, "goals": 0, "penalties": 0})
    except sqlite3.Error as e:
        # Log database errors
        print(f"Database error: {e}")
    finally:
        # Ensure connection is closed even if an error occurs
        conn.close()
    
    # Redirect back to the main football page
    return redirect(url_for('football_index'))

@app.route('/football/update_score', methods=['POST'])
def football_update_score():
    """
    Updates a player's statistics and team score when a goal is scored or penalty is given.
    1. Gets team, player index, and action type from form data
    2. Updates the player's stats in memory
    3. Updates the team's stats in memory
    4. Updates the player's record in the database
    5. Redirects back to the football index page
    
    Returns:
        Redirect to the football index page
    """
    # Extract data from form
    team = request.form['team']
    player_index = int(request.form['player_index'])
    action = request.form['action']

    # Get the correct team's player list
    players_list = football_games["team1"]["players"] if team == "1" else football_games["team2"]["players"]
    
    # Make sure the player index is valid
    if 0 <= player_index < len(players_list):
        player = players_list[player_index]
        
        # Handle different actions
        if action == 'goal':
            # Increase player's goal count
            player["goals"] += 1
            # Increase team's score
            football_games[f"team{team}"]["score"] += 1
            # Update team stats
            football_games[f"team{team}"]["stats"]["goals"] += 1
        elif action == 'penalty':
            # Increase player's penalty count
            player["penalties"] += 1
            # Update team stats
            football_games[f"team{team}"]["stats"]["penalties"] += 1

        # Update the database to reflect the changes
        try:
            conn = sqlite3.connect('football.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE football SET goals = ?, penalties = ? WHERE team = ? AND player_name = ?", 
                        (player["goals"], player["penalties"], team, player["name"]))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    # Redirect back to the main football page
    return redirect(url_for('football_index'))

@app.route('/football/end_match', methods=['POST'])
def football_end_match():
    """
    Ends the current football match and determines the result.
    1. Sets the match_ended flag to True
    2. Compares team scores to determine the winner
    3. Sets the result message based on the outcome
    4. Redirects back to the football index page
    
    Returns:
        Redirect to the football index page
    """
    # Mark the match as ended
    football_games["match_ended"] = True
    
    # Determine the match result based on team scores
    if football_games["team1"]["score"] > football_games["team2"]["score"]:
        football_games["result"] = f"{football_games['team1']['name']} wins!"
        winning_team = football_games["team1"]
    elif football_games["team2"]["score"] > football_games["team1"]["score"]:
        football_games["result"] = f"{football_games['team2']['name']} wins!"
        winning_team = football_games["team2"]
    else:
        football_games["result"] = "It's a draw!"
        winning_team = None

    # Find the top scorer from the winning team
    top_scorer = None
    if winning_team:
        top_scorer = max(winning_team["players"], key=lambda x: x["goals"], default=None)
        if top_scorer:
            football_games["top_scorer"] = f"Top Scorer: {top_scorer['name']} with {top_scorer['goals']} goals"
        else:
            football_games["top_scorer"] = "No top scorer"
    else:
        football_games["top_scorer"] = "No top scorer (draw)"
    
    return render_template('football.html', 
                            team1=football_games["team1"], 
                            team2=football_games["team2"], 
                            match_ended=football_games["match_ended"], 
                            result=football_games["result"],
                            top_scorer=football_games["top_scorer"])

    # # Redirect back to the main football page
    # return redirect(url_for('football_index'))

# ----- BASKETBALL ROUTES -----

@app.route('/basketball')
def basketball_index():
    """
    Renders the basketball.html template with the current game state.
    This is the main page for the basketball score tracker.
    
    Returns:
        Rendered HTML template with current game state data
    """
    return render_template('basketball.html', 
                        team1=basketball_games["team1"], 
                        team2=basketball_games["team2"], 
                        match_ended=basketball_games["match_ended"], 
                        result=basketball_games["result"])

@app.route('/basketball/add_player', methods=['POST'])
def basketball_add_player():
    """
    Handles POST requests to add a new player to a basketball team.
    1. Extracts team and player name from the form data
    2. Inserts the player into the database with initial stats (all 0)
    3. Adds the player to the in-memory team roster
    4. Redirects back to the basketball index page
    
    Returns:
        Redirect to the basketball index page
    """
    # Get form data
    team = request.form['team']
    player_name = request.form['player_name']
    
    try:
        # Connect to the basketball database
        conn = sqlite3.connect('basketball.db')
        cursor = conn.cursor()
        # Insert new player with initial stats (all zeros)
        cursor.execute("INSERT INTO basketball (team, player_name, points, twoPointers, threePointers, freeThrows) VALUES (?, ?, 0, 0, 0, 0)", (team, player_name))
        conn.commit()
        
        # Add player to the in-memory list for the correct team
        if team == "1":
            basketball_games["team1"]["players"].append({"name": player_name, "points": 0, "twoPointers": 0, "threePointers": 0, "freeThrows": 0})
        elif team == "2":
            basketball_games["team2"]["players"].append({"name": player_name, "points": 0, "twoPointers": 0, "threePointers": 0, "freeThrows": 0})
    except sqlite3.Error as e:
        # Log database errors
        print(f"Database error: {e}")
    finally:
        # Ensure connection is closed even if an error occurs
        conn.close()
    
    # Redirect back to the main basketball page
    return redirect(url_for('basketball_index'))

@app.route('/basketball/add_points', methods=['POST'])
def add_points():
    """
    Updates a player's points and statistics when they score.
    1. Gets team, player index, and point value from form data
    2. Updates the player's stats in memory (points and shot type counters)
    3. Updates the team score
    4. Updates the player's record in the database
    5. Redirects back to the basketball index page
    
    Returns:
        Redirect to the basketball index page
    """
    # Extract data from form
    team = request.form['team']
    player_index = int(request.form['player_index'])
    points = int(request.form['points'])

    # Get the correct team's player list
    players_list = basketball_games["team1"]["players"] if team == "1" else basketball_games["team2"]["players"]
    
    # Make sure the player index is valid
    if 0 <= player_index < len(players_list):
        player = players_list[player_index]
        # Increase player's points
        player["points"] += points
        # Increase team's score
        basketball_games[f"team{team}"]["score"] += points

        # Update shot type counters based on points value
        if points == 2:
            player["twoPointers"] += 1
        elif points == 3:
            player["threePointers"] += 1
        elif points == 1:
            player["freeThrows"] += 1

        # Update the database to reflect the changes
        try:
            conn = sqlite3.connect('basketball.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE basketball SET points = ?, twoPointers = ?, threePointers = ?, freeThrows = ? WHERE team = ? AND player_name = ?", 
                        (player["points"], player["twoPointers"], player["threePointers"], player["freeThrows"], team, player["name"]))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    # Redirect back to the main basketball page
    return redirect(url_for('basketball_index'))

@app.route('/basketball/end_game', methods=['POST'])
def end_game():
    """
    Ends the current basketball game and determines the result.
    1. Sets the match_ended flag to True
    2. Compares team scores to determine the winner
    3. Sets the result message based on the outcome
    4. Redirects back to the basketball index page
    
    Returns:
        Redirect to the basketball index page
    """
    # Mark the game as ended
    basketball_games["match_ended"] = True
    
    # Determine the game result based on team scores
    if basketball_games["team1"]["score"] > basketball_games["team2"]["score"]:
        basketball_games["result"] = f"{basketball_games['team1']['name']} wins!"
        winning_team = basketball_games["team1"]
    elif basketball_games["team2"]["score"] > basketball_games["team1"]["score"]:
        basketball_games["result"] = f"{basketball_games['team2']['name']} wins!"
        winning_team = basketball_games["team2"]
    else:
        basketball_games["result"] = "It's a draw!"
        winning_team = None

    # Find the top scorer from the winning team
    top_scorer = None
    if winning_team:
        top_scorer = max(winning_team["players"], key=lambda x: x["points"], default=None)
        if top_scorer:
            basketball_games["top_scorer"] = f"Top Scorer: {top_scorer['name']} with {top_scorer['points']} points"
        else:
            basketball_games["top_scorer"] = "No top scorer"
    else:
        basketball_games["top_scorer"] = "No top scorer (draw)"

    return render_template('basketball.html', 
                            team1=basketball_games["team1"], 
                            team2=basketball_games["team2"], 
                            match_ended=basketball_games["match_ended"], 
                            result=basketball_games["result"],
                            top_scorer=basketball_games["top_scorer"])

    # # Redirect back to the main basketball page
    # return redirect(url_for('basketball_index'))

# ----- HOME ROUTE -----

@app.route('/')
def home():
    """
    Root route that displays a simple welcome message and navigation instructions.
    
    Returns:
        String with welcome message and navigation information
    """
    return "Welcome to the Score Hub Use /football for football and /basketball for basketball."

# Run the Flask application in debug mode when executed directly
if __name__ == '__main__':
    app.run(debug=True)