from glob import glob
import os

from setuptools import setup

package_name = 'pincher_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*.*')),
        (os.path.join('share', package_name, 'meshes/STL'), glob('meshes/STL/*.*')),
        (os.path.join('share', package_name, 'meshes/visual'), glob('meshes/visual/*.*')),
        (os.path.join('share', package_name, 'meshes/collision'), glob('meshes/collision/*.*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Curso de Robótica 2026-I',
    maintainer_email='jriveramo@unal.edu.co',
    description='URDF/Xacro, mallas y visualización RViz del PhantomX Pincher X100.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={'console_scripts': []},
)