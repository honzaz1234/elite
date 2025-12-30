# hockeydata

The purpose of the hockeydata package is to provide tools for downloading hockey data 
from both EliteProspects and NHL.com, and transferring it into a custom database for 
further analysis.

The package currently supports downloading the following entities:

* Teams: general information such as founding year, location, current league, historical 
  team names, retired player numbers, affiliated teams, and stadium details.

* Leagues: league awards and historical seasonal standings of participating teams.

* Players: general information (age, position, handedness, etc.), family connections to 
  other hockey players, league awards received across seasons, and player statistics 
  for both leagues and tournaments.

* Games (from NHL.com): detailed game data, including schedules, results, and 
  player/game statistics.

## Installation

The package is not available on PyPI. 
To install it, run the setup.py file located in the root directory of the project:

```bash
python setup.py install
```
or
```bash
pip install .
```

## Usage

For examples of how to use the code, see the bin folder of the project. 
It contains example scripts for downloading all four entities: league, team, and player and game data.

## License

[MIT](https://choosealicense.com/licenses/mit/)
