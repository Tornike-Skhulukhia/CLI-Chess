import unittest

from _move_related_functions import (
    _is_chess_cell_coord,
    _is_chess_basic_move_str,
    _is_chess_notation_move_str,
)


class TestIsChessCellCoord(unittest.TestCase):
    def test_is_chess_cell_coord(self):
        for i in ["E1", "E2", "D1", "H3", "B6", "B7", "B8", "F5"]:
            self.assertTrue(_is_chess_cell_coord(i))

    def test_is_not_chess_cell_coord(self):
        for i in ["A9", "B0", "CC", "33", "", "F0", "D-1", "H22", "7", "A"]:
            self.assertFalse(_is_chess_cell_coord(i))


class TestIsChessBasicMoveStr(unittest.TestCase):
    def test_is_chess_basic_move_str(self):
        for i in [
            "E2 E4",
            "C1 E3",
            "A8 A1",
            "B1 C6",
            "O-O",
            "O-O-O",
            "E7 E8=N",
            "E7 E8=Q",
            "C7 C8=R",
        ]:
            self.assertTrue(_is_chess_basic_move_str(i))

    def test_is_not_chess_basic_move_str(self):
        for i in ["e2 e2", "B1 C9", "B0 B7", "O", "OO", "", "E7 E8=QM", "C7 C8=Rx"]:
            self.assertFalse(_is_chess_basic_move_str(i))


class TestIsChessNotationMoveStr(unittest.TestCase):
    def test_is_chess_notation_move_str(self):
        for i in [
            "e3",
            "d7",
            "Bf3",
            "Nb4",
            "Re8",
            "Qxe6+",
            "Qexe6+",
            "Q3xe6+",
            "Qe3xe6+",
        ]:
            self.assertTrue(_is_chess_notation_move_str(i))

    def test_is_not_chess_notation_move_str(self):
        for i in ["R e8", "QxE6+", "xNe4", "e4Nx", "A9", "a0", "b11", "00", "000"]:
            self.assertFalse(_is_chess_notation_move_str(i))


if __name__ == "__main__":
    unittest.main()
