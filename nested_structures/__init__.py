# coding: utf-8
from collections import OrderedDict


class Node(object):
    def __init__(self, item, children):
        self.item = item
        self.children = children

    def __getitem__(self, i):
        return self.children[i].item

    def __iter__(self):
        for k, c in self.children.iteritems():
            yield k, c

    def __len__(self):
        if self.children:
            return len(self.children)
        else:
            return 0


'''
Nested nodes
============

We define a "nested nodes" structure as a list of entries, where each entry is
one of the following:

 - A `tuple` containing two values:
  * A `key` of any type.
  * A `list` containing entries.
 - A `key` of any type.

For example, consider the following structure:

    >>> pprint(menu_actions)
    [('File',
      ['Load', 'Save', ('Quit', ['Quit without saving', 'Save and quit'])]),
     ('Edit', ['Copy', 'Paste', ('Fill', ['Down', 'Series'])])]

Here, we have a nested structure representing an application menu layout.  The
first entry contains the key `"File"` and several child entries.  The first two
child entries of `"File"` *(i.e., `"Save"` and `"Load"`)* consist only of a
*key*, whereas the third child entry, `"Quit"`, is a tuple containing both a
*key* and a `list` of child entries.
'''


def apply_depth_first(nodes, func, as_dict=False, parents=None):
    '''
    Given a structure such as the application menu layout described above, we
    may want to apply an operation to each entry to create a transformed
    version of the structure.

    For example, let's convert all entries in the application menu layout from
    above to upper-case:

    >>> pprint(apply_depth_first(menu_actions, lambda node, parents, nodes: node.upper()))
    [('FILE',
      ['LOAD', 'SAVE', ('QUIT', ['QUIT WITHOUT SAVING', 'SAVE AND QUIT'])]),
     ('EDIT', ['COPY', 'PASTE', ('FILL', ['DOWN', 'SERIES'])])]

    Here we used the `apply_depth_first` function to apply a `lambda` function
    to each entry to compute the upper-case value corresponding to each node/key.


    `as_dict`
    ---------

    To make traversing the structure easier, the output may be expressed as a
    nested `OrderedDict` structure.  For instance, let's apply the upper-case
    transformation from above, but this time with `as_dict=True`:

    >>> result = apply_depth_first(menu_actions, as_dict=True, \
    ...                            func=lambda node, parents, nodes: node.upper())

    >>> type(result)
    <class 'collections.OrderedDict'>

    Here we see that the result is an ordered dictionary.  Moreover, we can
    look up the transformed `"File"` entry based on the original key/node
    value.  Since an entry may contain children, each entry is wrapped as a
    `namedtuple` with `item` and `children` attributes.

    >>> type(result['File'])
    <class 'nested_structures.Node'>
    >>> result['File'].item
    'FILE'
    >>> type(result['File'].children)
    <class 'collections.OrderedDict'>

    If an entry has children, the `children` attribute is an `OrderedDict`.
    Otherwise, the `children` is set to `None`.

    Given the information from above, we can look up the `"Load"` child entry
    of the `"File"` entry.

    >>> result['File'].children['Load']
    Node(item='LOAD', children=None)

    Similarly, we can look up the `"Save and quit"` child entry of the `"Quit"`
    entry.

    >>> result['File'].children['Quit'].children['Save and quit']
    Node(item='SAVE AND QUIT', children=None)

    Note that this function *(i.e., `apply_depth_first`)* could be used to,
    e.g., create a menu GUI item for each entry in the structure.  This would
    decouple the description of the layout from the GUI framework used.
    '''
    if as_dict:
        items = OrderedDict()
    else:
        items = []

    if parents is None:
        parents = []

    for i, node in enumerate(nodes):
        if isinstance(node, tuple):
            node, nodes = node
        else:
            nodes = []

        item = func(node, parents, nodes)
        item_parents = parents + [node]
        if nodes:
            children = apply_depth_first(nodes, func,
                                         as_dict=as_dict,
                                         parents=item_parents)
        else:
            children = None

        if as_dict:
            items[node] = Node(item, children)
        elif nodes:
            items.append((item, children))
        else:
            items.append(item)
    return items


def apply_dict_depth_first(nodes, func, as_dict=True, parents=None):
    '''
    This function is similar to the `apply_depth_first` except that it operates
    on the `OrderedDict`-based structure returned from `apply_depth_first` when
    `as_dict=True`.

    Note that if `as_dict` is `False`, the result of this function is given in
    the entry/tuple form.
    '''
    if as_dict:
        items = OrderedDict()
    else:
        items = []

    if parents is None:
        parents = []

    for i, (k, node) in enumerate(nodes.iteritems()):
        item = func(k, node, parents)
        item_parents = parents + [(k, node)]
        if node.children is not None:
            children = apply_dict_depth_first(node.children, func,
                                              as_dict=as_dict,
                                              parents=item_parents)
        else:
            children = None
        if as_dict:
            items[k] = Node(item, children)
        elif children:
            items.append((item, children))
        else:
            items.append(item)
    return items


def collect(nested_nodes, transform=None):
    '''
    Return list containing the result of the `transform` function applied to
    each item in the supplied list of nested nodes.

    A custom transform function may be applied to each entry during the
    flattening by specifying a function through the `transform` keyword
    argument.  The `transform` function will be passed the following arguments:

     - `node`: The node/key of the entry.
     - `parents`: The node/key of the parents as a `list`.
     - `nodes`: The children of the entry.

    By default, the `transform` function simply returns the node/key, resulting
    in a flattened version of the original nested nodes structure.
    '''
    items = []

    if transform is None:
        transform = lambda node, parents, nodes: node

    def __collect__(node, parents, nodes):
        items.append(transform(node, parents, nodes))

    apply_depth_first(nested_nodes, __collect__)
    return items


def dict_collect(nodes, transform=None):
    items = []

    if transform is None:
        transform = lambda *args: tuple(args)

    def __collect__(key, node, parents):
        items.append(transform(key, node, parents))

    apply_dict_depth_first(nodes, __collect__)
    return items
