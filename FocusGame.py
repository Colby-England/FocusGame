# Author: Colby England
# Date: 11/13/2020
# Description: An object oriented version of the game Focus/Domination for two players.

# Global constant to limit height of a stack on the game board.
MAX_HEIGHT = 5


class FocusGame:
    """
    Class to represent the game Focus/Domination.

    This class will represent a two person game of Focus. It will ignore the 1x4 extensions on the outside of the
    board. The board will be represented by a list of lists. Each place on the board will be represented by a
    queue object that is defined later on in this program. The two players will be represented by player objects which
    are also defined later in this program.

    This class will directly interface with both the Queue and Player classes.

    This class will be responsible for making player's moves, checking winning conditions and keeping track of the
    game board. It will also allow the user to check the amount of captured and reserved pieces a player has.
    """

    def __init__(self, player_a, player_b):
        """
        Initializes a new focus game with the board configured for a two player start.
        initializes two player objects that take as parameters the tuples player_a & player_b
        Initializes a dictionary _players, that uses the player names as keys and the player objects as values, this
        will make it easier to access a player in later methods.
        Initializes _player_turn to the name of the first player for the beginning of the game.

        player_a: tuple that contains a player's name and their game piece
        player_b: tuple that contains a player's name and their game piece
        """

        self._game_board = [
            [Queue("R"), Queue("R"), Queue("G"),
             Queue("G"), Queue("R"), Queue("R")],
            [Queue("G"), Queue("G"), Queue("R"),
             Queue("R"), Queue("G"), Queue("G")],
            [Queue("R"), Queue("R"), Queue("G"),
             Queue("G"), Queue("R"), Queue("R")],
            [Queue("G"), Queue("G"), Queue("R"),
             Queue("R"), Queue("G"), Queue("G")],
            [Queue("R"), Queue("R"), Queue("G"),
             Queue("G"), Queue("R"), Queue("R")],
            [Queue("G"), Queue("G"), Queue("R"),
             Queue("R"), Queue("G"), Queue("G")],
        ]

        self._first_player = Player(*player_a)
        self._second_player = Player(*player_b)
        self._players = {
            self._first_player.get_name(): self._first_player,
            self._second_player.get_name(): self._second_player
        }
        self._player_turn = self._first_player.get_name()

    def get_game_board(self):
        """ Returns the list of lists that represents the game board. """

        return self._game_board

    def get_player_turn(self):
        """ Returns the player's name whose turn it is. """

        return self._player_turn

    def print_game_board(self):
        """ Prints out a formatted version of the game board. This is for testing/debugging purposes. """

        board = self.get_game_board()

        for row in range(len(board)):
            for column in range(len(board[row])):
                if board[row][column].get_length() > 0:
                    print(board[row][column].display_top(), end=" ")
                else:
                    print(" ", end=" ")
            print("")

    def show_reserve(self, player_name):
        """
        Returns the number of reserve pieces for the given players name.

        player_name: a string containing the player's name that you wish to see reserve pieces for.
        """

        if player_name not in self._players:
            return 0
        else:
            return self._players[player_name].get_reserved()

    def show_captured(self, player_name):
        """
        Returns the number of captured pieces for the given players name.

        player_name: a string containing the player's name that you wish to see captured pieces for.
        """

        if player_name not in self._players:
            return 0
        else:
            return self._players[player_name].get_captured()

    def show_pieces(self, position):
        """
        Returns a list of  the stack of pieces at a given position on the game board. Bottom piece is at index 0.

        position: tuple in the form of (row, tuple) that will be unpacked into ints.
        """

        row, column = position

        return self._game_board[row][column].get_data()

    def reserved_move(self, player_name, position):
        """
        Allows a player to make a move from their reserved pieces to the board. This will place the piece on top of the
        queue at the supplied position on the board. It will also decrement the player's reserve pieces by 1. If the
        player doesn't have any reserve pieces, or the location provided is invalid returns an error message. If the
        move is successful then _player_turn will be updated to the next player's turn.

        player_name: a string containing the player's name that you wish to make the reserved move for
        position: tuple in the form of (row, tuple) that will be unpacked into ints. This
        """

        row, column = position
        player = self._players[player_name]

        # Make sure it is the player's turn
        if player_name != self._player_turn:
            return False

        # Make sure the player has pieces in reserve to play
        if player.get_reserved() <= 0:
            return False

        # Make sure the move is a valid location
        if not self.check_position(row, column):
            return False

        # Add pieces to the stack
        self.get_game_board()[row][column].enqueue(player.get_piece())

        # Remove reserve piece from player
        player.remove_reserved()

        # If needed remove pieces from stack
        self.remove_pieces(player_name, row, column)

        # Swap turns
        self.switch_turns()

    def move_piece(self, player_name, move_from, move_to, num_pieces):
        """
        This method will attempt to make a move for a given player from one position to another moving a given number
        of pieces. This will return error messages if the player attempts to move out of turn, if the locations provided
        are invalid or if the number of pieces to move is invalid. If the move is successful then _player_turn will be
        updated to the next player's turn. This method will remove the given number of pieces from the top of the queue
        at the move_from position. This pieces will be added in reverse order to the queue at the move_to position. Then
        the height of the queue will be checked and pieces moved accordingly if it is greater than the max allowed
        height.

        If the move was successfully the message "successfully moved" will be returned.
        If the move result in a win returns the message "Win"

        If the move results in a queue that is greater than 5 pieces high it will call remove_pieces.

        player_name: String representing the player to make the move
        move_from: tuple that contains the position that the move will originate from.
        move_to: tuple that contains the position that the move will terminate at.
        num_pieces: the number of pieces that the player will attempt to move.

        """

        start_row, start_column = move_from

        end_row, end_column = move_to

        player = self._players[player_name]

        # Make sure it is the player's turn
        if player_name != self._player_turn:
            return False

        # Check that move_from & move_to are valid positions
        if not self.check_position(start_row, start_column) or not self.check_position(end_row, end_column):
            return False

        # Make sure the number of pieces is legal
        if num_pieces > self._game_board[start_row][start_column].get_length():
            return False

        # Check that the move is legal. Moves horizontally or vertically the correct number of squares.
        if not self.check_move(start_row, start_column, end_row, end_column, num_pieces):
            return False

        # Check the player controls the stack
        if player.get_piece() != self._game_board[start_row][start_column].display_top():
            return False

        # Place moved pieces into temp list, remove from starting stack, add to ending stack, remove pieces if
        # height is too large

        moved_pieces = self._game_board[start_row][start_column].remove_items(
            num_pieces)

        self._game_board[end_row][end_column].add_items(moved_pieces)

        self.remove_pieces(player_name, end_row, end_column)

        self.switch_turns()

        if self.check_win(player_name):
            self._player_turn = None
            return "Wins"
        else:
            return "successfully moved"

    def check_win(self, player_name):
        """ Checks if the given player has won the game. """

        wins = True
        player = self._players[player_name]

        if player.get_captured() < 18:
            wins = False

        for row in range(len(self._game_board)):
            for column in range(len(self._game_board)):
                if self._game_board[row][column].get_length() > 0:
                    if self._game_board[row][column].display_top() != player.get_piece():
                        wins = False

        return wins

    def switch_turns(self):
        """ Swaps the player's turns. """

        if self._player_turn == self._first_player.get_name():
            self._player_turn = self._second_player.get_name()
        else:
            self._player_turn = self._first_player.get_name()

    def remove_pieces(self, player_name, row, column):
        """
        Removes pieces from the queue and places them in the appropriate players captured or reserve. Loops through the
        queue and removes pieces from the bottom that exceed the max_height of the queue at the given position on the
        board. It will move the pieces to the appropriate player's captured or reserved pieces based on who made the
        move.

        player_name: a string containing the player's name that you wish to make the reserved move for
        row: int that represents the row of the queue on the board that pieces will be removed from
        column: int that represents the column of the queue on the board that pieces will be removed form
        """

        reserved_player = self._players[player_name]
        stack = self.get_game_board()[row][column]

        # If the stack is greater than MAX_HEIGHT loop through and remove pieces from the bottom until
        # stack is appropriate height. Add pieces to relevant players captured or reserved
        if stack.get_length() > MAX_HEIGHT:
            for piece in range(stack.get_length() - MAX_HEIGHT):
                removed_piece = stack.dequeue()
                if removed_piece == reserved_player.get_piece():
                    reserved_player.add_reserved()
                else:
                    reserved_player.add_captured()

    def check_position(self, row, column):
        """
        Returns true if a given position is within the game board, and false if it is not.

        row: an int representing the row of the position in question.
        column: an int representing the column of the position in question.
         """

        if row not in range(len(self.get_game_board())):
            return False
        elif column not in range(len(self.get_game_board())):
            return False
        else:
            return True

    def check_move(self, start_row, start_column, end_row, end_column, num_pieces):
        """ Checks that a move from the starting position is legal. Moves num_pieces, horizontally or vertically. """

        # Check horizontal move
        if start_row - end_row == 0 and abs(start_column - end_column) == num_pieces:
            return True

        # Check vertical move
        if start_column - end_column == 0 and abs(start_row - end_row) == num_pieces:
            return True

        return False


