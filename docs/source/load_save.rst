Loading and Saving
==================

Jericho provides the facility to load and save games either to strings or files. However, there are points in games where it's not possible to save. Notably, when the game is asking the player a question it will dissallow saving until the question is answered. An example of this is when the game is over, the interpreter will commonly ask whether you want to RESTART, RESTORE a saved game, or QUIT? If a save is attempted at this point, Jericho will throw a `RuntimeError` as the interpreter prohibits saving until the question is answered or the environment is reset.

We recommend using taking measures to handle possible errors when saving or loading:

.. code-block:: python

                try:
                    save = env.save_str()
                except RuntimeError:
                    print('Skipping Save')
