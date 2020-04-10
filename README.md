<p align="center">
    <br>
    <img src="https://raw.githubusercontent.com/microsoft/jericho/master/docs/source/imgs/jericho.png" width="300"/>
    <br>
<p>

<p align="center">
  <a href='https://jericho-py.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/jericho-py/badge/?version=latest' alt='Documentation Status' />
  </a>
  <a href='https://travis-ci.org/microsoft/jericho'>
    <img src='https://travis-ci.org/microsoft/jericho.svg?branch=master' alt='Build Status' />
  </a>
  <a href='https://badge.fury.io/py/jericho'>
    <img src='https://badge.fury.io/py/jericho.svg' alt='PyPI version' />
  </a>
<p>

<p align="center">
  A lightweight python-based interface connecting learning agents with interactive fiction games.
<p>

<br>

## Requirements
***Linux***, ***Python 3***, ***Spacy***, and basic build tools like ***gcc***.

## Install
```bash
pip3 install jericho
python3 -m spacy download en_core_web_sm
```

## Documentation
- [Quickstart](https://jericho-py.readthedocs.io/en/latest/tutorial_quick.html)
- [Frotz Environment](https://jericho-py.readthedocs.io/en/latest/frotz_env.html)
- [Object Tree](https://jericho-py.readthedocs.io/en/latest/object_tree.html)
- [Game Dictionary](https://jericho-py.readthedocs.io/en/latest/dictionary.html)
- [Template Action Generator](https://jericho-py.readthedocs.io/en/latest/template_action_generator.html)
- [Utilities](https://jericho-py.readthedocs.io/en/latest/util.html)
- [Defines](https://jericho-py.readthedocs.io/en/latest/defines.html)

## Agents
- [Template-DQN and DRRN](https://github.com/microsoft/tdqn)
- [Knowledge Graph Advantage Actor Critic (KG-A2C)](https://github.com/rajammanabrolu/KG-A2C)

## Citing Jericho
If Jericho is used in your research, please cite the following:
```
@article{hausknecht19,
  title={Interactive Fiction Games: A Colossal Adventure},
  author={Hausknecht, Matthew and Ammanabrolu, Prithviraj and C\^ot\'{e} Marc-Alexandre and Yuan Xingdi},
  journal={CoRR},
  year={2019},
  url={http://arxiv.org/abs/1909.05398},
  volume={abs/1909.05398}
}
```

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
