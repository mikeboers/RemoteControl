from setuptools import setup, find_packages

setup(
    
    name='remotecontrol',
    version='1.0.0-dev',
    description='A remote REPL and command socket.',
    url='http://github.com/westernx/remotecontrol',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    
    author='Mike Boers',
    author_email='remotecontrol@mikeboers.com',
    license='BSD-3',
    
    scripts=[
        'bin/remotecontrol',
    ],
    
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
)