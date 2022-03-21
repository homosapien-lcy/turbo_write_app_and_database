from functools import partial
# use pathos.multiprocessing instead of multiprocessing in some cases
# which uses dill and will not throw error cannot pickle
import pathos.multiprocessing as pathos_mp

pathos_core_pool_all = "pathos_mp.ProcessPool(nodes=None)"
pathos_core_pool_32 = "pathos_mp.ProcessPool(nodes=32)"
pathos_core_pool_24 = "pathos_mp.ProcessPool(nodes=24)"
pathos_core_pool_16 = "pathos_mp.ProcessPool(nodes=16)"
pathos_core_pool_12 = "pathos_mp.ProcessPool(nodes=12)"
pathos_core_pool_8 = "pathos_mp.ProcessPool(nodes=8)"
pathos_core_pool_6 = "pathos_mp.ProcessPool(nodes=6)"
pathos_core_pool_4 = "pathos_mp.ProcessPool(nodes=4)"
pathos_core_pool_2 = "pathos_mp.ProcessPool(nodes=2)"

import multiprocessing as mp

# set as string and then use eval(), if directly set: core_pool_8 = mp.Pool(processes=8)
# will result in error
core_pool_all = "mp.Pool(processes=None)"
core_pool_32 = "mp.Pool(processes=32)"
core_pool_24 = "mp.Pool(processes=24)"
core_pool_16 = "mp.Pool(processes=16)"
core_pool_12 = "mp.Pool(processes=12)"
core_pool_8 = "mp.Pool(processes=8)"
core_pool_6 = "mp.Pool(processes=6)"
core_pool_4 = "mp.Pool(processes=4)"
core_pool_2 = "mp.Pool(processes=2)"
