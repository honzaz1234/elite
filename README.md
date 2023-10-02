# hockeydata

The purpose of hockeydata package is to provide methods for downloading hockey data 
from eliteprospects.com website and for transfering them into custom database. There are 
methods available in the package to download information on 3 different entities: team, 
league and player. 
In case of the team, the data that can be accessed with the help of the package is 
general information about selected team, as for example the year the team was founded, 
its location, in what league it plays, the various  names that the team had over its history, 
players and numbers whose were retired by the team, its affiliated teams and info about stadium 
in which it plays. 
In case of the league, there can be downloaded awards that the league awards to its players and 
historical seasonal standing of teams in the league.
For player entity, there are available methods for downloading general info (age, position, handedness...), 
the information on relatives of the player who were also hockey players, league awards awarded to player 
in each season, and his statistics for each season in both tournaments and leagues.

## Installation

The package is not available on PyPI. In order to install it please run setup.py file in root directory 
of project (available at: https://github.com/honzaz1234/elite).

```bash
python setup.py install
```

## Usage

For example of code usage please see bin folder of the project in which there are availaible example
scripts for downloading all 3 entities (league, team, player).

## License

[MIT](https://choosealicense.com/licenses/mit/)
