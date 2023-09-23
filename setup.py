from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent

long_description = (this_directory/"README.md").read_text()

setup(
    name='hockeydata',
    version='0.1.0',
    description='Package for scraping data from eliteprospect website and transfering it in SQL database',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/honzaz1234/elite',
    author='jz',
    author_email='-',
    license='MIT',
    license_files = ('LICENSE.txt',),
    package_dir={"": "src"},
    packages = ['hockeydata', 'hockeydata.tests', 
                'hockeydata.database_creator', 'hockeydata.get_urls', 'hockeydata.input_dict', 'hockeydata.insert_db', 'hockeydata.scraper', 'hockeydata.update_dict'],
    install_requires=["sqlalchemy", "scrapy", "requests"],
    python_requires="~=3.10"
)