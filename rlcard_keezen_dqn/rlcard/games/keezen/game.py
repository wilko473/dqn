from copy import copy

from rlcard.games.keezen.card import CardState, Suit, CardValue
from rlcard.games.keezen.board import BoardState, FieldType
from rlcard.games.keezen.move import Move, MoveType
from rlcard.games.keezen.player import Player

from colorama import Fore, Style

class Game:
    """A game of Keezen. Has rules, players and a board with marbles. """

    GAME_ACTIONS = 271
    GAME_ACTIONS_SIMPLE = 87
    GAME_STATE_COLUMNS = 97  #123  # 97 # 123  # 123
    GAME_STATE_ROWS = 5
    allow_step_back = False

    def __init__(self, rules, players, board):
        self.rules = rules
        self.players = players
        self.board = board
        self.cards = self.rules.initialize_cards()
        self.card_ops = self.rules.initialize_card_ops(self.cards, board)
        self.game_history = []
        self.legal_moves = {}  # Maps action_index -> move
        # self.temp_rewards = [0, 0, 0, 0]

    def init_game(self):
        """Initializes the game. All marbles at wait fields, cards in stock."""
        self.game_history.clear()
        # self.temp_rewards = [0, 0, 0, 0]
        round_number = 0
        move_number = 0
        stock_cards, player_cards, played_cards = CardState.get_initial_card_state(self.cards, self.players)
        fields_with_marbles = BoardState.get_initial_board_state(self.board.marbles, self.board.waitFields)
        players_play_with_color = {}
        for player in self.players:
            players_play_with_color[player] = player.player_color
        deal_player = self.players[self.rules.player_start]
        move_player = deal_player.get_next_player(self.players)
        self._deal_cards(deal_player, stock_cards, player_cards, round_number)
        game_state = GameState(fields_with_marbles, stock_cards, player_cards, played_cards,
                               players_play_with_color, deal_player, move_player, round_number, move_number)
        if self.allow_step_back:
            self.game_history.append(game_state)
        # game_state_dict = game_state.get_state_for_player(move_player)
        return game_state, self.players.index(move_player)

    # def render(self, game_state):
    #     for player in self.players:
    #         marble_fields = []
    #         player_marbles = self.board.get_marbles_with_color(player.player_color)
    #         for player_marble in player_marbles:
    #             marble_fields.append(BoardState.get_field_for_marble(player_marble, game_state.fields_with_marbles).id_)
    #         player_cards = [card.card_value.name for card in game_state.player_cards[player]]
    #         print("Player " + player.name + ": Marbles: " + str(marble_fields) + ", Cards:" + str(player_cards))

    def render(self, game_state):
        field_idx = [[92, 93, -1, -1, -1, -1, 90, 91, 4, 5, 6, -1, -1, -1, -1, 20, 21],
                     [94, 95, -1, -1, -1, -1, 89, -1, 3, -1, 7, -1, -1, -1, -1, 22, 23],
                     [-1, -1, -1, -1, -1, -1, 88, -1, 2, -1, 8, -1, -1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1, -1, 87, -1, 1, -1, 9, -1, -1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1, -1, 86, -1, 0, -1, 10, -1, -1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1, -1, 85, -1, -1, -1, 11, -1, -1, -1, -1, -1, -1],
                     [78, 79, 80, 81, 82, 83, 84, -1, -1, -1, 12, 13, 14, 15, 16, 17, 18],
                     [77, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 19],
                     [76, 75, 74, 73, 72, -1, -1, -1, -1, -1, -1, -1, 24, 25, 26, 27, 28],
                     [67, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 29],
                     [66, 65, 64, 63, 62, 61, 60, -1, -1, -1, 36, 35, 34, 33, 32, 31, 30],
                     [-1, -1, -1, -1, -1, -1, 59, -1, -1, -1, 37, -1, -1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1, -1, 58, -1, 48, -1, 38, -1, -1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1, -1, 57, -1, 49, -1, 39, -1, -1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1, -1, 56, -1, 50, -1, 40, -1, -1, -1, -1, -1, -1],
                     [68, 69, -1, -1, -1, -1, 55, -1, 51, -1, 41, -1, -1, -1, -1, 44, 45],
                     [70, 71, -1, -1, -1, -1, 54, 53, 52, 43, 42, -1, -1, -1, -1, 46, 47]
                    ]
        player_cards = ["", "", "", ""]
        for player in self.players:
            cards = ""
            for card in game_state.player_cards[player]:
                suit_str = "?"
                if card.suit == Suit.HEARTS:
                    suit_str = "♥"
                elif card.suit == Suit.DIAMONDS:
                    suit_str = "♦"
                elif card.suit == Suit.SPADES:
                    suit_str = "♠"
                elif card.suit == Suit.CLUBS:
                    suit_str = "♣"
                cards = cards + " " + suit_str + str(card.card_value.value)
            player_cards[self.players.index(player)] = cards
        player_cards[self.players.index(game_state.move_player)] = player_cards[self.players.index(game_state.move_player)] + "<->"
        print("Now player " + str(game_state.move_player.player_color[0]) + " wil execute move number: "
              + str(game_state.move_number) + ", round number: " + str(game_state.round_number))
        print("                           " + player_cards[0])
        print("                    ------------------------------------")
        counter = 0
        for field_ids in field_idx:
            if counter == 8:
                row = "{0: <20}|".format(player_cards[3])
            else:
                row = "                    |"
            for field_id in field_ids:
                value = " "
                if field_id > -1:
                    field = self.board.fields[field_id]
                    marble = BoardState.get_marble_for_field_opt(field, game_state.fields_with_marbles)
                    value = field.get_str(marble)
                    if value == "G":
                        value = str(Fore.GREEN + value + Style.RESET_ALL)
                    elif value == "R":
                        value = str(Fore.RED + value + Style.RESET_ALL)
                    elif value == "B":
                        value = str(Fore.BLUE + value + Style.RESET_ALL)
                    elif value == "Y":
                        value = str(Fore.YELLOW + value + Style.RESET_ALL)

                    if value == "N":
                        value = "O"
                row = row + value + " "
            if counter == 8:
                print(row + "|" + player_cards[1])
            else:
                print(row + "|")
            counter = counter + 1
        print("                    ------------------------------------")
        print("                           " + player_cards[2])


    def get_allowed_moves(self, game_state) -> [Move]:
        """Returns the allowed moves. Might generate a DEAL event as well."""
        allowed_moves = []
        player_cards = game_state.player_cards[game_state.move_player]
        filtered_cards = {}
        for card in player_cards:
            if card.card_value not in filtered_cards.values():
                filtered_cards[card] = card.card_value
        for card in filtered_cards.keys():
            # moves_for_card = self._get_moves_for_card(card)  # TODO: Combine card ops to minimize branching
            moves_for_card = []
            card_ops = self.card_ops[card]
            for card_op in card_ops:
                moves = card_op.get_moves(game_state.move_player,
                                          game_state.players_play_with_color[game_state.move_player], card,
                                          game_state.fields_with_marbles)
                moves_for_card.extend(moves)
            allowed_moves.extend(moves_for_card)
        if not allowed_moves:
            if player_cards:
                cards_move = Move(MoveType.THROW_CARDS, game_state.move_player, player_cards, [])
                allowed_moves.append(cards_move)
            elif Game._is_round_over(game_state):
                done, rewards = self.is_over(game_state)
                if not done:
                    allowed_moves.append(Move(MoveType.DEAL, game_state.deal_player, [], []))
        return allowed_moves

    def step(self, move, game_state) -> ():  # GamePosition, reward, done, info: [String: String]):
        rewards = None
        if move:
            if move.move_type == MoveType.DEAL:
                if not Game._is_round_over(game_state):
                    raise ValueError("Cannot deal when round is not finished.")
                game_state.round_number += 1
                if not game_state.stock_cards:
                    CardState.reset(game_state.stock_cards, game_state.player_cards, game_state.played_cards)
                    game_state.deal_player = game_state.deal_player.get_next_player(self.players)
                elif self.rules.rotate_dealer_each_round:
                    game_state.deal_player = game_state.deal_player.get_next_player(self.players)
                self._deal_cards(game_state.deal_player, game_state.stock_cards, game_state.player_cards,
                                 game_state.round_number)
            else:
                # If move is a -4 from own start add a reward
                # if move.move_type == MoveType.RUN and move.cards[0].card_value == CardValue.FOUR:
                #     field = move.marble_moves[0].from_field
                #     marble = move.marble_moves[0].marble
                #     if field.type_ == FieldType.START and field.color_ == marble.color_:
                #         for idx, player in enumerate(self.players):
                #             if player == game_state.move_player:
                #                 self.temp_rewards[idx] = self.temp_rewards[idx] + 1000
                #                 print("4 BACKWARDS! temp_rewards: " + str(self.temp_rewards))

                CardState.play_cards(move.player, move.cards, game_state.player_cards, game_state.played_cards)
                for marble_move in move.marble_moves:
                    _ = BoardState.put_marble_on_field(marble_move.marble, marble_move.to_field,
                                                       game_state.fields_with_marbles)
                    for hit_marble_move in marble_move.hit_marble_moves:
                        _ = BoardState.put_marble_on_field(hit_marble_move.marble, hit_marble_move.to_field,
                                                           game_state.fields_with_marbles)
                if self.rules.switch_color and self.board.is_color_finished(game_state.move_player.player_color, game_state.fields_with_marbles, self.rules):
                    team_mate_color = game_state.move_player.get_team_mate().player_color
                    if (not self.board.is_color_finished(team_mate_color, game_state.fields_with_marbles, self.rules)) and \
                            game_state.move_player.player_color == game_state.move_player_plays_with_color():
                        # Switch color
                        game_state.players_play_with_color[game_state.move_player] = team_mate_color
                game_state.move_number += 1
        done, end_rewards = self.is_over(game_state)

        rewards = [0, 0, 0, 0]  # self.temp_rewards
        if done:
            rewards = end_rewards
            # Combine temporary rewards with end rewards
            # for idx, end_reward in enumerate(end_rewards):
            #     rewards[idx] = rewards[idx] + end_reward
        # else:  # Changed: change move_player when not finished
        if move and move.move_type == MoveType.DEAL:
            game_state.move_player = game_state.deal_player.get_next_player(self.players)
        else:
            game_state.move_player = game_state.move_player.get_next_player(self.players)

        copy_game_state = copy(game_state)
        if self.allow_step_back:
            copy_game_state.last_move = move
            self.game_history.append(copy_game_state)

        return copy_game_state, rewards, done

    @staticmethod
    def _is_round_over(game_state) -> bool:
        """Returns if the current round is over. All players have played their cards."""
        all_players_card_count = sum([len(element) for element in game_state.player_cards.values()])
        return all_players_card_count == 0

    def is_over(self, game_state):
        """Returns if the game is over. All marbles of a team are at the home fields.
        If the game is finished then the rewards for each player are returned."""


        # if move.move_type == MoveType.RUN and move.cards[0].card_value == CardValue.FOUR:
        #     field = move.marble_moves[0].from_field
        #     marble = move.marble_moves[0].marble
        #     if field.type_ == FieldType.START and field.color_ == marble.color_:
        #         for idx, player in enumerate(self.players):
        #             if player == game_state.move_player:
        #                 self.temp_rewards[idx] = self.temp_rewards[idx] + 1000
        #                 print("4 BACKWARDS! temp_rewards: " + str(self.temp_rewards))

        player_finished = self.board.is_color_finished(game_state.players_play_with_color[game_state.move_player],
                                                       game_state.fields_with_marbles, self.rules)
        if player_finished:
            if self.rules.switch_color:
                team_mate_color = game_state.players_play_with_color[game_state.move_player.get_team_mate()]
                team_mate_finished = self.board.is_color_finished(team_mate_color, game_state.fields_with_marbles, self.rules)
                if team_mate_finished:
                    rewards = []
                    for i in range(len(self.players)):
                        # for player in self.players:
                        player = self.players[i]
                        if player == game_state.move_player or player == game_state.move_player.get_team_mate():
                            reward_value = 1  # + self.temp_rewards[i]
                            #reward_value = max(1, 500 - game_state.move_number)
                            rewards.append(reward_value)
                        else:
                            reward_value = 0  # + self.temp_rewards[i]
                            # reward_value = min(-1, -500 + game_state.move_number)
                            rewards.append(reward_value)
                    #print("FINISHED. " + str(rewards))

                    return True, rewards
            else:
                rewards = []
                #for player in self.players:
                for i in range(len(self.players)):
                    player = self.players[i]
                    if player == game_state.move_player:
                        reward = 1  # + self.temp_rewards[i]
                        rewards.append(reward)
                    else:
                        reward = 0  # + self.temp_rewards[i]
                        rewards.append(reward)
                # print("FINISHED. " + str(rewards))
                return True, rewards
        return False, None

    def step_back(self):
        """Returns and removes the last game_state from game history."""
        if self.game_history:
            prev_game_state = self.game_history.pop()
            return prev_game_state
        return None

    def _deal_cards(self, deal_player, stock_cards, player_cards, round_number):
        """Deals the cards for a new round."""
        number_of_cards = self.rules.cards_per_round[round_number % len(self.rules.cards_per_round)]
        player = deal_player.get_next_player(self.players)
        for _ in range(number_of_cards):
            for _ in range(len(self.players)):
                _ = CardState.deal_card(player, stock_cards, player_cards)
                player = player.get_next_player(self.players)


