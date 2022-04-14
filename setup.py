from setuptools import setup

setup(
    name='quickenv',
    packages=['quickenv'],
    entry_points={
        'console_scripts': [
            'quickenv = quickenv:cli'
        ]
    },
    install_requires=[
        'click>=8'
    ],
    description="A small Python venv manager",
)
