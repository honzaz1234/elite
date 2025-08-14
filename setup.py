from setuptools import find_packages, setup
from pathlib import Path

print(find_packages(where="src"))

this_directory = Path(__file__).parent
long_description = (this_directory/"README.md").read_text()

setup(
    name='hockeydb',
    version='0.1',
    description='Package for scraping data from eliteprospect website and transfering it in SQL database',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/honzaz1234/elite',
    author='jz',
    author_email='-',
    license='MIT',
    license_files = ('LICENSE.txt',),
    package_dir={"": "src"},
    packages = [
        'hockeydb', 'hockeydb.database_creator', 'hockeydb.database_insert', 'hockeydb.database_queries', 'hockeydb.database_session', 'hockeydb.gamedata', 'hockeydb.hockeydata', 'hockeydb.logger', 'hockeydb.management', 'hockeydb.mappers', 'hockeydb.gamedata.input_dict', 'hockeydb.gamedata.update_dict', 'hockeydb.hockeydata.defunct', 'hockeydb.hockeydata.get_data', 'hockeydb.hockeydata.get_urls', 'hockeydb.hockeydata.input_dict', 'hockeydb.hockeydata.insert_db', 'hockeydb.hockeydata.playwright_setup', 'hockeydb.hockeydata.scraper', 'hockeydb.hockeydata.tests', 'hockeydb.hockeydata.update_dict'
        ],
    install_requires=["sqlalchemy", "scrapy", "requests"],
    python_requires="~=3.10"
)