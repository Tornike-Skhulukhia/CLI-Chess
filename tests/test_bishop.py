import unittest

from tests.base import BaseTest


class TestBishop(BaseTest):
    def test_can_not_fly_over_piece(self):
        # white tries to play bishop before opening with pawn
        self._assert_was_not_successful_move("c1 a3")
        self._assert_was_successful_move("b2 b4")

        # black moves
        self._assert_was_successful_move("d7 d5")

        # now it works
        self._assert_was_successful_move("c1 a3")


if __name__ == "__main__":
    unittest.main()
