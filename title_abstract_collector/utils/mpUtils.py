from functools import partial
import multiprocessing as mp

# set as string and then use eval(), if directly set: core_pool_8 = mp.Pool(processes=8)
# will result in error
core_pool_all = "mp.Pool(processes=None)"
core_pool_8 = "mp.Pool(processes=8)"
core_pool_6 = "mp.Pool(processes=6)"
core_pool_4 = "mp.Pool(processes=4)"
core_pool_2 = "mp.Pool(processes=2)"
