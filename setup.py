from setuptools import setup, find_packages
setup(name='hockeydata',
version='0.1',
description='Package for scraping data from eliteprospect website and transfering it in SQL database',
url='https://github.com/honzaz1234/elite',
author='jz',
author_email='jan.ziacik@gmail.com',
license='MIT',
package_dir={"": "src"},
packages = find_packages(
    where='src'
    ),
install_requires=["sqlalchemy>=2.0", "scrapy", "requests"],
python_requires="~=3.10")