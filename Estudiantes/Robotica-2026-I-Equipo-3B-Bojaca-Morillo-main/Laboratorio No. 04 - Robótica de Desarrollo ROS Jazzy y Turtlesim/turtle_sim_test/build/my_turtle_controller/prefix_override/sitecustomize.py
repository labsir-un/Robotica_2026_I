import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/elreyrt/ros2_ws/turtle_sim_test/install/my_turtle_controller'
