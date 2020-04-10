Jericho Quick-start
===================

Install
-------

Jericho requires Linux, Python 3, Spacy, and basic build tools like gcc.

There are two ways to install Jericho:

From PyPi
.........

.. code-block:: bash

   pip3 install jericho
   python3 -m spacy download en_core_web_sm


From Github
...........

1. Clone Jericho Repository:

.. code-block:: bash

   git clone https://github.com/microsoft/jericho.git

2. Install Jericho:

.. code-block:: bash

   cd jericho; pip3 install .
   python3 -m spacy download en_core_web_sm


Acquire Games
-------------

An archive of games can be downloaded as follows:

.. code-block:: bash

   wget https://github.com/BYU-PCCL/z-machine-games/archive/master.zip
   unzip master.zip

Jericho-supported games may be found in the ``jericho-game-suite`` subdirectory.


Basic Usage
-----------

Jericho implements a reinforcement learning interface in which the agent provides string-based actions, and the environment responds with string-based observations, rewards, and termination status:

.. code-block:: python

                from jericho import *
                # Create the environment, optionally specifying a random seed
                env = FrotzEnv("z-machine-games-master/jericho-game-suite/zork1.z5")
                initial_observation, info = env.reset()
                done = False
                while not done:
                    # Take an action in the environment using the step fuction.
                    # The resulting text-observation, reward, and game-over indicator is returned.
                    observation, reward, done, info = env.step('open mailbox')
                    # Total score and move-count are returned in the info dictionary
                    print('Total Score', info['score'], 'Moves', info['moves'])
                print('Scored', info['score'], 'out of', env.get_max_score())


Game Dictionary
---------------

:meth:`jericho.FrotzEnv.get_dictionary` returns the list of vocabulary words recognized by a game:

.. code-block:: python

                print('Recognized Vocabulary Words', list(env.get_dictionary()))

Note that most games recognize words up to a fixed length of 6 or 9 characters, so truncated words like 'northe' are functionally equivalent to 'northeast.' For more information see :doc:`dictionary`.


Loading and Saving
------------------

It's possible to save and load the game state using :meth:`jericho.FrotzEnv.get_state` and :meth:`jericho.FrotzEnv.set_state`:

.. code-block:: python

                from jericho import *
                env = FrotzEnv(rom_path)
                state = env.get_state() # Save the game to state
                env.step('attack troll') # Oops!
                'You swing and miss. The troll neatly removes your head.'
                env.set_state(state) # Restore to saved state


Object Tree
-----------

The object tree is an internal representation of game state. Jericho provides functions to access all or parts of this tree. For more information see :doc:`object_tree`.

.. code-block:: python

                all_objects = env.get_world_objects()
                print('Me:', env.get_player_object())
                print('My Inventory:', env.get_inventory())
                print('My Current Location:', env.get_player_location())


Getting Valid Actions
---------------------

One of the most common difficulties with parser-based text games is identifying which actions are recognized by the parser and applicable in the current location. Jericho's :meth:`jericho.FrotzEnv.get_valid_actions` provides a best-guess list of *valid-actions* that will have an effect on the current game state:


.. code-block:: python

                >>> from jericho import *
                >>> env = FrotzEnv("z-machine-games-master/jericho-game-suite/zork1.z5")
                >>> env.reset()
                'You are standing in an open field west of a white house, with a boarded front door. There is a small mailbox here.'
                >>> valid_actions = env.get_valid_actions()
                ['south', 'open mailbox', 'west', 'north']


Walkthroughs
------------

Jericho provides walkthroughs for supported games using :meth:`jericho.FrotzEnv.get_walkthrough`. To use the walkthrough, it is necessary to reset the environment with the desired seed:

.. code-block:: python

                >>> from jericho import *
                >>> env = FrotzEnv("z-machine-games-master/jericho-game-suite/zork1.z5")
                >>> walkthrough = env.get_walkthrough()
                >>> for act in walkthrough:
                >>>     env.step(act)
