from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'pincher_lab'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Equipo 1E - Robotica 2026-I',
    maintainer_email='jzapatapi@unal.edu.co',
    description='Control, cinematica y trayectorias del PhantomX Pincher X100.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pincher_node = pincher_lab.pincher_node:main',
            'joint_demo = pincher_lab.joint_demo:main',
            'trajectory_demo = pincher_lab.trajectory_demo:main',
            'teach_repeat = pincher_lab.teach_repeat:main',
            'figure_player = pincher_lab.figure_player:main',
            'choreography = pincher_lab.choreography:main',
            'kinematics_cli = pincher_lab.kinematics_cli:main',
            'recorder = pincher_lab.recorder:main',
            'experiments = pincher_lab.experiments:main',
            'fk_tf_check = pincher_lab.fk_tf_check:main',
            'kit_bridge = pincher_lab.kit_bridge:main',
        ],
    },
)
