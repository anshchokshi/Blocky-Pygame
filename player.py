"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.

    """

    players = []
    id_ = 0
    for _ in range(num_human):
        goals = generate_goals(1)
        players.append(HumanPlayer(id_, goals[0]))
        id_ += 1
    for _ in range(num_random):
        goals = generate_goals(1)
        players.append(RandomPlayer(id_, goals[0]))
        id_ += 1
    for i in smart_players:
        goals = generate_goals(1)
        players.append(SmartPlayer(id_, goals[0], i))
        id_ += 1

    return players


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """

    if block.level == level:
        pos = block.position
        x = location[0]
        y = location[1]
        if pos[0] <= x < (pos[0] + block.size) and pos[1] <= y < \
                (pos[1] + block.size):
            return block
        else:
            return None
    else:
        count = None
        for child in block.children:
            count = _get_block(child, location, level)
            if count is not None:
                return count
        return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        ##block = _get_block(board, mouse_pos, self._level)
        block = _get_block(board, mouse_pos, min(self._level, board.max_depth))
        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)
            self._desired_action = None
            return move


class RandomPlayer(Player):
    """
    === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    """
    _proceed: bool
    _level: int

    def __init__(self, player_id: int, goal: Goal) -> None:

        Player.__init__(self, player_id, goal)
        self._proceed = False
        self._level = 0

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed or board is None:
            return None
        else:
            final = ()
            x = self._height(board)
            count = random.randint(0, x)
            lst = self._random(board, count)
            copy = lst[random.randint(0, len(lst) - 1)]
            block = copy.create_copy()
            while self._proceed:
                x = self._height(board)
                count = random.randint(0, x)
                # lst = board.random(count)
                lst = self._random(board, count)
                copy = lst[random.randint(0, len(lst) - 1)]
                block = copy.create_copy()
                temp = random.randint(0, 6)
                j = random.randint(0, 1)
                if temp == 0 and block.smashable():
                    final = "smash", None, copy
                    self._proceed = False

                elif temp in(4, 2) and block.swap(j):
                    final = "swap", j, copy
                    self._proceed = False
                elif temp in (1, 3) and block.rotate(temp):
                    final = "rotate", temp, copy
                    self._proceed = False
                elif temp == 5 and block.paint(self.goal.colour):
                    final = "paint", None, copy
                    self._proceed = False
                elif temp == 6 and block.combine():
                    final = "combine", None, copy
                    self._proceed = False

        return final

    def _height(self, block: Block) -> int:
        """
        private helper function that returns the height of the block

        """
        if len(block.children) == 0:
            return block.level
        else:

            max_ = 0
            for item in block.children:
                max_ = self._height(item)

            return max_

    def _random(self, block: Block, level: int) -> List[Block]:
        """
        private helper function that returns a List of blocks at this given
        level
        """
        if block.level == level:
            return [block]
        else:
            final = []
            for item in block.children:
                final.extend(self._random(item, level))
            return final


class SmartPlayer(Player):
    """
    === Private Attributes ===
        _proceed:
        True when the player should make a move, False when the player should
        wait.
    """

    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        current = self.goal.score(board)
        highest = 0

        if not self._proceed:
            return None
        else:
            highest_move = None
            for _ in range(self._difficulty):

                valid = False
                while not valid:
                    x = self._height(board)
                    count = random.randint(0, x)

                    lst = self._random(board, count)

                    block = lst[random.randint(0, len(lst) - 1)]
                    copy = block.create_copy()
                    temp = random.randint(0, 6)
                    j = random.randint(0, 1)
                    if temp == 0 and copy.smashable():
                        copy.smash()
                        count = self.goal.score(copy)
                        if highest < count:
                            highest = count
                            highest_move = "smash", None, block
                        valid = True

                    elif temp in (4, 2) and copy.swap(j):
                        count = self.goal.score(copy)
                        if highest < count:
                            highest = count
                            highest_move = "swap", j, block
                        valid = True

                    elif temp in (1, 3) and copy.rotate(temp):
                        count = self.goal.score(copy)
                        if highest < count:
                            highest = count
                            highest_move = "rotate", temp, block
                        valid = True

                    elif temp == 5 and copy.paint(self.goal.colour):
                        count = self.goal.score(copy)
                        if highest < count:
                            highest = count
                            highest_move = "paint", None, block
                        valid = True

                    elif temp == 6 and copy.combine():

                        count = self.goal.score(copy)
                        if highest < count:
                            highest = count
                            highest_move = "combine", None, block
                        valid = True

            if highest > current:

                self._proceed = False
                return highest_move
            else:
                self._proceed = False
                highest_move = "pass", None, board
                return highest_move

    def _height(self, block: Block) -> int:
        """
        private helper function that returns the height of the block

        """
        if len(block.children) == 0:
            return block.level
        else:

            max_ = 0
            for item in block.children:
                max_ = self._height(item)

            return max_

    def _random(self, block: Block, level: int) -> List[Block]:
        """
        private helper function that returns a List of blocks at this given
        level
        """
        if block.level == level:
            return [block]
        else:
            final = []
            for item in block.children:
                final.extend(self._random(item, level))
            return final


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
