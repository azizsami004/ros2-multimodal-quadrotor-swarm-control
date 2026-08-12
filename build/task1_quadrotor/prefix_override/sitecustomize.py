import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/abdul/Desktop/intp assignment/task_1_ws/install/task1_quadrotor'
