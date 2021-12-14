from rlcard.games.mejn.board import FieldColor, Board
from rlcard.games.mejn.game import Game
from rlcard.games.mejn.player import Player, PlayerLocation


class Env:
    """The environment to play the game."""

    def __init__(self):
        player_north = Player("Green", FieldColor.GREEN, PlayerLocation.NORTH)
        player_east = Player("Red", FieldColor.RED, PlayerLocation.EAST)
        player_south = Player("Blue", FieldColor.BLUE, PlayerLocation.SOUTH)
        player_west = Player("Yellow", FieldColor.YELLOW, PlayerLocation.WEST)
        self.players = [player_north, player_east, player_south, player_west]
        self.game = Game(self.players, Board(self.players))
        self.game_state = None

    def reset(self):
        self.game_state = self.game.init_game()
        return self.game_state

    def get_allowed_moves(self, dice):
        return self.game.get_allowed_moves(self.game_state, dice)

    def step(self, move):
        self.game_state, rewards, done = self.game.step(move, self.game_state)
        return self.game_state, rewards, done

    def observation(self, player):
        if player is None:
            return self.game_state
        return self.game_state.get_state_for_player(player)

    def is_done(self):
        return self.game.is_over(self.game_state)

    def render(self):
        self.game.render(self.game_state)
