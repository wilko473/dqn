class PlayerLocation:
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


class Player:
    """Player of the game."""
    def __init__(self, name, player_color, location):
        self.name = name
        self.player_color = player_color
        self.team = None
        self.location = location
        self.is_local_human = False

    def get_next_player(self, players_):
        """Returns the next player."""
        index_of_player = players_.index(self)
        index_of_next_player = (index_of_player + 1) % len(players_)
        next_player = players_[index_of_next_player]
        return next_player

    def get_prev_player(self, players_):
        """Returns the previous player."""
        index_of_player = players_.index(self)
        index_of_prev_player = (index_of_player - 1) % len(players_)
        return players_[index_of_prev_player]

    def get_team_mate(self):
        for team_player in self.team.players:
            if team_player != self:
                return team_player
        return None

    def __str__(self):
        return "Player[{0}]: {1} {2}.".format(self.name, self.location, self.player_color)


class Team:
    """Team of two players."""
    def __init__(self, name, players):
        self.name = name
        self.players = players
        for player in self.players:
            player.team = self

    def __str__(self):
        return "Team {0}".format(self.name)
