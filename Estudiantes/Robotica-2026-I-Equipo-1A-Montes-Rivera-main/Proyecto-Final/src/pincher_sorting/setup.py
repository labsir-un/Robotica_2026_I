from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'pincher_sorting'

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
    description='Máquina de estados Pick & Place para PhantomX Pincher X100.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sorting_node = pincher_sorting.sorting_node:main',
            'test_routine_node = pincher_sorting.test_routine_node:main',
            'test_block_publisher = pincher_sorting.test_block_publisher:main',
            'spawn_object = pincher_sorting.spawn_object:main',
            'vision_node = pincher_sorting.vision_node:main',
        ],
    },
)
