"""
Assignment 2 - Sample Tests

=== CSC148 Summer 2024 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains sample tests for Assignment 2, Tasks 1 and 2.
The tests use the provided example-directory, so make sure you have downloaded
and extracted it into the same place as this test file.
This test suite is very small. You should plan to add to it significantly to
thoroughly test your code.

IMPORTANT NOTES:
    - If using PyCharm, go into your Settings window, and go to
      Editor -> General.
      Make sure the "Ensure line feed at file end on Save" is NOT checked.
      Then, make sure none of the example files have a blank line at the end.
      (If they do, the data size will be off.)

    - os.listdir behaves differently on different
      operating systems.  These tests expect the outcomes that one gets
      when running on the *Teaching Lab machines*.
      Please run all of your tests there - otherwise,
      you might get inaccurate test failures!

    - Depending on your operating system or other system settings, you
      may end up with other files in your example-directory that will cause
      inaccurate test failures. That will not happen on the Teachin Lab
      machines.  This is a second reason why you should run this test module
      there.
"""
import os

from hypothesis import given
from hypothesis.strategies import integers

from tm_trees import TMTree, FileSystemTree

# This should be the path to the "workshop" folder in the sample data.
# You may need to modify this, depending on where you downloaded and
# extracted the files.
EXAMPLE_PATH = os.path.join(os.getcwd(), 'example-directory', 'workshop')


def test_single_file() -> None:
    """Test a tree with a single file.
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    assert tree._name == 'draft.pptx'
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 58
    assert is_valid_colour(tree._colour)


def test_example_data() -> None:
    """Test the root of the tree at the 'workshop' folder in the example data
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    assert tree._name == 'workshop'
    assert tree._parent_tree is None
    assert tree.data_size == 151
    assert is_valid_colour(tree._colour)

    assert len(tree._subtrees) == 3
    for subtree in tree._subtrees:
        # Note the use of is rather than ==.
        # This checks ids rather than values.
        assert subtree._parent_tree is tree


def test_file_structure():
    tree = FileSystemTree(EXAMPLE_PATH)
    assert tree._name == 'workshop'
    subfolder = tree._subtrees[0]
    assert subfolder._name == 'activities'
    assert len(subfolder._subtrees) > 0
    sub_subfolder1 = subfolder._subtrees[0]
    assert sub_subfolder1._name == 'images'
    sub_subfolder2 = subfolder._subtrees[1]
    assert sub_subfolder2._name == 'Plan.tex'
    assert sub_subfolder2.get_parent()._name == 'activities'


@given(integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000))
def test_single_file_rectangles(x, y, width, height) -> None:
    """Test that the correct rectangle is produced for a single file."""
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.update_rectangles((x, y, width, height))
    rects = tree.get_rectangles()

    # This should be just a single rectangle and colour returned.
    assert len(rects) == 1
    rect, colour = rects[0]
    assert rect == (x, y, width, height)
    assert is_valid_colour(colour)


