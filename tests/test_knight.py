import unittest

from tests.base import BaseTest


class TestKnight(BaseTest):
    def test_can_move_properly(self):
        ### white
        # invalid
        self._assert_was_not_successful_move("b1 d3")
        # valid
        self._assert_was_successful_move("b1 c3")

        ### black
        # invalid
        self._assert_was_not_successful_move("g8 h7")
        # valid
        self._assert_was_successful_move("g8 f6")

        # white
        self._assert_was_successful_move("c3 d5")

        # black
        self._assert_was_successful_move("f6 d5")


if __name__ == "__main__":
    unittest.main()