class GameState:
    """A GameState holds the state of a game. This means the marble positions, player cards, move player, the colors
        players play with, deal player, round and move numbers."""

    def __init__(self, fields_with_marbles, stock_cards, player_cards, played_cards, players_play_with_color,
                 deal_player, move_player, round_number, move_number):
        self.fields_with_marbles = dict(fields_with_marbles)
        self.stock_cards = list(stock_cards)
        self.played_cards = list(played_cards)
        self.player_cards = dict(player_cards)
        self.players_play_with_color = dict(players_play_with_color)
        self.deal_player = deal_player
        self.move_player = move_player
        self.round_number = round_number
        self.move_number = move_number
        self.last_move = None

    def __copy__(self):
        new_one = type(self)(self.fields_with_marbles, self.stock_cards, self.player_cards, self.played_cards,
                             self.players_play_with_color, self.deal_player, self.move_player, self.round_number,
                             self.move_number)
        return new_one

    def move_player_plays_with_color(self):
        return self.players_play_with_color[self.move_player]

    def get_state_for_player(self, player: Player):
        state = dict()
        state['state_for_player'] = player
        state['fields_with_marbles'] = dict(self.fields_with_marbles)
        state['stock_count'] = len(self.stock_cards)
        state['played_cards'] = list(self.played_cards)
        state['player_cards'] = list(self.player_cards[player])
        player_card_count = {}
        for player in self.player_cards.keys():
            player_card_count[player] = len(self.player_cards[player])
        state['player_card_count'] = player_card_count
        state['players_play_with_color'] = dict(self.players_play_with_color)
        state['deal_player'] = self.deal_player
        state['move_player'] = self.move_player
        state['round_number'] = self.round_number
        state['move_number'] = self.move_number
        return state


