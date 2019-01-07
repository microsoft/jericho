# Jericho :ghost: [![Build Status](https://travis-ci.org/Microsoft/jericho.svg?branch=master)](https://travis-ci.org/Microsoft/jericho) [![PyPI version](https://badge.fury.io/py/jericho.svg)](https://badge.fury.io/py/jericho)
**Jericho is an environment that connects learning agents with interactive fiction games.** Jericho uses [Frotz](http://frotz.sourceforge.net/) and [Ztools](http://inform-fiction.org/zmachine/ztools.html) to provide a fast, python-based interface to Z-machine games.

## Requirements
***Linux***, ***Python 3***, and basic build tools like ***gcc***.

## Install
```bash
pip3 install --user jericho
```

## Usage
```python
from jericho import *
env = FrotzEnv("roms/zork1.z5", seed=12)
# Take an action in the environment using the step() fuction.
# The resulting text observation and game score is returned.
observation, score, done, info = env.step('open mailbox')
# Reset the game to start anew
env.reset()
# Game have different max scores
env.get_max_score()
# Saving the game is possible with save_str()
saved_game = env.save_str()
# Loading is just as easy
env.load_str(saved_game)

# Jericho supports visibilty into the game including viewing the RAM
env.get_ram()
# And the object tree
env.get_world_objects()
# As well as shortcuts for particular objects, such as the player
env.get_player_object()
# And their inventory
env.get_inventory()
# Or their location
env.get_player_location()

# It's also possible to teleport the player to a location
env.teleport_player(123)
# Or to teleport an object to the player
env.teleport_obj_to_player(164)
# Be careful with these methods as they can teleport objects that aren't meant to be moved.
# NOTE: after teleportation, need to look twice before description updates.

# Finally, to detect whether an action was recognized by the parser and changed the game state
env.step('hail taxi')
if env.world_changed():
  print('We found a valid action!')
```

## Supported Games
Game | Download | MD5 Hash
--- | --- | ---
[The Acorn Court](http://ifdb.tads.org/viewgame?id=tqvambr6vowym20v) | [acorncourt.z5](http://mirror.ifarchive.org/if-archive/games/zcode/acorncourt.z5) | a61400439aa76f8faba3b8f01edd4a72
[Adventureland](http://ifdb.tads.org/viewgame?id=dy4ok8sdlut6ddj7) | [Adventureland.z5](http://mirror.ifarchive.org/if-archive/games/zcode/Adventureland.z5) | a42545bd17330ae5e6fed02270ccfb4a
[Adventure](http://ifdb.tads.org/viewgame?id=fft6pu91j85y4acv) | [Advent.z5](http://mirror.ifarchive.org/if-archive/games/zcode/Advent.z5) | ee2242e155fd8910921b0f8e04019a3a
[Afflicted](http://ifdb.tads.org/viewgame?id=epl4q2933rczoo9x) | [afflicted.z8](http://mirror.ifarchive.org/if-archive/games/competition2008/zcode/afflicted/afflicted.z8) | 064272be87de7106192b6fb743c4dfc4
[Anchorhead](http://ifdb.tads.org/viewgame?id=op0uw1gn1tjqmjt7) | [anchor.z8](http://ifarchive.org/if-archive/games/zcode/anchor.z8) | c043df8624e0e1e9fda92f1a74b6e402
[The Awakening](http://ifdb.tads.org/viewgame?id=12pkmwaekw4suh7g) | [awaken.z5](http://mirror.ifarchive.org/if-archive/games/zcode/awaken.z5) | 9ba48c72d96ab3e7956a8570b12d34d6
[Balances](http://ifdb.tads.org/viewgame?id=x6ne0bbd2oqm6h3a) | [Balances.z5](http://mirror.ifarchive.org/if-archive/games/zcode/Balances.z5) | f2cb8f94a7e8df3b850a758da26fa387
[Ballyhoo](http://ifdb.tads.org/viewgame?id=b0i6bx7g4rkrekgg) | ballyhoo.z3 | 5d54e326815b0ed3aff8efb8ff02ef2f
[Curses!](https://ifdb.tads.org/viewgame?id=plvzam05bmz3enh8) | [curses.z5](http://mirror.ifarchive.org/if-archive/games/zcode/curses.z5) | f06a42a29a5a4e6aa70958c9ae4c37cd
[Cutthroats](http://ifdb.tads.org/viewgame?id=4ao65o1u0xuvj8jf) | cutthroat.z3 | 216eeeba1c8017a77343dc8482f6f185
[Deephome: A Telleen Adventure](http://ifdb.tads.org/viewgame?id=x85otcikhwp8bwup) | [deephome.z5](http://mirror.ifarchive.org/if-archive/games/zcode/deephome.z5) | 5e56a6e5cdeecded434a8fd8012fc2c6
[Detective](http://ifdb.tads.org/viewgame?id=1po9rgq2xssupefw) | [detective.z5](http://mirror.ifarchive.org/if-archive/games/zcode/detective.z5) | 822655c9be83e292e06d3d3b1d6a9734
[Dragon Adventure](http://ifdb.tads.org/viewgame?id=sjiyffz8n5patu8l) | [Dragon.z5](http://mirror.ifarchive.org/if-archive/games/zcode/dragon.zip) | 96d314997e5d3a5a793c83845977d44d
[Enchanter](http://ifdb.tads.org/viewgame?id=vu4xhul3abknifcr) | enchanter.z3 | ad3cdea88d81033fe29167688bd98c31
[The Enterprise Incidents](http://ifdb.tads.org/viewgame?id=ld1f3t5epeagilfz) | [enter.z5](http://mirror.ifarchive.org/if-archive/games/zcode/enter.z5) | 4c48ba2c5523d78c5f7f9b7809d16b1d
[Goldilocks is a FOX!](http://ifdb.tads.org/viewgame?id=59ztsy9p01avd6wp) | [gold.z5](http://mirror.ifarchive.org/if-archive/games/zcode/gold.z5) | f275ddf32ce8a9e744d53c3b99c5a658
[The Hitchhiker's Guide to the Galaxy](http://ifdb.tads.org/viewgame?id=ouv80gvsl32xlion) | hhgg.z3 | 6666389f60e0c8e4ceb08242a263bb52
[Hollywood Hijinx](http://ifdb.tads.org/viewgame?id=jnfkbgdgopwfqist) | hollywood.z3 | 1ea91a064941a3f612b20833f0a47df7
[Hunter, in Darkness](http://ifdb.tads.org/viewgame?id=mh1a6hizgwjdbeg7) | [huntdark.z5](http://mirror.ifarchive.org/if-archive/games/competition99/inform/huntdark/huntdark.z5) | 253b02c8012710577085b9fd3a155cb7
[Infidel](http://ifdb.tads.org/viewgame?id=anu79a4n1jedg5mm) | infidel.z3 | 425fa66869309d7ed7f8ef04a492fbb7
[Inhumane](http://ifdb.tads.org/viewgame?id=wvs2vmbigm9unlpd) | [inhumane.z5](http://mirror.ifarchive.org/if-archive/games/zcode/inhumane.z5) | 84d3ce7ccfafb873736490811a0cc78c
[The Jewel of Knowledge](http://ifdb.tads.org/viewgame?id=hu60gp1bgkhlo5yx) | [jewel.z5](http://mirror.ifarchive.org/if-archive/games/zcode/jewel.z5) | 1eef9c0fa009ca4adf4872cfc5249d45
[Return to Karn](http://ifdb.tads.org/viewgame?id=bx8118ggp6j7nslo) | [karn.z5](http://mirror.ifarchive.org/if-archive/games/zcode/karn.z5) | ec55791be814db3663ad1aec0d6b7690
[Leather Goddesses of Phobos](http://ifdb.tads.org/viewgame?id=3p9fdt4fxr2goctw) | lgop.z3 | 8241afdadbdcdb934ee06afc6ba59b67
[All Quiet on the Library Front](http://ifdb.tads.org/viewgame?id=400zakqderzjnu1i) | [library.z5](http://mirror.ifarchive.org/if-archive/games/zcode/library.z5) | daf57133d346442b983bd333fb586cc4
[Mother Loose](http://ifdb.tads.org/viewgame?id=4wd3lyaxi4thp8qi) | [loose.z5](http://mirror.ifarchive.org/if-archive/games/zcode/loose.z5) | 31a0c1e360dce94aa5bece5240691d17
[Lost Pig](http://ifdb.tads.org/viewgame?id=mohwfk47yjzii14w) | [LostPig.z8](http://mirror.ifarchive.org/if-archive/games/zcode/LostPig.z8) | aaf0b90fbb31717481c02832bf412070
[The Ludicorp Mystery](http://ifdb.tads.org/viewgame?id=r6g7pflngn3uxbam) | [ludicorp.z5](http://mirror.ifarchive.org/if-archive/games/zcode/ludicorp.z5) | 646a63307f77dcdcd011f330277ae262
[The Lurking Horror](http://ifdb.tads.org/viewgame?id=jhbd0kja1t57uop) | lurking.z3 | 5f42ff092a2f30471ae98150ef4da2e1
[The Moonlit Tower](http://ifdb.tads.org/viewgame?id=10387w68qlwehbyq) | [Moonlit.z5](http://mirror.ifarchive.org/if-archive/games/competition2002/zcode/moonlit/Moonlit.z5) | bf75b9651cff0e2d04302f19c443588e
[Monsters of Murdac](http://ifdb.tads.org/viewgame?id=q36lh5np0q9nak28) | [Murdac.z5](http://mirror.ifarchive.org/if-archive/games/zcode/Murdac.z5) | 570179d4f21b2f600862dbffbb5afc3e
[Night at the Computer Center](http://ifdb.tads.org/viewgame?id=ydhwa11st460g9u3) | [night.z5](http://mirror.ifarchive.org/if-archive/games/zcode/night.z5) | 72125f159cccd581786ac16a2828d4e3
[9:05](http://ifdb.tads.org/viewgame?id=qzftg3j8nh5f34i2) | [905.z5](http://mirror.ifarchive.org/if-archive/games/zcode/905.z5) | 4c5067169b834d247a30bb08d1039896
[OMNIQuest](http://ifdb.tads.org/viewgame?id=mygqz9tzxqvryead) | [omniquest.z5](http://mirror.ifarchive.org/if-archive/games/zcode/omniquest.z5) | 80ea198bca425b6d819c74bfa854236e
[Party Foul](http://ifdb.tads.org/viewgame?id=cqwq699i9qiqdju) | [partyfoul.z8](https://drive.google.com/uc?export=download&id=18FLKC7thabFBoB6261EQUOdUoODOdR0i) | d221daa82708c4e54447f1a884c239ef
[Pentari](http://ifdb.tads.org/viewgame?id=llchvog0ukwrphih) | [pentari.z5](http://mirror.ifarchive.org/if-archive/games/zcode/pentari.z5) | f24c6863468823b744e910ccfe997c6d
[Planetfall](http://ifdb.tads.org/viewgame?id=xe6kb3cuqwie2q38) | planetfall.z3 | 6487dc814b280f5603c53155de378d27
[Plundered Hearts](http://ifdb.tads.org/viewgame?id=ddagftras22bnz8h) | plundered.z3 | 6ae4fd54b7e55675ec7e54ec4dd26462
[Reverberations](http://ifdb.tads.org/viewgame?id=dop7nbjl90r5zmf9) | [reverb.z5](http://mirror.ifarchive.org/if-archive/games/zcode/reverb.z5) | be6d5fa9587a079782b64739e629461f
[Seastalker](http://ifdb.tads.org/viewgame?id=56wb8hflec2isvzm) | seastalker.z3 | ee339dbdbb0792f67e20bd71bafe0ea5
[The Meteor, the Stone and a Long Glass of Sherbet](http://ifdb.tads.org/viewgame?id=273o81yvg64m4pkz) | [sherbet.z5](http://mirror.ifarchive.org/if-archive/games/zcode/sherbet.z5) | 53bf7a60017e06998cc1542cf35f76fa
[Sherlock](http://ifdb.tads.org/viewgame?id=ug3qu521hze8bsvz) | sherlock.z5 | 35240654d83f9e7073973d338f9657b8
[Snack Time!](http://ifdb.tads.org/viewgame?id=yr3y8s9k8e40hl5q) | [snacktime.z8](http://mirror.ifarchive.org/if-archive/games/competition2008/zcode/snack/snacktime.z8) | 0ff228d12d7cb470dc1a8e9a5151769b
[Sorcerer](http://ifdb.tads.org/viewgame?id=lidg5nx9ig0bwk55) | sorcerer.z3 | 20f1468a058d0a6de016ae70022e651c
[Spellbreaker](http://ifdb.tads.org/viewgame?id=wqsmrahzozosu3r) | spellbrkr.z3 | 7a92ce19a39bedd970d0f1e296981f71
[SPIRITWRAK](http://ifdb.tads.org/viewgame?id=tqpowvmdoemtooqf) | [spirit.z5](http://mirror.ifarchive.org/if-archive/games/zcode/spirit.z5) | 808039c4e9554bdd15d7793539b3bd97
[The Temple](http://ifdb.tads.org/viewgame?id=kq9qgjkf2k6xn1c0) | [temple.z5](http://mirror.ifarchive.org/if-archive/games/zcode/temple.z5) | 22a0ddac6be15540616c10f1007197f3
[Theatre](http://ifdb.tads.org/viewgame?id=bv8of8y9xeo7307g) | [theatre.z5](http://mirror.ifarchive.org/if-archive/games/zcode/theatre.z5) | 33dcc5085acb290d1817e07653c13480
[Trinity](http://ifdb.tads.org/viewgame?id=j18kjz80hxjtyayw) | trinity.z4 | 3bf1a444a1fc2057130ecb9806117233
[Tryst of Fate](http://ifdb.tads.org/viewgame?id=ic0ebhbi70bdmyc2) | [tryst205.z5](http://mirror.ifarchive.org/if-archive/games/zcode/tryst205.z5) | fc65ad8d4588da92fd39871f6f7463db
[The Weapon](http://ifdb.tads.org/viewgame?id=tcebhl79rlxo3qrk) | [weapon.z5](http://mirror.ifarchive.org/if-archive/games/zcode/weapon.zip) | c632204be3849d6c5bb6f4eb5aca3cc0
[Wishbringer](http://ifdb.tads.org/viewgame?id=z02joykzh66wfhcl) | wishbringer.z3 | 87ed53d854f7e57c36106fca3b9cf5a6
[Raising the Flag on Mount Yo Momma](http://ifdb.tads.org/viewgame?id=1iqmpkn009h9gbug) | [yomomma.z8](https://drive.google.com/uc?export=download&id=1DnfJCWYXxXnn5TAHVAqHlr1BQbgf1Qm2) | 5b10162a7a134e7b4c381ecedfb4bc44
[Escape from the Starship Zenon](http://ifdb.tads.org/viewgame?id=rw7zv98mifbr3335) | [zenon.z5](http://mirror.ifarchive.org/if-archive/games/zcode/zenon.z5) | 631cc926b4251f5a5f646d3a6bdac8c6
[Zork I](http://ifdb.tads.org/viewgame?id=0dbnusxunq7fw5ro) | zork1.z5 | b732a93a6244ddd92a9b9a3e3a46c687
[Zork II](http://ifdb.tads.org/viewgame?id=yzzm4puxyjakk8c4) | zork2.z5 | 5bcd91ee055e9bd42812617571be227b
[Zork III](http://ifdb.tads.org/viewgame?id=vrsot1zgy1wfcdru) | zork3.z5 | ffda9ee2d428fa2fa8e75a1914ff6959
[Zork: The Undiscovered Underground](http://ifdb.tads.org/viewgame?id=40hswtkhap88gzvn) | ztuu.z5 | d8e1578470cbc676e013e03d72c93141


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
