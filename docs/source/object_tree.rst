Object Tree
===========

The Object Tree is an internal representation of all locations and objects present in a Z-machine game, including the player and their inventory.

Each object has *parent*, *child*, and *sibling* object. Parent objects typically contain the child objects. For example if we have a parent object *Treasure Chest*, it may contain a child object *Cutlass* that has a sibling object *Eye Patch*. And the treasure chest may have a parent object *Sandy Beach* corresponding to the location of the chest. If and when the player reaches the Sandy Beach, the object tree will be rearranged so that the player-object's sibling will become the Treasure Chest.

Objects additionally have attributes which are set and unset to keep track of the state of an object. For example a *window* can either be in the open or closed position; this is tracked through its attributes.
Finally, the *properties* of an object are numerical values that determine how the object may be interacted with.

For a great tutorial on the Object Tree, see `Z-Machine Standards <https://inform-fiction.org/zmachine/standards/z1point1/overview.html>`_.

In Jericho, the full object tree can be accessed with :meth:`jericho.FrotzEnv.get_world_objects`. Jericho also provides shortcuts to particular objects of interest such as the player :meth:`jericho.FrotzEnv.get_player_object`, the player's location :meth:`jericho.FrotzEnv.get_player_location`, and the player's inventory :meth:`jericho.FrotzEnv.get_inventory`.

ZObject
-------

Jericho's ZObject is a ctypes structure that providing access to the name, parent, sibling, child, attributes, and properties of an object.

.. autoclass:: jericho.ZObject
  :members:
