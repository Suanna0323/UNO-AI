#main AI file
#-----------------------AI-----------------------#
import random

# -----------------------GAME STATE-----------------------#
class GameState:
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
        """Count cards by color in hand."""
        counts = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0, 'wild': 0}
        for card in hand:
            if card.text in ['wild', 'wild draw four']:
                counts['wild'] += 1
            else:
                if card.color in counts:
                    counts[card.color] += 1
        return counts

    def is_terminal(self):
        """Check if game is over (someone has no cards)."""
        return len(self.ai_hand) == 0 or len(self.opponent_hand) == 0

    def apply_move(self, card, is_ai):
        """
        Generate successor state by applying a move.

        card: Card to play
        is_ai: True if AI is playing the card


        Returns New GameState object

        """
        if is_ai:
            # AI plays card - remove from AI hand
            new_ai_hand = [c for c in self.ai_hand if c != card]
            new_opponent_hand = self.opponent_hand.copy()
            next_player = 'opponent'
        else:
            # Opponent plays card - remove from opponent hand
            new_ai_hand = self.ai_hand.copy()
            new_opponent_hand = [c for c in self.opponent_hand if c != card]
            next_player = 'ai'

        # Create new state with played card as current card
        return GameState(
            ai_hand=new_ai_hand,
            opponent_hand=new_opponent_hand,
            current_card=card,
            deck_size=self.deck_size,
            current_player=next_player
        )

    def get_valid_moves(self, is_ai):
        """
        Get valid cards for current player.

        is_ai: True for AI's hand, False for opponent's hand

        Returns list of valid cards that can be played

        """
        hand = self.ai_hand if is_ai else self.opponent_hand
        valid = []
        for card in hand:
            if (card.color == self.current_card.color or
                card.text == self.current_card.text or
                    card.text in ['wild', 'wild draw four']):
                valid.append(card)
        return valid
    
class AI_bot:
    def __init__(self, name, deck, hand, difficulty='medium'):
        self.name = name
        self.hand = hand
        self.is_AI_turn = False
        self.difficulty = difficulty
    
        # Game state tracking for better AI decisions
        self.deck_size = len(deck)
        self.opponent_hand_size = 7  # Initial hand size
        self.discard_history = []  # Track played cards for color inference

        # Difficulty configuration
        self.DEPTH_CONFIG = {'easy': 2, 'medium': 4, 'hard': 6}
        self.SAMPLE_CONFIG = {'easy': 5, 'medium': 10, 'hard': 15}

    def draw_card(self, deck=None):
        """Draw a card from the deck (used by special cards)"""
        if deck and len(deck) > 0:
            card = deck.pop()
            self.hand.append(card)
            return card
        return None

    def skip(self):
        pass

    def reverse(self):
        pass

    
    def choose_color(self): #wild
        pass

