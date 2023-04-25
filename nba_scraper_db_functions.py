def create_game_info(url, season, season_gamecount):
    '''
    Create game metadata.
    ---
    Inputs:
    
    url: game url containing the date the game was played
    season: integer value in the pattern 'YY-YY' representing the NBA season the game occured.
    season_gamecount: a value used to update the unique game id for every game in a season.
    ---
    Outputs:
    
    A list containing the unique game_id, season, and date of the game.
    '''
    
    season_gamecount += 1
    game_count = str(season_gamecount)
    
    # ensure that game_count is always 4 characters long
    while len(game_count) < 4:
        game_count = '0' + game_count
    
    # create date variables from the url
    id_string = url.strip(string.ascii_letters+string.punctuation)
    year = id_string[0:4]
    month = id_string[4:6]
    day = id_string[6:8]
    
    # recombine date variables
    date = year+'-'+month+'-'+day
    
    # create unique game_id 
    game_id = int(season+month+day+game_count)
    # WHY DO I NEED THE SEASON VARIABLE TO BE DECLARED AT ALL???
    season = int(season)
    
    return [game_id, season, date]

def create_team_info(table):
    '''
    Create a dataframe with game results. Uses an html table as input.
    ---
    Inputs:
    
    table: a BeautifulSoup html table
    ---
    Outputs:
    
    team_info: a dataframe with the relevant game information (team_ids, scores, and boolean 'results' column)
    '''
    
    # get team_ids
    id_rows = table.findAll('th', attrs={'class':'center', 'data-stat':'team', 'scope':'row'})
    team_ids = [row.text.strip() for row in id_rows]
    
    # get final score
    scores = table.findAll('td', attrs={'class': 'center', 'data-stat': 'T'})
    final_scores = [int(score.text.strip()) for score in scores]
    
    # boolean game-winner: away=0, home=1
    if final_scores[0] > final_scores[1]:
        result=0
    else:
        result=1
    
    team_info = [team_ids[0], final_scores[0], team_ids[1], final_scores[1], result]
    
    return team_info

def create_info_df(game_info, team_info):
    '''
    Combine the data from create_game_info() and create_team_info into a dataframe
    ---
    Inputs:

    game_info: output from the create_game_info() function
    team_info: output from the create_team_info() function
    ---
    Output:

    A dataframe containing all relevant metadata and results from an NBA game.
    '''
    info = game_info + team_info
    info_df = pd.DataFrame([info], columns=info_columns)
    return info_df

def create_boxscores(table, game_id):
    '''
    Create a player and team boxscore from an html table
    ---
    Input:

    table: an html table from BeautifulSoup containing boxscore data for an NBA game
    game_id: a unique integer id representing the specific NBA game
    ---
    Output:

    player_box_df: a dataframe of player boxscore data
    team_box_df: a dataframe of team boxscore data
    '''

    # ignore first 'tr', it is table title, not column
    rows = table.findAll('tr')[1:]
    # first 'th' is 'Starters', but will be changed into the player names
    headers = rows[0].findAll('th')
    # provide column names
    headerlist = [h.text.strip() for h in headers]
    
    # ignore first row (headers)
    data = rows[1:]
    # get names column
    player_names = [row.find('th').text.strip() for row in rows]
    # get player stats
    player_stats = [[stat.text.strip() for stat in row.findAll('td')] for row in data]
    # add player name as first entry in each row
    for i in range(len(player_stats)):
        # ignore header with i+1
        player_stats[i].insert(0, player_names[i+1])
    
    # create player stats dataframe
    player_box_df = pd.DataFrame(player_stats, columns=headerlist)
    # drop 'Reserves' row
    player_box_df.drop(player_box_df[player_box_df['Starters'] == 'Reserves'].index, inplace=True)
    
    # add game id column
    player_box_df.insert(loc=0, column='game_id', value=game_id)
    
    # create team stats dataframe from last row in player stats
    team_box_df = pd.DataFrame(player_box_df.iloc[-1]).T
    
    #drop team totals from player stats df
    player_box_df = player_box_df[:-1].rename(columns={'Starters': 'player'})

    return player_box_df, team_box_df