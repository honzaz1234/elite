from setuptools import setup, find_packages
setup(name='hockey_data',
version='0.1',
description='Package for scraping data from eliteprospect website and transfering it in SQL database',
url='https://github.com/honzaz1234/elite',
author='jz',
author_email='jan.ziacik@gmail.com',
license='MIT',
package_dir={"": "src"},
packages = find_packages(
    where='src',
    ),
install_requires=["sqlalchemy", "re", "datetime", "json", "time", "scrapy", "requests"],
python_requeiers="~=3.10")