"""
Assignment 2: Trees for Treemap

=== CSC148 Summer 2024 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, David Liu, Diane Horton,
                   Haocheng Hu, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None

        self._expanded = False

        # 1. Initialize self._colour and self.data_size, according to the
        # docstring.
        # 2. Set this tree as the parent for each of its subtrees.
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        if self._subtrees == []:
            self.data_size = data_size
        else:
            self.data_size = sum(
                subt.data_size for subt in self._subtrees)

        for subtree in self._subtrees:
            subtree._parent_tree = self

        self.update_rectangles(self.rect)
        self.update_data_sizes()

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def get_parent(self) -> Optional[TMTree]:
        """Returns the parent of this tree.
        """
        return self._parent_tree

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.

        >>> t = TMTree("root", [], 10)
        >>> t.update_rectangles((0, 0, 100, 100))
        >>> t.rect
        (0, 0, 100, 100)

        >>> t1 = TMTree("file1", [], 4)
        >>> t2 = TMTree("file2", [], 6)
        >>> t = TMTree("root", [t1, t2], 10)
        >>> t.expand()
        >>> t.update_rectangles((0, 0, 100, 100))
        >>> t1.rect
        (0, 0, 100, 40)
        >>> t2.rect
        (0, 40, 100, 60)
        """
        # Read the handout carefully to help get started identifying base cases,
        # then write the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # elements of a rectangle, as follows.
        # x, y, width, height = rect
        x, y, width, height = rect

        # if the size is 0, the rectangle is empty (area 0)
        if self.data_size == 0:
            self.rect = (x, y, 0, 0)

        # if there is no subtrees, then the
        # rectangle is the entire given rectangle
        elif self._is_visible():
            self.rect = rect

        # if the width > height, create vertical rectangles for all the subtrees
        elif width > height:
            total_file_size = self.data_size

            previous_width = x

            for i in range(len(self._subtrees)):
                # if the subtree is the last one, then width is the
                # remaining space of the rectangle
                if i == len(self._subtrees) - 1:
                    width_of_subtree_rectangle = (x + width) - previous_width
                # otherwise, calculate how much size the sub-file takes of the
                # parent file and then calculate the width corresponding to that
                else:
                    percentage_of_total = self._subtrees[i].data_size / float(
                        total_file_size)
                    width_of_subtree_rectangle = int(
                        percentage_of_total * width)

                # set the rectangle for the subtree, then recurse,
                # then update the previous_width for the next subtree
                self._subtrees[i].rect = (
                    previous_width, y, width_of_subtree_rectangle, height)

                self._subtrees[i].update_rectangles(
                    (previous_width, y, width_of_subtree_rectangle, height))

                previous_width += width_of_subtree_rectangle

        else:
            total_file_size = self.data_size

            previous_height = y

            for i in range(len(self._subtrees)):
                # if the subtree is the last one, then height is the
                # remaining space of the rectangle
                if i == len(self._subtrees) - 1:
                    height_of_subtree_rectangle = (y + height) - previous_height
                # otherwise calculate how much size the sub-file takes of the
                # parent file, then calculate the height corresponding to that
                else:
                    percentage_of_total = self._subtrees[i].data_size / float(
                        total_file_size)
                    height_of_subtree_rectangle = int(
                        percentage_of_total * height)

                # set the rectangle for the subtree, then recurse,
                # then update the previous_height for the next subtree
                self._subtrees[i].rect = (
                    x, previous_height, width, height_of_subtree_rectangle)

                self._subtrees[i].update_rectangles(
                    (x, previous_height, width, height_of_subtree_rectangle))

                previous_height += height_of_subtree_rectangle

    def get_rectangles(self) -> List[
            Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        if self.is_empty() or self.data_size == 0:
            return []
        elif self._is_visible():
            return [(self.rect, self._colour)]
        else:
            all_rectangles = []

            for subtree in self._subtrees:
                all_rectangles.extend(subtree.get_rectangles())

            return all_rectangles

    def _is_visible(self) -> bool:
        """Return True if this tree is either a leaf or not expanded
         and all its ancestors are expanded."""
        if self._subtrees == [] or self._expanded is False:
            current = self._parent_tree
            while current is not None:
                if not current._expanded:
                    return False
                current = current._parent_tree
            return True
        return False

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """
        Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.
        """
        point_x, point_y = pos
        x, y, width, height = self.rect

        if (x <= point_x < x + width) and (
                y <= point_y < y + height) and self._is_visible():
            return self
        else:
            for subtree in self._subtrees:
                answer = subtree.get_tree_at_position(pos)
                if answer is not None:
                    return answer
        return None

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        if self._subtrees == []:
            return self.data_size
        else:
            new_size = 0
            for subtree in self._subtrees:
                new_size += subtree.update_data_sizes()

            self.data_size = new_size
            return new_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        # check if self is a leaf and destination is an internal node
        if self._subtrees == [] and destination._subtrees != []:
            current_parent = self._parent_tree

            # remove the leaf from its current parent's subtrees
            self._parent_tree._subtrees.remove(self)

            # check if this parent now has no subtrees,
            # as you have to update its data size then
            if self._parent_tree._subtrees == []:
                self._parent_tree.data_size = 0

            # add self to destination's subtree's
            destination._subtrees.append(self)
            self._parent_tree = destination

            # update the data_sizes and update_rectangles
            # of the original parent and all its parents
            while current_parent is not None:
                current_parent.update_data_sizes()
                current_parent.update_rectangles(current_parent.rect)
                current_parent = current_parent._parent_tree

            # update the data_sizes and update_rectangles
            # of the new parent and all its parents
            current_parent = destination
            while current_parent is not None:
                current_parent.update_data_sizes()
                current_parent.update_rectangles(current_parent.rect)
                current_parent = current_parent._parent_tree

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        if self._subtrees == []:
            amount_to_add = math.ceil(self.data_size * abs(factor))

            if factor >= 0:
                self.data_size += amount_to_add
            else:
                if self.data_size - amount_to_add < 1:
                    self.data_size = 1
                else:
                    self.data_size -= amount_to_add

        # update the sizes of all parent files
        current_parent = self._parent_tree

        while current_parent is not None:
            current_parent.update_data_sizes()
            current_parent.update_rectangles(current_parent.rect)
            current_parent = current_parent._parent_tree

    def delete_self(self) -> bool:
        """Removes the current node from the visualization and
        returns whether the deletion was successful.

        Only do this if this node has a parent tree.
        """
        # check if self has a parent
        if self._parent_tree is not None:
            current_parent = self._parent_tree

            # remove self from the parent's subtrees
            self._parent_tree._subtrees.remove(self)

            # if the parent now has no subtrees, set its data_size to 0
            if self._parent_tree._subtrees == []:
                current_parent.data_size = 0

            # update the data_sizes and rectangle
            # sizes of old parent, and all it's parents
            while current_parent is not None:
                current_parent.update_data_sizes()
                current_parent.update_rectangles(current_parent.rect)
                current_parent = current_parent._parent_tree

            return True

        else:
            return False

    def expand(self) -> None:
        """Expand this node in the displayed-tree,
        if it is not already expanded, revealing all its contents."""
        if self._subtrees == []:
            pass
        else:
            self._expanded = True
            # Update rectangles from self
            self.update_rectangles(self.rect)

    def expand_all(self) -> None:
        """ expand all the trees in the data_tree"""
        self.expand()
        for subtree in self._subtrees:
            subtree.expand_all()

    def collapse(self) -> None:
        """ collapse this tree in the display tree, revealing
        the parent tree instead"""
        if self._parent_tree is None:
            pass
        else:
            # get the parent tree
            parent = self._parent_tree

            # call the helper function to collapse all the parents subtrees
            parent._collapse_helper()

    def _collapse_helper(self) -> None:
        self._expanded = False

        for subtree in self._subtrees:
            subtree._collapse_helper()

    def collapse_all(self) -> None:
        """ collapse the whole display tree showing only the root now"""

        # get the overall root of the tree
        current_parent = self

        while current_parent._parent_tree is not None:
            current_parent = current_parent._parent_tree

        # call helper to collapse the root, and all subtrees
        current_parent._collapse_all_helper()

    def _collapse_all_helper(self) -> None:
        self.collapse()

        for subtree in self._subtrees:
            subtree._collapse_all_helper()

    # Methods for the string representation
    def get_path_string(self) -> str:
        """
        Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                self.get_separator() + self._name

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.

        >>> import os
        >>> tree = FileSystemTree(os.path.join('example-directory', 'workshop'))
        >>> tree._name
        'workshop'
        >>> tree.data_size
        151
        >>> len(tree._subtrees) > 0
        True

        >>> tree = FileSystemTree(os.path.join('example-directory', 'workshop', 'activities'))
        >>> tree._name
        'activities'
        >>> tree.data_size
        71

        >>> tree = FileSystemTree(os.path.join('example-directory', 'workshop', 'activities', 'images', 'Q2.pdf'))
        >>> tree._name
        'Q2.pdf'
        >>> tree.data_size
        20
        >>> len(tree._subtrees) == 0
        True
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!
        file_name = os.path.basename(path)
        subtrees = []
        data_size = 0

        if os.path.isdir(path):
            for inner_file in os.listdir(path):
                inner_file_path = os.path.join(path, inner_file)
                subtree = FileSystemTree(inner_file_path)
                subtrees.append(subtree)
                data_size += subtree.data_size
        else:
            data_size = os.path.getsize(path)

        TMTree.__init__(self, file_name, subtrees, data_size)

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
