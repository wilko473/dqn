from rlcard.games.keezen.card import CardValue, Suit, Card
from rlcard.games.keezen.cardop import CardOpRun, CardOpStart, CardOpSwitchOneOwnMarble, CardOpSplitTwoMarbles


class Rules:
    rotate_dealer_each_round = True
    player_start = 1  # This is the index of the first deal player
    cards_per_round = [5, 4, 4]  # Number of cards each player gets per round. After these rounds the stock is reset.

    def __init__(self, game_type="Keez"):
        self.game_type = game_type
        self.switch_color = True
        self.finish_marble_nrs = 4
        if self.game_type == "KeezSimple":
            self.switch_color = False
            self.finish_marble_nrs = 2

    def initialize_cards(self) -> []:
        """Initializes the cards."""
        cards = []
        if self.game_type == "Keez" or self.game_type == "KeezSimple":
            card_values = [CardValue.ACE, CardValue.KING, CardValue.QUEEN, CardValue.JACK, CardValue.TEN,
                           CardValue.NINE,
                           CardValue.EIGHT, CardValue.SEVEN, CardValue.SIX, CardValue.FIVE, CardValue.FOUR,
                           CardValue.THREE, CardValue.TWO]
            card_id = 0
            for suit in [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]:
                for card_value in card_values:
                    card = Card(suit, card_value, card_id)
                    cards.append(card)
                    card_id += 1

        return cards

    def initialize_card_ops(self, cards, board) -> {}:  # [Card: [CardOp]]:
        """Initializes the card operations."""
        card_ops = {}
        if self.game_type == "Keez":
            for card in cards:
                if card.card_value == CardValue.ACE:
                    card_ops[card] = [CardOpRun(board, 1), CardOpStart(board)]
                elif card.card_value == CardValue.TWO:
                    card_ops[card] = [CardOpRun(board, 2)]
                elif card.card_value == CardValue.THREE:
                    card_ops[card] = [CardOpRun(board, 3)]
                elif card.card_value == CardValue.FOUR:
                    card_ops[card] = [CardOpRun(board, -4)]
                elif card.card_value == CardValue.FIVE:
                    card_ops[card] = [CardOpRun(board, 5)]
                elif card.card_value == CardValue.SIX:
                    card_ops[card] = [CardOpRun(board, 6)]
                elif card.card_value == CardValue.SEVEN:
                    card_ops[card] = [CardOpSplitTwoMarbles(board)]
                elif card.card_value == CardValue.EIGHT:
                    card_ops[card] = [CardOpRun(board, 8)]
                elif card.card_value == CardValue.NINE:
                    card_ops[card] = [CardOpRun(board, 9)]
                elif card.card_value == CardValue.TEN:
                    card_ops[card] = [CardOpRun(board, 10)]
                elif card.card_value == CardValue.JACK:
                    card_ops[card] = [CardOpSwitchOneOwnMarble(board)]
                elif card.card_value == CardValue.QUEEN:
                    card_ops[card] = [CardOpRun(board, 12)]
                elif card.card_value == CardValue.KING:
                    card_ops[card] = [CardOpStart(board)]
        elif self.game_type == "KeezSimple":
            for card in cards:
                if card.card_value == CardValue.ACE:
                    card_ops[card] = [CardOpRun(board, 1), CardOpStart(board)]
                elif card.card_value == CardValue.TWO:
                    card_ops[card] = [CardOpRun(board, 2)]
                elif card.card_value == CardValue.THREE:
                    card_ops[card] = [CardOpRun(board, 3)]
                elif card.card_value == CardValue.FOUR:
                    card_ops[card] = [CardOpRun(board, -4)]
                elif card.card_value == CardValue.FIVE:
                    card_ops[card] = [CardOpRun(board, 5)]
                elif card.card_value == CardValue.SIX:
                    card_ops[card] = [CardOpRun(board, 6)]
                elif card.card_value == CardValue.SEVEN:
                    card_ops[card] = [CardOpRun(board, 7)]  # No CardOpSplitTwoMarbles(board)]
                elif card.card_value == CardValue.EIGHT:
                    card_ops[card] = [CardOpRun(board, 8)]
                elif card.card_value == CardValue.NINE:
                    card_ops[card] = [CardOpRun(board, 9)]
                elif card.card_value == CardValue.TEN:
                    card_ops[card] = [CardOpRun(board, 10)]
                elif card.card_value == CardValue.JACK:
                    card_ops[card] = [CardOpSwitchOneOwnMarble(board)]
                elif card.card_value == CardValue.QUEEN:
                    card_ops[card] = [CardOpRun(board, 12)]
                elif card.card_value == CardValue.KING:
                    card_ops[card] = [CardOpStart(board)]
        return card_ops

