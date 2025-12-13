# AI_uno.py
# main AI file
import random

# -----------------------GAME STATE-----------------------#
class GameState:
    """Represents a snapshot of the Uno game for AI evaluation."""
    def __init__(self, ai_hand, opponent_hand, current_card, deck_size, current_player):
        """
        Initialize game state.
        ai_hand: List of Card objects in AI's hand
        opponent_hand: List of Card objects in opponent's hand
        current_card: Current card on discard pile
        deck_size: Number of cards remaining in deck
        current_player: 'ai' or 'opponent'
        """
        self.ai_hand = ai_hand
        self.opponent_hand = opponent_hand
        self.current_card = current_card
        self.deck_size = deck_size
        self.current_player = current_player

        # Pre-compute color distributions for evaluation
        self.ai_color_count = self._count_colors(ai_hand)
        self.opp_color_count = self._count_colors(opponent_hand)

    def _count_colors(self, hand):
        """Count the number of cards of each color in a given hand."""
        counts = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0, 'wild': 0}
        for card in hand:
            if card.text in ['wild', 'wild draw four']:
                counts['wild'] += 1
            else:
                if card.color in counts:
                    counts[card.color] += 1
        return counts

    def is_terminal(self):
        """Check if the game has ended (any player has no cards)."""
        return len(self.ai_hand) == 0 or len(self.opponent_hand) == 0

    def apply_move(self, card, is_ai):
        """
        Generate a new game state after a player plays a card.
        card: Card to play
        is_ai: True if AI is playing the card
        Returns a new GameState object
        """
        if is_ai:
            new_ai_hand = [c for c in self.ai_hand if c != card]
            new_opponent_hand = self.opponent_hand.copy()
            next_player = 'opponent'
        else:
            new_ai_hand = self.ai_hand.copy()
            new_opponent_hand = [c for c in self.opponent_hand if c != card]
            next_player = 'ai'

        return GameState(
            ai_hand=new_ai_hand,
            opponent_hand=new_opponent_hand,
            current_card=card,
            deck_size=self.deck_size,
            current_player=next_player
        )

    def get_valid_moves(self, is_ai):
        """
        Return a list of cards that can be legally played for the current player.
        """
        hand = self.ai_hand if is_ai else self.opponent_hand
        valid = []
        for card in hand:
            if (card.color == self.current_card.color or
                card.text == self.current_card.text or
                    card.text in ['wild', 'wild draw four']):
                valid.append(card)
        return valid

