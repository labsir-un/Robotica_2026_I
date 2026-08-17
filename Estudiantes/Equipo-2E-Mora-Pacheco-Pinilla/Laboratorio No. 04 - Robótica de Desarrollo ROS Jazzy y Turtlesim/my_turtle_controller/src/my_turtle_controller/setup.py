from setuptools import find_packages, setup

package_name = 'my_turtle_controller'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Estudiante',
    maintainer_email='estudiante@unal.edu.co',
    description='Control manual y automatico de turtlesim mediante teclado en ROS 2 Jazzy Jalisco.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_turtle = my_turtle_controller.move_turtle:main',
        ],
    },
)