class GameActions:
    # 'NO', 'SP07P23P3', 'SP07P33P1','SP07P04T0', ADDED 16x SW11Pxxx for R and Y
    ALL_ACTIONS_271 = ['NO', 'DL', 'RU01P0', 'RU01P1', 'RU01P2', 'RU01P3', 'RU02P0', 'RU02P1', 'RU02P2', 'RU02P3', 'RU03P0',
                       'RU03P1', 'RU03P2', 'RU03P3', 'RU04P0', 'RU04P1', 'RU04P2', 'RU04P3', 'RU05P0', 'RU05P1',
                       'RU05P2', 'RU05P3', 'RU06P0', 'RU06P1', 'RU06P2', 'RU06P3',  # 'RU07P0', 'RU07P1', 'RU07P2',
                       # 'RU07P3', # erbij
                       'RU08P0', 'RU08P1', 'RU08P2',
                       'RU08P3', 'RU09P0', 'RU09P1', 'RU09P2', 'RU09P3', 'RU10P0', 'RU10P1', 'RU10P2', 'RU10P3',
                       'RU12P0', 'RU12P1', 'RU12P2', 'RU12P3', 'SP07P0', 'SP07P01P1', 'SP07P01P2', 'SP07P01P3',
                       'SP07P01T0', 'SP07P01T1', 'SP07P01T2', 'SP07P01T3', 'SP07P02P1', 'SP07P02P2', 'SP07P02P3',
                       'SP07P02T0', 'SP07P02T1', 'SP07P02T2', 'SP07P02T3', 'SP07P03P1', 'SP07P03P2', 'SP07P03P3',
                       'SP07P03T0', 'SP07P03T1', 'SP07P03T2', 'SP07P03T3', 'SP07P04P1', 'SP07P04P2', 'SP07P04P3',
                       'SP07P04T1', 'SP07P04T2', 'SP07P04T3', 'SP07P05P1', 'SP07P05P2', 'SP07P05P3', 'SP07P05T0', 'SP07P04T0',
                       'SP07P05T1', 'SP07P05T2', 'SP07P05T3', 'SP07P06P1', 'SP07P06P2', 'SP07P06P3', 'SP07P06T0',
                       'SP07P06T1', 'SP07P06T2', 'SP07P06T3', 'SP07P1', 'SP07P11P0', 'SP07P11P2', 'SP07P11P3',
                       'SP07P11T0', 'SP07P11T1', 'SP07P11T2', 'SP07P11T3', 'SP07P12P0', 'SP07P12P2', 'SP07P12P3',
                       'SP07P12T0', 'SP07P12T1', 'SP07P12T2', 'SP07P12T3', 'SP07P13P0', 'SP07P13P2', 'SP07P13P3',
                       'SP07P13T0', 'SP07P13T1', 'SP07P13T2', 'SP07P13T3', 'SP07P14P0', 'SP07P14P2', 'SP07P14P3',
                       'SP07P14T0', 'SP07P14T1', 'SP07P14T2', 'SP07P14T3', 'SP07P15P0', 'SP07P15P2', 'SP07P15P3',
                       'SP07P15T0', 'SP07P15T1', 'SP07P15T2', 'SP07P15T3', 'SP07P16P0', 'SP07P16P2', 'SP07P16P3',
                       'SP07P16T0', 'SP07P16T1', 'SP07P16T2', 'SP07P16T3', 'SP07P2', 'SP07P21P0', 'SP07P21P1',
                       'SP07P21P3', 'SP07P21T0', 'SP07P21T1', 'SP07P21T2', 'SP07P21T3', 'SP07P22P0', 'SP07P22P1',
                       'SP07P22P3', 'SP07P22T0', 'SP07P22T1', 'SP07P22T2', 'SP07P22T3', 'SP07P23P0', 'SP07P23P1', 'SP07P23P3',
                       'SP07P23T0', 'SP07P23T1', 'SP07P23T2', 'SP07P23T3', 'SP07P24P0', 'SP07P24P1', 'SP07P24P3',
                       'SP07P24T0', 'SP07P24T1', 'SP07P24T2', 'SP07P24T3', 'SP07P25P0', 'SP07P25P1', 'SP07P25P3',
                       'SP07P25T0', 'SP07P25T1', 'SP07P25T2', 'SP07P25T3', 'SP07P26P0', 'SP07P26P1', 'SP07P26P3',
                       'SP07P26T0', 'SP07P26T1', 'SP07P26T2', 'SP07P26T3', 'SP07P3', 'SP07P31P0', 'SP07P31P1',
                       'SP07P31P2', 'SP07P31T0', 'SP07P31T1', 'SP07P31T2', 'SP07P31T3', 'SP07P32P0', 'SP07P32P1',
                       'SP07P32P2', 'SP07P32T0', 'SP07P32T1', 'SP07P32T2', 'SP07P32T3', 'SP07P33P0', 'SP07P33P2', 'SP07P33P1',
                       'SP07P33T0', 'SP07P33T1', 'SP07P33T2', 'SP07P33T3', 'SP07P34P0', 'SP07P34P1', 'SP07P34P2',
                       'SP07P34T0', 'SP07P34T1', 'SP07P34T2', 'SP07P34T3', 'SP07P35P0', 'SP07P35P1', 'SP07P35P2',
                       'SP07P35T0', 'SP07P35T1', 'SP07P35T2', 'SP07P35T3', 'SP07P36P0', 'SP07P36P1', 'SP07P36P2',
                       'SP07P36T0', 'SP07P36T1', 'SP07P36T2', 'SP07P36T3', 'ST01P0', 'ST01P1', 'ST01P2', 'ST01P3',
                       'ST13P0', 'ST13P1', 'ST13P2', 'ST13P3', 'SW11P0A0', 'SW11P0B0', 'SW11P0A1', 'SW11P0B1',
                       'SW11P0A2', 'SW11P0B2', 'SW11P0A3', 'SW11P0B3',
                       'SW11P0T0', 'SW11P0T1', 'SW11P0T2', 'SW11P0T3', 'SW11P1A0', 'SW11P1B0', 'SW11P1A1', 'SW11P1B1',
                       'SW11P1A2', 'SW11P1B2', 'SW11P1A3', 'SW11P1B3',
                       'SW11P1T0', 'SW11P1T1', 'SW11P1T2', 'SW11P1T3', 'SW11P2A0', 'SW11P2B0', 'SW11P2A1', 'SW11P2B1',
                       'SW11P2A2', 'SW11P2B2', 'SW11P2A3', 'SW11P2B3',
                       'SW11P2T0', 'SW11P2T1', 'SW11P2T2', 'SW11P2T3', 'SW11P3A0', 'SW11P3B0', 'SW11P3A1', 'SW11P3B1',
                       'SW11P3A2', 'SW11P3B2', 'SW11P3A3', 'SW11P3B3',
                       'SW11P3T0', 'SW11P3T1', 'SW11P3T2', 'SW11P3T3', 'TC']

    ALL_ACTIONS_25 = ['NO', 'DL', 'RU01', 'RU02', 'RU03', 'RU04', 'RU05', 'RU06', 'RU08', 'RU09', 'RU10', 'RU12',
                      'SP07P0P7', 'SP07P1P6', 'SP07P2P5', 'SP07P3P4', 'SP07P4P3', 'SP07P5P2', 'SP07P6P1', 'SP07P7P0',
                      'ST01', 'ST13', 'SW11PO', 'SW11PT', 'TC']

    # Game actions with 7 RUN: 87
    ALL_ACTIONS_SIMPLE = ['NO', 'DL', 'RU01P0', 'RU01P1', 'RU01P2', 'RU01P3', 'RU02P0', 'RU02P1', 'RU02P2', 'RU02P3', 'RU03P0',
                       'RU03P1', 'RU03P2', 'RU03P3', 'RU04P0', 'RU04P1', 'RU04P2', 'RU04P3', 'RU05P0', 'RU05P1',
                       'RU05P2', 'RU05P3', 'RU06P0', 'RU06P1', 'RU06P2', 'RU06P3',  'RU07P0', 'RU07P1', 'RU07P2',
                       'RU07P3',  # RUN 7 Added
                       'RU08P0', 'RU08P1', 'RU08P2',
                       'RU08P3', 'RU09P0', 'RU09P1', 'RU09P2', 'RU09P3', 'RU10P0', 'RU10P1', 'RU10P2', 'RU10P3',
                       'RU12P0', 'RU12P1', 'RU12P2', 'RU12P3',
                       # All SPLIT actions disabled
                       # 'SP07P0', 'SP07P01P1', 'SP07P01P2', 'SP07P01P3',
                       # 'SP07P01T0', 'SP07P01T1', 'SP07P01T2', 'SP07P01T3', 'SP07P02P1', 'SP07P02P2', 'SP07P02P3',
                       # 'SP07P02T0', 'SP07P02T1', 'SP07P02T2', 'SP07P02T3', 'SP07P03P1', 'SP07P03P2', 'SP07P03P3',
                       # 'SP07P03T0', 'SP07P03T1', 'SP07P03T2', 'SP07P03T3', 'SP07P04P1', 'SP07P04P2', 'SP07P04P3',
                       # 'SP07P04T1', 'SP07P04T2', 'SP07P04T3', 'SP07P05P1', 'SP07P05P2', 'SP07P05P3', 'SP07P05T0', 'SP07P04T0',
                       # 'SP07P05T1', 'SP07P05T2', 'SP07P05T3', 'SP07P06P1', 'SP07P06P2', 'SP07P06P3', 'SP07P06T0',
                       # 'SP07P06T1', 'SP07P06T2', 'SP07P06T3', 'SP07P1', 'SP07P11P0', 'SP07P11P2', 'SP07P11P3',
                       # 'SP07P11T0', 'SP07P11T1', 'SP07P11T2', 'SP07P11T3', 'SP07P12P0', 'SP07P12P2', 'SP07P12P3',
                       # 'SP07P12T0', 'SP07P12T1', 'SP07P12T2', 'SP07P12T3', 'SP07P13P0', 'SP07P13P2', 'SP07P13P3',
                       # 'SP07P13T0', 'SP07P13T1', 'SP07P13T2', 'SP07P13T3', 'SP07P14P0', 'SP07P14P2', 'SP07P14P3',
                       # 'SP07P14T0', 'SP07P14T1', 'SP07P14T2', 'SP07P14T3', 'SP07P15P0', 'SP07P15P2', 'SP07P15P3',
                       # 'SP07P15T0', 'SP07P15T1', 'SP07P15T2', 'SP07P15T3', 'SP07P16P0', 'SP07P16P2', 'SP07P16P3',
                       # 'SP07P16T0', 'SP07P16T1', 'SP07P16T2', 'SP07P16T3', 'SP07P2', 'SP07P21P0', 'SP07P21P1',
                       # 'SP07P21P3', 'SP07P21T0', 'SP07P21T1', 'SP07P21T2', 'SP07P21T3', 'SP07P22P0', 'SP07P22P1',
                       # 'SP07P22P3', 'SP07P22T0', 'SP07P22T1', 'SP07P22T2', 'SP07P22T3', 'SP07P23P0', 'SP07P23P1', 'SP07P23P3',
                       # 'SP07P23T0', 'SP07P23T1', 'SP07P23T2', 'SP07P23T3', 'SP07P24P0', 'SP07P24P1', 'SP07P24P3',
                       # 'SP07P24T0', 'SP07P24T1', 'SP07P24T2', 'SP07P24T3', 'SP07P25P0', 'SP07P25P1', 'SP07P25P3',
                       # 'SP07P25T0', 'SP07P25T1', 'SP07P25T2', 'SP07P25T3', 'SP07P26P0', 'SP07P26P1', 'SP07P26P3',
                       # 'SP07P26T0', 'SP07P26T1', 'SP07P26T2', 'SP07P26T3', 'SP07P3', 'SP07P31P0', 'SP07P31P1',
                       # 'SP07P31P2', 'SP07P31T0', 'SP07P31T1', 'SP07P31T2', 'SP07P31T3', 'SP07P32P0', 'SP07P32P1',
                       # 'SP07P32P2', 'SP07P32T0', 'SP07P32T1', 'SP07P32T2', 'SP07P32T3', 'SP07P33P0', 'SP07P33P2', 'SP07P33P1',
                       # 'SP07P33T0', 'SP07P33T1', 'SP07P33T2', 'SP07P33T3', 'SP07P34P0', 'SP07P34P1', 'SP07P34P2',
                       # 'SP07P34T0', 'SP07P34T1', 'SP07P34T2', 'SP07P34T3', 'SP07P35P0', 'SP07P35P1', 'SP07P35P2',
                       # 'SP07P35T0', 'SP07P35T1', 'SP07P35T2', 'SP07P35T3', 'SP07P36P0', 'SP07P36P1', 'SP07P36P2',
                       # 'SP07P36T0', 'SP07P36T1', 'SP07P36T2', 'SP07P36T3',
                       'ST01P0', 'ST01P1', 'ST01P2', 'ST01P3',
                       'ST13P0', 'ST13P1', 'ST13P2', 'ST13P3', 'SW11P0O0', 'SW11P0O1', 'SW11P0O2', 'SW11P0O3',
                       'SW11P0T0', 'SW11P0T1', 'SW11P0T2', 'SW11P0T3', 'SW11P1O0', 'SW11P1O1', 'SW11P1O2', 'SW11P1O3',
                       'SW11P1T0', 'SW11P1T1', 'SW11P1T2', 'SW11P1T3', 'SW11P2O0', 'SW11P2O1', 'SW11P2O2', 'SW11P2O3',
                       'SW11P2T0', 'SW11P2T1', 'SW11P2T2', 'SW11P2T3', 'SW11P3O0', 'SW11P3O1', 'SW11P3O2', 'SW11P3O3',
                       'SW11P3T0', 'SW11P3T1', 'SW11P3T2', 'SW11P3T3', 'TC']

    # COPY OF ALL ACTIONS, WITH SWITCH BUG: SW11P0O0, not SW11P0Y0 and SW11P0R0
    # ALL_ACTIONS_ORG= ['NO', 'DL', 'RU01P0', 'RU01P1', 'RU01P2', 'RU01P3', 'RU02P0', 'RU02P1', 'RU02P2', 'RU02P3',
    #                    'RU03P0',
    #                    'RU03P1', 'RU03P2', 'RU03P3', 'RU04P0', 'RU04P1', 'RU04P2', 'RU04P3', 'RU05P0', 'RU05P1',
    #                    'RU05P2', 'RU05P3', 'RU06P0', 'RU06P1', 'RU06P2', 'RU06P3',  # 'RU07P0', 'RU07P1', 'RU07P2',
    #                    # 'RU07P3', # erbij
    #                    'RU08P0', 'RU08P1', 'RU08P2',
    #                    'RU08P3', 'RU09P0', 'RU09P1', 'RU09P2', 'RU09P3', 'RU10P0', 'RU10P1', 'RU10P2', 'RU10P3',
    #                    'RU12P0', 'RU12P1', 'RU12P2', 'RU12P3', 'SP07P0', 'SP07P01P1', 'SP07P01P2', 'SP07P01P3',
    #                    'SP07P01T0', 'SP07P01T1', 'SP07P01T2', 'SP07P01T3', 'SP07P02P1', 'SP07P02P2', 'SP07P02P3',
    #                    'SP07P02T0', 'SP07P02T1', 'SP07P02T2', 'SP07P02T3', 'SP07P03P1', 'SP07P03P2', 'SP07P03P3',
    #                    'SP07P03T0', 'SP07P03T1', 'SP07P03T2', 'SP07P03T3', 'SP07P04P1', 'SP07P04P2', 'SP07P04P3',
    #                    'SP07P04T1', 'SP07P04T2', 'SP07P04T3', 'SP07P05P1', 'SP07P05P2', 'SP07P05P3', 'SP07P05T0',
    #                    'SP07P04T0',
    #                    'SP07P05T1', 'SP07P05T2', 'SP07P05T3', 'SP07P06P1', 'SP07P06P2', 'SP07P06P3', 'SP07P06T0',
    #                    'SP07P06T1', 'SP07P06T2', 'SP07P06T3', 'SP07P1', 'SP07P11P0', 'SP07P11P2', 'SP07P11P3',
    #                    'SP07P11T0', 'SP07P11T1', 'SP07P11T2', 'SP07P11T3', 'SP07P12P0', 'SP07P12P2', 'SP07P12P3',
    #                    'SP07P12T0', 'SP07P12T1', 'SP07P12T2', 'SP07P12T3', 'SP07P13P0', 'SP07P13P2', 'SP07P13P3',
    #                    'SP07P13T0', 'SP07P13T1', 'SP07P13T2', 'SP07P13T3', 'SP07P14P0', 'SP07P14P2', 'SP07P14P3',
    #                    'SP07P14T0', 'SP07P14T1', 'SP07P14T2', 'SP07P14T3', 'SP07P15P0', 'SP07P15P2', 'SP07P15P3',
    #                    'SP07P15T0', 'SP07P15T1', 'SP07P15T2', 'SP07P15T3', 'SP07P16P0', 'SP07P16P2', 'SP07P16P3',
    #                    'SP07P16T0', 'SP07P16T1', 'SP07P16T2', 'SP07P16T3', 'SP07P2', 'SP07P21P0', 'SP07P21P1',
    #                    'SP07P21P3', 'SP07P21T0', 'SP07P21T1', 'SP07P21T2', 'SP07P21T3', 'SP07P22P0', 'SP07P22P1',
    #                    'SP07P22P3', 'SP07P22T0', 'SP07P22T1', 'SP07P22T2', 'SP07P22T3', 'SP07P23P0', 'SP07P23P1',
    #                    'SP07P23P3',
    #                    'SP07P23T0', 'SP07P23T1', 'SP07P23T2', 'SP07P23T3', 'SP07P24P0', 'SP07P24P1', 'SP07P24P3',
    #                    'SP07P24T0', 'SP07P24T1', 'SP07P24T2', 'SP07P24T3', 'SP07P25P0', 'SP07P25P1', 'SP07P25P3',
    #                    'SP07P25T0', 'SP07P25T1', 'SP07P25T2', 'SP07P25T3', 'SP07P26P0', 'SP07P26P1', 'SP07P26P3',
    #                    'SP07P26T0', 'SP07P26T1', 'SP07P26T2', 'SP07P26T3', 'SP07P3', 'SP07P31P0', 'SP07P31P1',
    #                    'SP07P31P2', 'SP07P31T0', 'SP07P31T1', 'SP07P31T2', 'SP07P31T3', 'SP07P32P0', 'SP07P32P1',
    #                    'SP07P32P2', 'SP07P32T0', 'SP07P32T1', 'SP07P32T2', 'SP07P32T3', 'SP07P33P0', 'SP07P33P2',
    #                    'SP07P33P1',
    #                    'SP07P33T0', 'SP07P33T1', 'SP07P33T2', 'SP07P33T3', 'SP07P34P0', 'SP07P34P1', 'SP07P34P2',
    #                    'SP07P34T0', 'SP07P34T1', 'SP07P34T2', 'SP07P34T3', 'SP07P35P0', 'SP07P35P1', 'SP07P35P2',
    #                    'SP07P35T0', 'SP07P35T1', 'SP07P35T2', 'SP07P35T3', 'SP07P36P0', 'SP07P36P1', 'SP07P36P2',
    #                    'SP07P36T0', 'SP07P36T1', 'SP07P36T2', 'SP07P36T3', 'ST01P0', 'ST01P1', 'ST01P2', 'ST01P3',
    #                    'ST13P0', 'ST13P1', 'ST13P2', 'ST13P3', 'SW11P0O0', 'SW11P0O1', 'SW11P0O2', 'SW11P0O3',
    #                    'SW11P0T0', 'SW11P0T1', 'SW11P0T2', 'SW11P0T3', 'SW11P1O0', 'SW11P1O1', 'SW11P1O2', 'SW11P1O3',
    #                    'SW11P1T0', 'SW11P1T1', 'SW11P1T2', 'SW11P1T3', 'SW11P2O0', 'SW11P2O1', 'SW11P2O2', 'SW11P2O3',
    #                    'SW11P2T0', 'SW11P2T1', 'SW11P2T2', 'SW11P2T3', 'SW11P3O0', 'SW11P3O1', 'SW11P3O2', 'SW11P3O3',
    #                    'SW11P3T0', 'SW11P3T1', 'SW11P3T2', 'SW11P3T3', 'TC']
