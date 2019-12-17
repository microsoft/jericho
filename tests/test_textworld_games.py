import os
from os.path import join as pjoin
import textwrap

import jericho


DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))


def test_loading_a_textworld_game():
    env = jericho.FrotzEnv(pjoin(DATA_PATH, "tw-game.z8"))
    state, info = env.reset()

    assert not env.victory()
    assert not env.game_over()
    assert env.get_score() == 0
    assert env.get_max_score() == 3

    state, reward, done, info = env.step("go east")
    assert not done
    assert reward == 0

    state, reward, done, info = env.step("insert carrot into chest")
    assert not done
    assert reward == 2

    state, reward, done, info = env.step("close chest")
    assert done
    assert env.victory()
    assert reward == 1
    assert info['score'] == 3

    state = env.reset()
    state, reward, done, info = env.step("eat carrot")
    assert done
    assert env.game_over()  # Lost
    assert info['score'] == 0


def test_cleaning_observation():
    gamefile = "tw-cooking-recipe3+cook+cut-2057SPdQu0mWiv0k.z8"
    env = jericho.FrotzEnv(pjoin(DATA_PATH, gamefile))
    state, info = env.reset()

    EXPECTED = textwrap.dedent(
    r"""


                        ________  ________  __    __  ________
                       |        \|        \|  \  |  \|        \
                        \$$$$$$$$| $$$$$$$$| $$  | $$ \$$$$$$$$
                          | $$   | $$__     \$$\/  $$   | $$
                          | $$   | $$  \     >$$  $$    | $$
                          | $$   | $$$$$    /  $$$$\    | $$
                          | $$   | $$_____ |  $$ \$$\   | $$
                          | $$   | $$     \| $$  | $$   | $$
                           \$$    \$$$$$$$$ \$$   \$$    \$$
                  __       __   ______   _______   __        _______
                 |  \  _  |  \ /      \ |       \ |  \      |       \
                 | $$ / \ | $$|  $$$$$$\| $$$$$$$\| $$      | $$$$$$$\
                 | $$/  $\| $$| $$  | $$| $$__| $$| $$      | $$  | $$
                 | $$  $$$\ $$| $$  | $$| $$    $$| $$      | $$  | $$
                 | $$ $$\$$\$$| $$  | $$| $$$$$$$\| $$      | $$  | $$
                 | $$$$  \$$$$| $$__/ $$| $$  | $$| $$_____ | $$__/ $$
                 | $$$    \$$$ \$$    $$| $$  | $$| $$     \| $$    $$
                  \$$      \$$  \$$$$$$  \$$   \$$ \$$$$$$$$ \$$$$$$$

    You are hungry! Let's cook a delicious meal. Check the cookbook in the kitchen for the recipe. Once done, enjoy your meal!

    -= Kitchen =-
    You arrive in a kitchen. An ordinary kind of place. The room seems oddly familiar, as though it were only superficially different from the other rooms in the building.

    You lean against the wall, inadvertently pressing a secret button. The wall opens up to reveal a fridge. The fridge is empty, what a horrible day! You make out a closed oven. You lean against the wall, inadvertently pressing a secret button. The wall opens up to reveal a table. You see a cookbook on the table. Now that's what I call TextWorld! What's that over there? It looks like it's a counter. You see a red apple and a knife on the counter. You make out a stove. But the thing hasn't got anything on it.


    """)
    assert [line.strip() for line in state.split("\n")] == [line.strip() for line in EXPECTED.split("\n")]
