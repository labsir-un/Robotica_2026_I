from setuptools import find_packages, setup

setup(
    name='lab05_code',
    version='0.1.0',
    packages=find_packages(),
    data_files=[],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'individual_movement = lab05_code.individual_movement:main',
            'calibration = lab05_code.calibration:main',
            'teach_and_repeat = lab05_code.individual_movement:main',
            'interpolation = lab05_code.interpolation:main',
            'sinusoidal = lab05_code.sinusoidal:main',
            'fk_dh = lab05_code.fk_dh:main',
            'ik = lab05_code.ik:main',

            'tracing = lab05_code.tracing:main',
            'choreography = lab05_code.choreography:main',
        ],
    },
)
