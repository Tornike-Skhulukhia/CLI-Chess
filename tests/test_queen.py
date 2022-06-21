import unittest

from tests.base import BaseTest


class TestQueen(BaseTest):
    def test_can_move_properly(self):
        ### white
        # invalid
        self._assert_was_not_successful_move("d1 f3")
        # valid
        self._assert_was_successful_move("e2 e4")

        ### black
        # invalid
        self._assert_was_not_successful_move("d8 a5")
        # valid
        self._assert_was_successful_move("e7 e5")

        ### white
        self._assert_was_successful_move("d1 h5")

        # black
        self._assert_was_successful_move("d8 e7")

        ### white | kills pawn near king with check
        self._assert_was_successful_move("h5 f7")

        ### black | can not move something else if check still remains
        self._assert_was_not_successful_move("b8 c6")
        self._assert_was_not_successful_move("f8 b4")
        # but can kill piece that gives check
        self._assert_was_successful_move("e7 f7")


if __name__ == "__main__":
    unittest.main()
