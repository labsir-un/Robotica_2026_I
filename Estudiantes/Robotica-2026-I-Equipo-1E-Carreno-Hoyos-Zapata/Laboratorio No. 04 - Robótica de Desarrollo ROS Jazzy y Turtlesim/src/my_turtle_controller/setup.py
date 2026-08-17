from setuptools import find_packages, setup

package_name = 'my_turtle_controller'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jose Andres Zapata Piñeros',
    maintainer_email='jzapatapi@unal.edu.co',
    description='Controlador de turtlesim — Lab 04 Robótica 2026-I UNAL',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_turtle = my_turtle_controller.move_turtle:main',
        ],
    },
)
