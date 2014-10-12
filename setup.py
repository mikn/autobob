from setuptools import setup, find_packages

with open('requirements.txt') as reqs:
    inst_reqs = reqs.read().split('\n')

setup(
    name='autobob',
    version='0.1.0',
    packages=find_packages(),
    author='Mikael Knutsson',
    author_email='mikael.knutsson@gmail.com',
    description='A bot framework made according to actual software principles',
    long_description=open('README.txt').read(),
    classifiers='License :: OSI Approved :: BSD License',
    install_requires=inst_reqs,
    entry_points={
        'console_scripts': ['autobob = autobob.main:main',
                            'autobob_init = autobob.init:main']
    }
)