class Queue:
    """
    A queue class that will represent the stacks of pieces on the board. The bottom piece of the stack will be in
    index 0 with the topmost piece in the last index of the queue.

    This class won't directly interface with any other classes, but the Focus class will interface with Queue.
    """

    def __init__(self, first_member):
        """
        Creates a new queue, with first_member in index 0.

        first_member: can be any type
        """

        self.data = [first_member]

    def enqueue(self, value):
        """
        Adds value to the end of the queue.

        value: can be any type
        """

        self.data.append(value)

    def dequeue(self):
        """ Removes and returns the value at index 0 of the queue. """

        value = self.data[0]
        del self.data[0]
        return value

    def is_empty(self):
        """ Returns true if the queue is empty, false otherwise. """

        return len(self.data) == 0

    def display_top(self):
        """
        Returns the value at the end of the queue. In the case of this game that will be the game piece
        that is on "top" of the stack, or the piece that would be visible to the player's in a real Focus game.
        """

        return self.data[-1]

    def remove_items(self, num_pieces):
        """ Removes the given number of pieces from the end of the queue and returns a list of those pieces. """

        removed_pieces = self.data[-num_pieces:]
        self.data = self.data[:-num_pieces]

        return removed_pieces

    def add_items(self, pieces_to_add):
        """ Takes a list of pieces and adds them to the end of the queue. """

        self.data += pieces_to_add

    def get_data(self):
        """
        Returns a list that contains all values within the queue.
        """

        return self.data

    def get_length(self):
        """ Returns the length of the queue. """

        return len(self.data)


