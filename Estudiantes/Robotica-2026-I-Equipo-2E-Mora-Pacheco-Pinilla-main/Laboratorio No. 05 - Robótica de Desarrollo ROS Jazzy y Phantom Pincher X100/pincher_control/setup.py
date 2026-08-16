from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'pincher_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Curso de Robótica 2026-I',
    maintainer_email='pendiente@ejemplo.invalid',
    description='Control directo, GUI y herramientas Dynamixel para PhantomX Pincher X100 en ROS 2 Jazzy.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'control_servo = pincher_control.control_servo:main',
            'pincher_gui = pincher_control.pincher_gui:main',
            'scan_dynamixel = pincher_control.scan_dynamixel:main',
        ],
    },
)
