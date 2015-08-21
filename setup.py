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
    
    entry_points={

        'console_scripts': '''
            remotecontrol = remotecontrol.cli:main
        ''',

        'appinit.maya.gui': '''
            remotecontrol_maya = remotecontrol.setup:setup_maya
        ''',
        'appinit.nuke.gui': '''
            remotecontrol_nuke = remotecontrol.setup:setup_nuke
        ''',
        'appinit.houdini.gui': '''
            remotecontrol_houdini = remotecontrol.setup:setup_houdini
        ''',
        'appinit.mari.gui': '''
            remotecontrol_mari = remotecontrol.setup:setup_mari
        ''',
    },

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
)
