from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'pincher_hmi'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jesús Rivera',
    maintainer_email='jriveramo@unal.edu.co',
    description='Interfaz HMI PyQt5 para PhantomX Pincher X100 con Visión y Vacío.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hmi_gui = pincher_hmi.hmi_gui:main',
        ],
    },
)
