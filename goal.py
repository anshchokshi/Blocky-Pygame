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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)

    """

    goals = []
    count = random.randint(0, 1)
    temp = random.sample(range(0, len(COLOUR_LIST)), num_goals)
    if count == 0:

        for i in range(num_goals):
            goals.append(PerimeterGoal(COLOUR_LIST[temp[i]]))
        return goals
    else:
        for i in range(num_goals):
            goals.append(BlobGoal(COLOUR_LIST[temp[i]]))
        return goals


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """

    if block.level == block.max_depth:
        return [[block.colour]]
    elif len(block.children) == 0:

        x = 2 ** (block.max_depth - block.level)
        temp = []

        for a in range(x):
            temp.append([])
            for b in range(x):
                temp[a].insert(b, block.colour)

        return temp

    else:

        if (block.level + 1) == block.max_depth:
            temp = [[], []]
            temp[0].append(block.children[1].colour)
            temp[0].append(block.children[2].colour)
            temp[1].append(block.children[0].colour)
            temp[1].append(block.children[3].colour)
            return temp
        else:
            x = 2 ** (block.max_depth - block.level)
            temp = []
            for i in range(x):
                temp.append([])
            count = _flatten(block.children[1])
            for i in range(len(count)):
                temp[i].extend(count[i])
            count = _flatten(block.children[2])
            y = len(count)
            for i in range(len(count)):
                temp[i].extend(count[i])

            count = _flatten(block.children[0])
            for i in range(len(count)):
                temp[i + y].extend(count[i])
            count = _flatten(block.children[3])

            for i in range(len(count)):
                temp[i + y].extend(count[i])

            return temp

class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """
    Player must aim to put the most possible units on the outer
    perimeter of the board
    """

    def score(self, board: Block) -> int:
        flatten = _flatten(board)
        score = 0
        for i in range(len(flatten)):
            for j in range(len(flatten)):
                if flatten[i][j] == self.colour and \
                        (i == 0 or i + 1 == len(flatten)):

                    if j == 0 or j + 1 == len(flatten):
                        score += 2
                    else:
                        score += 1
                else:
                    if (j == 0 or j + 1 == len(flatten)) and\
                            flatten[i][j] == self.colour:
                        score += 1

        return score

    def description(self) -> str:
        """
        returns the description of the goal
        """
        color = colour_name(self.colour)
        return 'Player must aim to put the most possible units {} on the outer'\
               'perimeter'.format(color)


class BlobGoal(Goal):
    """
    Player must aim for the largest "blob"

    """
    def score(self, board: Block) -> int:
        """
        returns the blob score of this board
        """
        flat = _flatten(board)
        count = 0
        i = len(flat)
        temp = []
        for a in range(i):
            temp.append([])
            for b in range(i):
                temp[a].insert(b, -1)
        highest = 0
        for x in range(i):
            for y in range(i):

                count = self._undiscovered_blob_size((x, y), flat, temp)
                if highest < count:
                    highest = count

        return highest

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """

        x = pos[0]
        y = pos[1]
        if visited[x][y] == 1 or visited[x][y] == 0:
            return 0
        elif board[x][y] != self.colour:
            visited[x][y] = 0
            return 0
        else:
            visited[x][y] = 1
            if self._condition(pos, board, visited):
                return 1
            else:
                position = self._pos(pos, board, visited)
                count = 1
                for item in position:
                    temp = (item[0], item[1])
                    count += self._undiscovered_blob_size(temp, board, visited)
                return count

    def _condition(self, pos: Tuple[int, int],
                   board: List[List[Tuple[int, int, int]]],
                   visited: List[List[int]]) -> bool:
        """
        private helper function that returns False if there exists a unit block
        next to the given block on sides or up or down
        """
        x = pos[0]
        y = pos[1]
        final = True

        if 0 < x:
            if board[x - 1][y] == self.colour and visited[x - 1][y] == -1:
                final = False
        if x < len(board[0]) - 1:
            if board[x + 1][y] == self.colour and visited[x + 1][y] == -1:
                final = False
        if 0 < y:
            if board[x][y - 1] == self.colour and visited[x][y - 1] == -1:
                final = False
        if y < len(board[0]) - 1 and visited[x][y + 1] == -1:
            if board[x][y + 1] == self.colour:
                final = False
        return final

    def _pos(self, pos: Tuple[int, int],
             board: List[List[Tuple[int, int, int]]],
             visited: List[List[int]]) -> List[Tuple[int, int]]:
        """
        private helper function that returns all the position of blocks that
        connected with the given block
        """
        x = pos[0]
        y = pos[1]
        final = []

        if 0 < x:
            if board[x - 1][y] == self.colour and visited[x - 1][y] == -1:
                final.append((x-1, y))

        if x < len(board[0]) - 1:
            if board[x + 1][y] == self.colour and visited[x + 1][y] == -1:
                final.append((x+1, y))

        if 0 < y:
            if board[x][y - 1] == self.colour and visited[x][y - 1] == -1:
                final.append((x, y-1))

        if y < len(board[0]) - 1:
            if board[x][y + 1] == self.colour and visited[x][y + 1] == -1:
                final.append((x, y+1))

        return final

    def description(self) -> str:
        """
        returns the description of the goal
        """
        color = colour_name(self.colour)
        return 'Player must aim for the largest "blob" of {}'.format(color)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