#randomly deal a valid card, need to add AI logic later
    def random_card(self, hand, current_card, deck):
        valid_card = []
        for card in hand:
            if card.color == current_card.color or card.text == current_card.text or card.text in ['wild', 'wild draw four']:
                valid_card.append(card)

        #if no valid card, draw 1 card
        if not valid_card:
            if deck:
                print("AI has no valid card, drawing a card") #for debugging only
                new_card = deck.pop()
                self.hand.append(new_card)
                return None  # Return None to skip turn after drawing
            #skip
            print("restart game")
            return None
        else:
            self.choosen_card = random.choice(valid_card)
            print("AI played: ", self.choosen_card.color, self.choosen_card.text)
            return self.choosen_card
    
    #animation for playing card...looks much cooler with this
    def play_card(self, random_card, speed=1): #change the speed for faster/slower animation
        #no card to play
        if random_card is None:
            return
        
        x = random_card.widget.winfo_x()
        y = random_card.widget.winfo_y()
        random_card.place(x=0, y=0, width = 100, height = 120)
        random_card.widget.tkraise()

        while x < 350 or y < 200:
            if x < 350:
                x += speed
            if y < 200:
                y += speed
            random_card.place(x=x, y=y, width = 100, height = 120)
            random_card.widget.update()

     # -----------------------HELPER UTILITIES-----------------------#
    def _get_valid_cards(self, hand, current_card):
        """Get all valid cards that can be played."""
        valid = []
        for card in hand:
            if (card.color == current_card.color or
                card.text == current_card.text or
                    card.text in ['wild', 'wild draw four']):
                valid.append(card)
        return valid

    def _count_colors(self, hand):
        """Count cards by color in hand."""
        counts = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0, 'wild': 0}
        for card in hand:
            if card.text in ['wild', 'wild draw four']:
                counts['wild'] += 1
            else:
                if card.color in counts:
                    counts[card.color] += 1
        return counts

    def _generate_full_deck(self):
        """
        Generate all possible UNO cards for determinization.

        """
        colors = ['red', 'yellow', 'green', 'blue']
        numbers = ['0', '1', '1', '2', '2', '3', '3', '4', '4', '5', '5',
                   '6', '6', '7', '7', '8', '8', '9', '9']
        actions = ['skip', 'reverse', 'draw two']
        wilds = ['wild', 'wild draw four']

        deck = []

        # Number cards
        for color in colors:
            for number in numbers:
                deck.append((color, number))

        # Action cards (2 of each per color)
        for color in colors:
            for action in actions:
                deck.append((color, action))
                deck.append((color, action))

        # Wild cards (4 of each type)
        for _ in range(4):
            for wild in wilds:
                deck.append(('gray40', wild))

        return deck

    def _get_depth_for_difficulty(self):
        """Get search depth based on difficulty."""
        return self.DEPTH_CONFIG.get(self.difficulty, 4)

    def _get_num_samples(self):
        """Get number of determinization samples based on difficulty."""
        return self.SAMPLE_CONFIG.get(self.difficulty, 10)

    # -----------------------EVALUATION FUNCTION-----------------------#
    def _evaluate_state(self, state):
        """
        Evaluate game state from AI's perspective.
        Higher score = better for AI.

        Returns Float score (positive favors AI, negative favors opponent)

        """
        # Terminal state checks (highest priority)
        if len(state.ai_hand) == 0:
            return 1000  # AI wins!
        if len(state.opponent_hand) == 0:
            return -1000  # AI loses

        # Weighted sum of features
        score = 0.0

        # Feature 1: Hand size difference (most important)
        hand_size_diff = len(state.opponent_hand) - len(state.ai_hand)
        score += hand_size_diff * 100

        # Feature 2: Special cards in hand
        score += self._evaluate_special_cards(state) * 50

        # Feature 3: Color matching potential
        score += self._evaluate_color_potential(state) * 30

        # Feature 4: Card playability
        score += self._evaluate_playability(state) * 20

        # Feature 5: Winning probability estimate
        score += self._evaluate_winning_chance(state) * 150

        return score

    def _evaluate_special_cards(self, state):
        """
        Score based on special cards in hands.
        Special cards are powerful (Skip, Reverse, Draw Two, Wild).

        """
        ai_special = 0
        opp_special = 0

        # Count special cards
        for card in state.ai_hand:
            if card.text in ['skip', 'reverse', 'draw two']:
                ai_special += 1
            elif card.text in ['wild', 'wild draw four']:
                ai_special += 2  # Wilds are more valuable

        for card in state.opponent_hand:
            if card.text in ['skip', 'reverse', 'draw two']:
                opp_special += 1
            elif card.text in ['wild', 'wild draw four']:
                opp_special += 2

        return ai_special - opp_special

    def _evaluate_color_potential(self, state):
        """
        Score based on color distribution.
        Better to have concentrated colors (easier to chain plays).

        """
        # Calculate color concentration for AI
        ai_max_color = max(state.ai_color_count.values()
                           ) if state.ai_color_count else 0

        # Calculate for opponent
        opp_max_color = max(state.opp_color_count.values()
                            ) if state.opp_color_count else 0

        # Prefer having one dominant color (concentration)
        ai_concentration = ai_max_color / max(len(state.ai_hand), 1)
        opp_concentration = opp_max_color / max(len(state.opponent_hand), 1)

        return (ai_concentration - opp_concentration)

    def _evaluate_playability(self, state):
        """
        Score based on how many valid moves each player has.
        More options = better position.

        """
        ai_valid = len(state.get_valid_moves(is_ai=True))
        opp_valid = len(state.get_valid_moves(is_ai=False))

        # Normalize by hand size
        ai_playability = ai_valid / max(len(state.ai_hand), 1)
        opp_playability = opp_valid / max(len(state.opponent_hand), 1)

        return ai_playability - opp_playability

    def _evaluate_winning_chance(self, state):
        """
        Estimate probability of winning based on hand size ratio.

        """
        ai_cards = len(state.ai_hand)
        opp_cards = len(state.opponent_hand)

        # Bonus for being close to winning
        if ai_cards <= 2:
            bonus = 2.0  # Close to winning
        elif ai_cards <= 4:
            bonus = 1.0
        else:
            bonus = 0.0

        # Penalty if opponent close to winning
        if opp_cards <= 2:
            penalty = -2.0  # Opponent close to winning
        elif opp_cards <= 4:
            penalty = -1.0
        else:
            penalty = 0.0

        return bonus + penalty

    # -----------------------DETERMINIZATION-----------------------#
    def _get_unknown_cards(self, current_card):
        """
        Calculate which cards are unknown to AI.
        Unknown = All cards - AI's hand - Current card - Discard history

        """
        # Generate full deck as tuples (color, text)
        full_deck_tuples = self._generate_full_deck()

        # Convert AI's hand to tuples for comparison
        known_tuples = set()
        for card in self.hand:
            known_tuples.add((card.color, card.text))

        # Add current card
        known_tuples.add((current_card.color, current_card.text))

        # Add discard history
        for card in self.discard_history:
            known_tuples.add((card.color, card.text))

        # Filter to unknown cards
        unknown = [card_tuple for card_tuple in full_deck_tuples
                   if card_tuple not in known_tuples]

        return unknown

    def _sample_opponent_hand(self, current_card):
        """
        Generate a random possible opponent hand based on unknown cards.

        Returns list of card tuples representing a possible opponent hand

        """
        # Get cards we know are unknown
        unknown_cards = self._get_unknown_cards(current_card)

        # Sample random cards for opponent hand
        if len(unknown_cards) < self.opponent_hand_size:
            # Edge case: not enough cards to sample
            sampled_hand = random.sample(unknown_cards, min(
                len(unknown_cards), self.opponent_hand_size))
        else:
            sampled_hand = random.sample(
                unknown_cards, self.opponent_hand_size)

        return sampled_hand

    def _create_card_from_tuple(self, card_tuple):
        """
        Create a lightweight card object from tuple for use in GameState.
        We need actual Card-like objects for the game state.

        """
        # Create a simple object with color and text attributes
        class SimpleCard:
            def __init__(self, color, text):
                self.color = color
                self.text = text

        return SimpleCard(card_tuple[0], card_tuple[1])

    # -----------------------MOVE ORDERING-----------------------#
    def _order_moves(self, valid_cards, state):
        """
        Order moves by heuristic priority for better alpha-beta pruning.

        Priority (high to low):
        1. Cards that win the game (empty hand after play)
        2. Wild Draw Four
        3. Wild
        4. Draw Two
        5. Skip/Reverse
        6. Cards matching current color
        7. Number cards

        """
        def move_priority(card):
            # Win immediately
            if len(state.ai_hand) == 1:
                return 1000

            # Special card priorities
            if card.text == 'wild draw four':
                return 900
            elif card.text == 'wild':
                return 800
            elif card.text == 'draw two':
                return 700
            elif card.text in ['skip', 'reverse']:
                return 600
            elif card.color == state.current_card.color:
                return 500  # Color match is good
            else:
                return 400  # Text match

        return sorted(valid_cards, key=move_priority, reverse=True)

    # -----------------------MINIMAX ALGORITHM-----------------------#
    def _minimax(self, state, depth, alpha, beta, is_maximizing):
        """
        Minimax algorithm with alpha-beta pruning.

        state: GameState object
        depth: Remaining search depth
        alpha: Best value for maximizer
        beta: Best value for minimizer
        is_maximizing: True if AI's turn (maximizing), False if opponent's turn

        Returns evaluation score for this state

        """
        # Terminal conditions
        if depth == 0 or state.is_terminal():
            return self._evaluate_state(state)

        if is_maximizing:  # AI's turn (maximize score)
            max_eval = float('-inf')

            # Generate all possible moves for AI
            valid_moves = state.get_valid_moves(is_ai=True)

            if not valid_moves:
                # No valid moves - would need to draw card
                # For simplicity, return current evaluation
                return self._evaluate_state(state)

            # Move ordering heuristic for better pruning
            valid_moves = self._order_moves(valid_moves, state)

            for move in valid_moves:
                # Generate successor state
                next_state = state.apply_move(move, is_ai=True)

                # Recursive call
                eval_score = self._minimax(
                    next_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)

                # Alpha-beta pruning
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff

            return max_eval

        else:  # Opponent's turn (minimize score)
            min_eval = float('inf')

            # Generate all possible moves for opponent
            valid_moves = state.get_valid_moves(is_ai=False)

            if not valid_moves:
                # No valid moves
                return self._evaluate_state(state)

            # Move ordering
            valid_moves = self._order_moves(valid_moves, state)

            for move in valid_moves:
                # Generate successor state
                next_state = state.apply_move(move, is_ai=False)

                # Recursive call
                eval_score = self._minimax(
                    next_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)

                # Alpha-beta pruning
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff

            return min_eval

    def minimax_card(self, hand, current_card):
        """
        Main entry point for Minimax AI decision making with determinization.

        hand: AI's current hand (list of Card objects)
        current_card: Current card on discard pile

        Returns card object to play (or None if must draw)

        """
        # Get valid moves
        valid_cards = self._get_valid_cards(hand, current_card)

        if not valid_cards:
            return None  # No valid cards - must draw

        # If only one valid card, play it
        if len(valid_cards) == 1:
            self.choosen_card = valid_cards[0]
            print(
                f"AI played: {self.choosen_card.color} {self.choosen_card.text}")
            return self.choosen_card

        # Get search depth and number of samples based on difficulty
        depth = self._get_depth_for_difficulty()
        num_samples = self._get_num_samples()

        # Determinization - sample possible opponent hands
        move_scores = {}

        for sample_idx in range(num_samples):
            # Sample a possible opponent hand
            opponent_hand_tuples = self._sample_opponent_hand(current_card)
            opponent_hand_objects = [self._create_card_from_tuple(
                t) for t in opponent_hand_tuples]

            # For each valid card, run minimax
            for card in valid_cards:
                # Create initial game state (after AI plays this card)
                initial_state = GameState(
                    # Remove played card
                    ai_hand=[c for c in hand if c != card],
                    opponent_hand=opponent_hand_objects,
                    current_card=card,  # This card becomes current
                    deck_size=self.deck_size,
                    current_player='opponent'  # After AI plays, opponent's turn
                )

                # Run minimax with alpha-beta pruning
                score = self._minimax(initial_state, depth, float(
                    '-inf'), float('inf'), False)

                # Accumulate scores (use id as key since Card objects might not be hashable)
                card_id = id(card)
                move_scores[card_id] = move_scores.get(card_id, 0) + score

        # Average scores and select best move
        best_card_id = max(move_scores, key=move_scores.get)
        best_card = next(
            card for card in valid_cards if id(card) == best_card_id)

        self.choosen_card = best_card
        print(f"AI played: {self.choosen_card.color} {self.choosen_card.text}")
        return self.choosen_card

    # -----------------------WILD CARD COLOR SELECTION-----------------------#
    def choose_color(self):
        """
        Sophisticated wild card color selection strategy.

        Balances multiple factors:
        1. Color with most cards in AI hand (60% weight)
        2. Color opponent likely has fewer of (30% weight)
        3. Color with special cards (10% weight)

        Returns best color to choose ('red', 'yellow', 'green', or 'blue')
        """
        # Count colors in AI's hand
        color_counts = self._count_colors(self.hand)

        # Infer opponent's weak colors from discard history
        opponent_weak_colors = self._infer_opponent_weak_colors()

        # Weight 1: Color with most cards (60%)
        ai_color_score = {
            'red': color_counts.get('red', 0) * 0.6,
            'yellow': color_counts.get('yellow', 0) * 0.6,
            'green': color_counts.get('green', 0) * 0.6,
            'blue': color_counts.get('blue', 0) * 0.6
        }

        # Weight 2: Opponent's weak colors (30%)
        for color, weakness in opponent_weak_colors.items():
            ai_color_score[color] += weakness * 0.3

        # Weight 3: Colors with special cards (10%)
        for card in self.hand:
            if card.text in ['skip', 'reverse', 'draw two'] and card.color in ai_color_score:
                ai_color_score[card.color] += 0.1

        # Return color with highest score
        best_color = max(ai_color_score, key=ai_color_score.get)
        return best_color

    def _infer_opponent_weak_colors(self):
        """
        Infer which colors opponent likely has fewer of based on discard history.

        """
        # Count how often each color was NOT played when it could have been
        color_weakness = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0}

        # Simple heuristic: if a color appears less in discard history,
        # opponent might have fewer of that color
        color_play_counts = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0}

        for card in self.discard_history:
            if card.color in color_play_counts:
                color_play_counts[card.color] += 1

        # Normalize: colors with fewer plays are "weaker"
        total_plays = sum(color_play_counts.values())
        if total_plays > 0:
            for color in color_weakness:
                # Inverse relationship: fewer plays = higher weakness
                color_weakness[color] = 1.0 - \
                    (color_play_counts[color] / total_plays)

        return color_weakness

    def choose_card(self, hand, current_card):
        """
        Main entry point for AI decision.
        Delegates to minimax_card().

        """
        return self.minimax_card(hand, current_card)