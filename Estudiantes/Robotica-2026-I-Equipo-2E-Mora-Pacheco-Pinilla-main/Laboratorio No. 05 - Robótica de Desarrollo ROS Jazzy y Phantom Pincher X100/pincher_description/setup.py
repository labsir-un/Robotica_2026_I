from glob import glob
import os

from setuptools import setup

package_name = 'pincher_description'

def _mesh_data_files():
    entries = []
    for root, dirs, names in os.walk('meshes'):
        if not names:
            continue
        files = [os.path.join(root, name) for name in names]
        install_dir = os.path.join('share', package_name, root)
        entries.append((install_dir, files))
    return entries

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=(
        [('share/ament_index/resource_index/packages', ['resource/' + package_name])] +
        [('share/' + package_name, ['package.xml'])] +
        [(os.path.join('share', package_name, 'urdf'), glob('urdf/*'))] +
        _mesh_data_files() +
        [(os.path.join('share', package_name, 'rviz'), glob('rviz/*'))] +
        [(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py'))]
    ),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Curso de Robótica 2026-I',
    maintainer_email='pendiente@ejemplo.invalid',
    description='URDF/Xacro, mallas y visualización RViz del PhantomX Pincher X100.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={'console_scripts': ['robot_desc_pub = pincher_description.robot_desc_pub:main']},
)