# -----------------------AI BOT-----------------------#
class AI_bot:
    """Represents the AI player and decision-making logic."""
    def __init__(self, name, deck, hand, difficulty='medium'):
        self.name = name
        self.hand = hand
        self.is_AI_turn = False
        self.difficulty = difficulty

        self.deck_size = len(deck)
        self.opponent_hand_size = 7
        self.discard_history = []

        # Difficulty settings for minimax depth and opponent sampling
        self.DEPTH_CONFIG = {'easy': 2, 'medium': 4, 'hard': 6}
        self.SAMPLE_CONFIG = {'easy': 2, 'medium': 4, 'hard': 6}

    # -----------------------CORE METHODS-----------------------#
    def draw_card(self, deck=None):
        """Draw a card from the deck and add it to AI's hand."""
        if deck and len(deck) > 0:
            card = deck.pop()
            self.hand.append(card)
            return card
        return None

    def draw_card_silent(self, deck=None):
        """Draw a card silently (no UI effect)."""
        if deck and len(deck) > 0:
            drawn = deck.pop()
            self.hand.append(drawn)
            return drawn
        return None

    def skip(self):
        """Placeholder for skip logic."""
        pass

    def reverse(self):
        """Placeholder for reverse logic."""
        pass

    def random_card(self, hand, current_card, deck):
        """
        Select a random valid card from hand to play.
        Draw a card if no valid moves are available.
        """
        valid_card = []
        for card in hand:
            if (card.color == current_card.color or
                card.text == current_card.text or
                    card.text in ['wild', 'wild draw four']):
                valid_card.append(card)

        if not valid_card:
            if deck:
                new_card = deck.pop()
                self.hand.append(new_card)
                return None
            return None
        else:
            self.choosen_card = random.choice(valid_card)
            return self.choosen_card

    def play_card(self, random_card, speed=1):
        """Placeholder for logic to play a card in UI."""
        if random_card is None:
            return

    # -----------------------HELPERS-----------------------#
    def _get_valid_cards(self, hand, current_card):
        """Return all cards from hand that can be legally played."""
        valid = []
        for card in hand:
            if (card.color == current_card.color or
                card.text == current_card.text or
                    card.text in ['wild', 'wild draw four']):
                valid.append(card)
        return valid

    def _count_colors(self, hand):
        """Count number of cards per color, including wilds."""
        counts = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0, 'wild': 0}
        for card in hand:
            if card.text in ['wild', 'wild draw four']:
                counts['wild'] += 1
            elif card.color in counts:
                counts[card.color] += 1
        return counts

    def _generate_full_deck(self):
        """Return a list of all cards in a standard Uno deck."""
        colors = ['red', 'yellow', 'green', 'blue']
        numbers = ['0', '1', '1', '2', '2', '3', '3', '4', '4', '5', '5',
                   '6', '6', '7', '7', '8', '8', '9', '9']
        actions = ['skip', 'reverse', 'draw two']
        wilds = ['wild', 'wild draw four']

        deck = []
        for color in colors:
            for number in numbers:
                deck.append((color, number))
            for action in actions:
                deck.append((color, action))
                deck.append((color, action))
        for _ in range(4):
            for wild in wilds:
                deck.append(('gray40', wild))
        return deck

    def _get_depth_for_difficulty(self):
        """Return minimax depth based on AI difficulty."""
        return self.DEPTH_CONFIG.get(self.difficulty, 4)

    def _get_num_samples(self):
        """Return number of opponent hand samples based on difficulty."""
        return self.SAMPLE_CONFIG.get(self.difficulty, 4)

    # -----------------------EVALUATION-----------------------#
    def _evaluate_state(self, state):
        """Compute heuristic value for a given game state."""
        if len(state.ai_hand) == 0:
            return 1000  # AI won
        if len(state.opponent_hand) == 0:
            return -1000  # Opponent won

        score = 0.0
        hand_size_diff = len(state.opponent_hand) - len(state.ai_hand)
        score += hand_size_diff * 100
        score += self._evaluate_special_cards(state) * 50
        score += self._evaluate_color_potential(state) * 30
        score += self._evaluate_playability(state) * 20
        score += self._evaluate_winning_chance(state) * 150
        return score

    def _evaluate_special_cards(self, state):
        """Score difference based on special cards in hand."""
        ai_special, opp_special = 0, 0
        for card in state.ai_hand:
            if card.text in ['skip', 'reverse', 'draw two']:
                ai_special += 1
            elif card.text in ['wild', 'wild draw four']:
                ai_special += 2
        for card in state.opponent_hand:
            if card.text in ['skip', 'reverse', 'draw two']:
                opp_special += 1
            elif card.text in ['wild', 'wild draw four']:
                opp_special += 2
        return ai_special - opp_special

    def _evaluate_color_potential(self, state):
        """Evaluate advantage based on color concentration in hand."""
        ai_max = max(state.ai_color_count.values()) if state.ai_color_count else 0
        opp_max = max(state.opp_color_count.values()) if state.opp_color_count else 0
        ai_conc = ai_max / max(len(state.ai_hand), 1)
        opp_conc = opp_max / max(len(state.opponent_hand), 1)
        return ai_conc - opp_conc

    def _evaluate_playability(self, state):
        """Evaluate how many cards are playable for each player."""
        ai_valid = len(state.get_valid_moves(True))
        opp_valid = len(state.get_valid_moves(False))
        return (ai_valid / max(len(state.ai_hand), 1)) - (opp_valid / max(len(state.opponent_hand), 1))

    def _evaluate_winning_chance(self, state):
        """Evaluate winning chance based on hand sizes."""
        ai_cards = len(state.ai_hand)
        opp_cards = len(state.opponent_hand)
        bonus = 2.0 if ai_cards <= 2 else 1.0 if ai_cards <= 4 else 0.0
        penalty = -2.0 if opp_cards <= 2 else -1.0 if opp_cards <= 4 else 0.0
        return bonus + penalty

    # -----------------------MINIMAX-----------------------#
    def _order_moves(self, valid_cards, state):
        """Order moves heuristically to improve alpha-beta pruning efficiency."""
        def move_priority(card):
            if len(state.ai_hand) == 1:
                return 1000
            if card.text == 'wild draw four':
                return 900
            elif card.text == 'wild':
                return 800
            elif card.text == 'draw two':
                return 700
            elif card.text in ['skip', 'reverse']:
                return 600
            elif card.color == state.current_card.color:
                return 500
            else:
                return 400
        return sorted(valid_cards, key=move_priority, reverse=True)

    def _minimax(self, state, depth, alpha, beta, is_maximizing):
        """Recursive minimax with alpha-beta pruning to evaluate moves."""
        if depth == 0 or state.is_terminal():
            return self._evaluate_state(state)
        if is_maximizing:
            max_eval = float('-inf')
            valid_moves = self._order_moves(state.get_valid_moves(True), state)
            if not valid_moves:
                return self._evaluate_state(state)
            for move in valid_moves:
                next_state = state.apply_move(move, True)
                eval_score = self._minimax(next_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            valid_moves = self._order_moves(state.get_valid_moves(False), state)
            if not valid_moves:
                return self._evaluate_state(state)
            for move in valid_moves:
                next_state = state.apply_move(move, False)
                eval_score = self._minimax(next_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def minimax_card(self, hand, current_card):
        """Select the best card to play using minimax over multiple sampled opponent hands."""
        valid_cards = self._get_valid_cards(hand, current_card)
        if not valid_cards:
            return None
        if len(valid_cards) == 1:
            self.choosen_card = valid_cards[0]
            return valid_cards[0]

        depth = self._get_depth_for_difficulty()
        num_samples = self._get_num_samples()
        move_scores = {}

        for _ in range(num_samples):
            opponent_hand_tuples = self._sample_opponent_hand(current_card)
            opponent_hand_objects = [self._create_card_from_tuple(t) for t in opponent_hand_tuples]
            for card in valid_cards:
                initial_state = GameState(
                    ai_hand=[c for c in hand if c != card],
                    opponent_hand=opponent_hand_objects,
                    current_card=card,
                    deck_size=self.deck_size,
                    current_player='opponent'
                )
                score = self._minimax(initial_state, depth, float('-inf'), float('inf'), False)
                card_id = id(card)
                move_scores[card_id] = move_scores.get(card_id, 0) + score

        best_card_id = max(move_scores, key=move_scores.get)
        best_card = next(card for card in valid_cards if id(card) == best_card_id)
        self.choosen_card = best_card
        return best_card

    # -----------------------DETERMINIZATION-----------------------#
    def _get_unknown_cards(self, current_card):
        """Return cards that are not known to AI (for sampling opponent hand)."""
        full_deck = self._generate_full_deck()
        known = {(card.color, card.text) for card in self.hand}
        known.add((current_card.color, current_card.text))
        for card in self.discard_history:
            known.add((card.color, card.text))
        return [c for c in full_deck if c not in known]

    def _sample_opponent_hand(self, current_card):
        """Randomly sample a possible opponent hand from unknown cards."""
        unknown = self._get_unknown_cards(current_card)
        if len(unknown) < self.opponent_hand_size:
            return random.sample(unknown, len(unknown))
        return random.sample(unknown, self.opponent_hand_size)

    def _create_card_from_tuple(self, tup):
        """Create a simple card object from (color, text) tuple."""
        class SimpleCard:
            def __init__(self, color, text):
                self.color = color
                self.text = text
        return SimpleCard(tup[0], tup[1])

    # -----------------------WILD CARD-----------------------#
    def choose_color(self):
        """Select the color that AI has most cards of for wild cards."""
        color_counts = self._count_colors(self.hand)
        best = max(['red', 'yellow', 'green', 'blue'], key=lambda c: color_counts.get(c, 0))
        return best

    def choose_card(self, hand, current_card):
        """Main AI function to choose the next card to play."""
        return self.minimax_card(hand, current_card)
