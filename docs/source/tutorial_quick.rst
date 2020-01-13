Jericho Quick-start
===================

Install
-------

Jericho requires Linux, Python 3, and basic build tools like gcc.

There are two ways to install Jericho:

From PyPi
.........

.. code-block:: bash

   pip3 install --user jericho


From Github
...........

1. Clone Jericho Repository:

.. code-block:: bash

    git clone https://github.com/microsoft/jericho.git ~/jericho

2. Install Jericho:

.. code-block:: bash

    cd ~/jericho; pip3 install --user .


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
                env = FrotzEnv("z-machine-games-master/jericho-game-suite/zork1.z5", seed=12)
                initial_observation = env.reset()
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

It's possible to get the list of vocabulary words recognized by a game:

.. code-block:: python

                print('Recognized Vocabulary Words', list(env.get_dictionary()))

Note that most games recognize words up to a fixed length of 6 or 9 characters, so truncated words like 'northe' are functionally equivalent to 'northeast.' For more information see :doc:`dictionary`.


Loading and Saving
------------------

It's possible to save and load the game state using the following methods:

.. code-block:: python

                game_state = env.get_state()
                env.set_state(game_state)


Change Detection
----------------

Since many actions may not be recognized by the game's parser, Jericho provides a best-guess facility to determine if the last action changed the state of the game:

.. code-block:: python

                env.step('take leaflet')
                if env.world_changed():
                    print('Found a valid action!')


Object Tree
-----------

The object tree is an internal representation of game state. Jericho provides functions to access all or parts of this tree. For more information see :doc:`object_tree`.

.. code-block:: python

                all_objects = env.get_world_objects()
                print('Me:', env.get_player_object())
                print('My Inventory:', env.get_inventory())
                print('My Current Location:', env.get_player_location())


Finding Valid Actions
---------------------

One of the most common difficulties with parser-based text games is identifying which actions are recognized by the parser and applicable in the current location. Jericho provides a facility to best-guess identify a list of *valid-actions* that will have an effect on the current game state.

Pairing the :class:`jericho.template_action_generator.TemplateActionGenerator` with :meth:`jericho.FrotzEnv.find_valid_actions`, it's possible to identify valid actions as follows:


.. code-block:: python

                >>> from jericho import *
                >>> from jericho.template_action_generator import TemplateActionGenerator
                >>> rom = 'zork1.z5'
                >>> env = FrotzEnv(rom)
                >>> bindings = load_bindings(rom)
                >>> act_gen = TemplateActionGenerator(bindings)
                >>> env.reset()
                'You are standing in an open field west of a white house, with a boarded front door. There is a small mailbox here.'
                >>> interactive_objs = [obj[0] for obj in env.identify_interactive_objects(use_object_tree=True)]
                ['mailbox', 'boarded', 'white']
                >>> candidate_actions = act_gen.generate_actions(interactive_objs)
                ['drive boarded', 'swim in mailbox', 'jump white', 'kick boarded','pour white in boarded', ... ]
                >>> valid_actions = env.find_valid_actions(candidate_actions)
                ['south', 'open mailbox', 'west', 'north']