def test_example_data_rectangles() -> None:
    """This test sorts the subtrees, because different operating systems have
    different behaviours with os.listdir.

    You should *NOT* do any sorting in your own code
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    tree.update_rectangles((0, 0, 200, 100))
    tree.expand_all()
    rects = tree.get_rectangles()

    # IMPORTANT: This test should pass when you have completed Task 2, but
    # will fail once you have completed Task 5.
    # You should edit it as you make progress through the tasks,
    # and add further tests for the later task functionality.
    assert len(rects) == 6

    # UPDATED:
    # Here, we illustrate the correct order of the returned rectangles.
    # Note that this corresponds to the folder contents always being
    # sorted in alphabetical order. This is enforced in these sample tests
    # only so that you can run them on your own computer, rather than on
    # the Teaching Labs.
    actual_rects = [r[0] for r in rects]
    expected_rects = [(0, 0, 94, 2), (0, 2, 94, 28), (0, 30, 94, 70),
                      (94, 0, 76, 100), (170, 0, 30, 72), (170, 72, 30, 28)]

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


def test_update_rectangles_decimals_vertical():
    t1 = TMTree("leaf1", [], 3)
    t2 = TMTree("leaf2", [], 7)
    t = TMTree("root", [t1, t2], 10)
    t.update_rectangles((0, 0, 100, 50))
    t.expand_all()
    assert t1.rect == (0, 0, 30, 50)
    assert t2.rect == (30, 0, 70, 50)

    t1 = TMTree("leaf1", [], 13)
    t2 = TMTree("leaf2", [], 17)
    t = TMTree("root", [t1, t2], 30)
    t.expand_all()
    t.update_rectangles((0, 0, 90, 70))
    assert t1.rect == (0, 0, 39, 70)
    assert t2.rect == (39, 0, 51, 70)


def test_update_rectangles_decimals_horizontal():
    t1 = TMTree("leaf1", [], 25)
    t2 = TMTree("leaf2", [], 35)
    t3 = TMTree("leaf3", [], 40)
    t = TMTree("root", [t1, t2, t3], 100)
    t.update_rectangles((0, 0, 50, 150))
    t.expand_all()
    assert t1.rect == (0, 0, 50, 37)
    assert t2.rect == (0, 37, 50, 52)
    assert t3.rect == (0, 89, 50, 61)


def test_get_tree_at_position_complex():
    t1 = TMTree("leaf1", [], 25)
    t2 = TMTree("leaf2", [], 35)
    t3 = TMTree("leaf3", [], 40)
    t = TMTree("root", [t1, t2, t3], 100)
    t.update_rectangles((0, 0, 50, 150))
    t.expand_all()

    assert t.get_tree_at_position((25, 19))._name == 'leaf1'
    assert t.get_tree_at_position((25, 36))._name == 'leaf1'
    assert t.get_tree_at_position((25, 37))._name == 'leaf2'
    assert t.get_tree_at_position((25, 45))._name == 'leaf2'
    assert t.get_tree_at_position((25, 120))._name == 'leaf3'
    assert t.get_tree_at_position((60, 25)) is None
    assert t.get_tree_at_position((25, 150)) is None


def test_change_size():
    t1 = TMTree("leaf1", [], 100)
    t = TMTree("root", [t1], 100)
    t1.change_size(0.01)
    assert t1.data_size == 101
    t1.change_size(1.5)
    assert t1.data_size == 253
    t1.change_size(-0.01)
    assert t1.data_size == 250


def test_update_data_sizes():
    t6 = TMTree("leaf3", [], 100)
    t5 = TMTree("leaf2", [], 100)
    t4 = TMTree("leaf1", [], 100)

    t3 = TMTree("middle2", [t6], 100)
    t2 = TMTree("middle1", [t4, t5], 100)

    t1 = TMTree("root", [t2, t3], 100)

    assert t1.data_size == 300
    assert t2.data_size == 200
    assert t4.data_size == 100

    t6.change_size(0.01)
    assert t3.data_size == 101
    assert t1.data_size == 301

    t4.change_size(0.015)
    assert t2.data_size == 202
    assert t1.data_size == 303
    assert t6.data_size == 101


def test_move():
    t6 = TMTree("leaf3", [], 100)
    t5 = TMTree("leaf2", [], 100)
    t4 = TMTree("leaf1", [], 100)
    t3 = TMTree("middle2", [t6], 100)
    t2 = TMTree("middle1", [t4, t5], 100)
    t1 = TMTree("root", [t2, t3], 100)

    assert t6.get_parent() == t3
    assert len(t3._subtrees) == 1
    t6.move(t2)
    assert len(t2._subtrees) == 3

    names = []
    for item in t2._subtrees:
        names.append(item._name)
    assert names == ['leaf1', 'leaf2', 'leaf3']

    assert t2._subtrees[-1] == t6
    assert t3._subtrees == []
    assert t2.data_size == 300
    assert t3.data_size == 0


def test_move_to_non_leaf():
    t1 = TMTree("leaf1", [], 10)
    t2 = TMTree("leaf2", [], 10)
    t = TMTree("root", [t1, t2])
    t1.move(t2)

    assert len(t._subtrees) == 2
    assert len(t2._subtrees) == 0
    assert t._subtrees[0] == t1


def test_delete_self():
    t6 = TMTree("leaf3", [], 100)
    t5 = TMTree("leaf2", [], 100)
    t4 = TMTree("leaf1", [], 100)
    t3 = TMTree("middle2", [t6], 100)
    t2 = TMTree("middle1", [t4, t5], 100)
    t1 = TMTree("root", [t2, t3], 100)

    t3.delete_self()
    assert t1._subtrees == [t2]
    assert t1.data_size == 200

    t5.delete_self()
    assert t2._subtrees == [t4]
    assert t1.data_size == 100

    t2.delete_self()
    assert t1._subtrees == []
    assert t1.data_size == 0


def test_expand_all():
    # Create a sample tree
    t6 = TMTree("leaf3", [], 100)
    t5 = TMTree("leaf2", [], 100)
    t4 = TMTree("leaf1", [], 100)
    t3 = TMTree("middle2", [t6], 100)
    t2 = TMTree("middle1", [t4, t5], 100)
    t1 = TMTree("root", [t2, t3], 100)

    # Initially, only the root should be expanded
    assert not t2._expanded
    assert not t3._expanded
    assert not t4._expanded
    assert not t5._expanded
    assert not t6._expanded

    # Expand all nodes
    t1.expand_all()

    assert t1._expanded
    # Now, all nodes should be expanded
    assert t2._expanded
    assert t3._expanded
    # assert t4._expanded
    # assert t5._expanded
    # assert t6._expanded


##############################################################################
# Helpers
##############################################################################


def is_valid_colour(colour: tuple[int, int, int]) -> bool:
    """Return True iff <colour> is a valid colour. That is, if all of its
    values are between 0 and 255, inclusive.
    """
    for i in range(3):
        if not 0 <= colour[i] <= 255:
            return False
    return True


def _sort_subtrees(tree: TMTree) -> None:
    """Sort the subtrees of <tree> in alphabetical order.
    THIS IS FOR THE PURPOSES OF THE SAMPLE TEST ONLY; YOU SHOULD NOT SORT
    YOUR SUBTREES IN THIS WAY. This allows the sample test to run on different
    operating systems.

    This is recursive, and affects all levels of the tree.
    """
    if not tree.is_empty():
        for subtree in tree._subtrees:
            _sort_subtrees(subtree)

        tree._subtrees.sort(key=lambda t: t._name)


if __name__ == '__main__':
    import pytest

    pytest.main(['a2_sample_test.py'])
