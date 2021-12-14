import numpy as np
from enum import Enum
from random import shuffle
from rlcard.games.keezen.player import Player


class Card:
    """Card type. Has an id, suit and card value."""

    def __init__(self, suit, card_value, id_):
        self.suit = suit
        self.card_value = card_value
        self.id_ = id_

    def __str__(self):
        return "Card[{0}]: {1} {2}".format(self.id_, self.suit, self. card_value)

class CardState:
    """Helps to manage the positions of all cards."""

    @staticmethod
    def get_initial_card_state(cards: [Card], players):
        stock_cards: [Card] = cards.copy()
        player_cards: {Player: [Card]} = {}
        for player in players:
            player_cards[player] = []
        played_cards: [Card] = []
        shuffle(stock_cards)
        return stock_cards, player_cards, played_cards

    @staticmethod
    def reset(stock_cards, player_cards, played_cards):
        """Resets the stock and shuffles."""
        stock_cards.extend(played_cards)
        played_cards.clear()
        for player in player_cards.keys():
            cards = player_cards[player]
            stock_cards.extend(cards)
            player_cards[player] = []
        shuffle(stock_cards)

    @staticmethod
    def deal_card(player, stock_cards, player_cards) -> Card:
        """Deal a card to a player."""
        card: Card = stock_cards.pop()
        player_cards[player].append(card)
        return card

    @staticmethod
    def play_cards(player, cards, player_cards, played_cards):
        """Play multiple cards (throw all)."""
        played_cards.extend(cards)
        if len(cards) == 1:
            player_cards[player].remove(cards[0])
        else:
            player_cards[player].clear()

    # OLD: bytearray 96 implementation
    # @staticmethod
    # def get_card_state_as_array(cur_player, players, cards, stock_cards, player_cards, played_cards):
    #     """Array with card positions. 0 is unknown, 1 is current player, 2 is played. Counts are added too."""
    #     card_array = bytearray(96)
    #     for idx, card in enumerate(cards):
    #         if card in player_cards[cur_player]:
    #             card_array[idx] = 1
    #         elif card in played_cards:
    #             card_array[idx] = 2
    #     # Card counts for players
    #     for idx, player in enumerate(players, start=52):
    #         card_array[idx] = len(player_cards[player])
    #     # Card count for stock
    #     card_array[56] = len(played_cards)
    #     card_array[57] = len(stock_cards)
    #     return card_array

    @staticmethod
    def get_card_state_as_matrix(cards: [Card]):
        """Returns the cards in a 5x13 matrix."""
        indices = [0]*13
        for card in cards:
            card_index = card.card_value.value - 1
            indices[card_index] = indices[card_index] + 1
        card_state = np.zeros((5, 13), dtype=int)
        for i, index in enumerate(indices):
            if index == 1:
                card_state[index][i] = 1
        return card_state


class Suit(Enum):
    DIAMONDS = 0
    HEARTS = 1
    CLUBS = 2
    SPADES = 3


class CardValue(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

# class CardLocation(Enum):
#     """Enum to define all possible card locations."""
#     NONE = int(0b00000000)  # Invalid
#     P_NORTH = int(0b00000001)
#     P_EAST = int(0b00000010)
#     P_SOUTH = int(0b00000100)
#     P_WEST = int(0b00001000)
#     S_PLAYED = int(0b00010000)
#     S_STOCK = int(0b00100000)

# class CardState:
#     """State of the playing cards."""
#     cardPositions = []  # [UInt8]()
#     cardsForPlayer = {Player: [Card]}
#
#     #  Behind the cards in the array: card count for players, stock, played cards
#     def init(self, stock: Stock, players):
#         for card in stock.initial_cards:
#             self.cardPositions.append(self.get_card_location_value(card, stock, players))
#
#     def get_card_location_value(self, card: Card, stock: Stock, players) -> CardLocation:
#         if card in stock.stock_cards:
#             return CardLocation.S_STOCK
#         elif card in stock.played_cards:
#             return CardLocation.S_PLAYED
#         else:
#             for player in players:
#                 if player.cards.contains(card):
#                     if player.location == PlayerLocation.NORTH:
#                         return CardLocation.P_NORTH
#                     elif player.location == PlayerLocation.EAST:
#                         return CardLocation.P_EAST
#                     elif player.location == PlayerLocation.SOUTH:
#                         return CardLocation.P_SOUTH
#                     elif player.location == PlayerLocation.WEST:
#                         return CardLocation.P_WEST
#         return CardLocation.NONE