class Player:
    """
    A class to represent a player of the game. It will be responsible for keeping track of the player's
    name their piece choice and the number of reserve and captured pieces they have.

    Player will not directly interface with any other classes, but Focus will interface with Player.
    """

    def __init__(self, name, piece):
        """
        Creates a new player object with the given name and piece type.
        Initializes _name to the given string that represents the player's name
        Initializes _piece to the given string that represents the player's piece (R or G)
        Initializes _reserve to 0, this will be an int that keeps track of how many pieces the player has in reserve
        Initializes _captured to 0, this will be an int that keeps track of how many pieces the player has captured

        name: string that represents the player's name
        piece: string that represents the player's piece (R or G)
        """

        self._name = name
        self._piece = piece
        self._reserve = 0
        self._captured = 0

    def get_name(self):
        """ Returns the players name. """

        return self._name

    def get_piece(self):
        """ Returns the players piece. """

        return self._piece

    def get_reserved(self):
        """ Returns the number of pieces a player has in reserve"""

        return self._reserve

    def get_captured(self):
        """ Returns the number of pieces a player has captured. """

        return self._captured

    def add_captured(self):
        """ Adds a piece to the players captured pieces. """

        self._captured += 1

    def add_reserved(self):
        """ Adds a piece to the players reserved pieces. """

        self._reserve += 1

    def remove_reserved(self):
        """
        Removes a piece from the players reserved. Checks to make sure the reserve pieces are greater than
        0 before attempting to subtract one.
        """
        if self._reserve > 0:
            self._reserve -= 1
        else:
            self._reserve -= 0
