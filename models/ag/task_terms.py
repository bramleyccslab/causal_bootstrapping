# %%
import math
import pandas as pd
from pandas.core.common import flatten
from copy import copy

from helpers import secure_list, copy_list
from base_classes import *
from base_methods import *

# %%
# Define task classes
class Stripe:
  def __init__(self, name):
    self.ctype = 'stripe'
    self.name = name
    self.value = int(name[1:])
  def __str__(self):
    return self.name

class Dot:
  def __init__(self, name):
    self.ctype = 'dot'
    self.name = name
    self.value = int(name[1:])
  def __str__(self):
    return self.name

class Egg:
  def __init__(self, stripe, dot):
    self.ctype = 'egg'
    self.stripe = stripe
    self.dot = dot
  @property
  def name(self):
    return f'Egg({self.stripe.name},{self.dot.name})'
  def __str__(self):
    return self.name

# %%
# Base task base terms
for i in range(5):
  exec(f"S{i} = Stripe('S{i}')")

for i in range(5):
  exec(f"O{i} = Dot('O{i}')")

# Placeholders for typed program enumeration
stripe = Placeholder('stripe')
dot = Placeholder('dot')
num = Placeholder('num')
egg = Placeholder('egg')

# Primitives
getStripe = Primitive('getStripe', ['egg'], 'num', lambda x: copy(x[0].stripe.value))
getDot= Primitive('getDot', ['egg'], 'num', lambda x: copy(x[0].dot.value))

addnn = Primitive('addnn', ['num', 'num'], 'num', lambda x: sum(x))
subnn = Primitive('subnn', ['num', 'num'], 'num', lambda x: x[0]-x[1])
mulnn = Primitive('mulnn', ['num', 'num'], 'num', lambda x: math.prod(x))

I = Primitive('I', 'egg', 'egg', return_myself)

# Routers
B = Router('B', send_right)
C = Router('C', send_left)
S = Router('S', send_both)
K = Router('K', constant)

BB = ComRouter([B, B])
BC = ComRouter([B, C])
BS = ComRouter([B, S])
BK = ComRouter([B, K])
CB = ComRouter([C, B])
CC = ComRouter([C, C])
CS = ComRouter([C, S])
CK = ComRouter([C, K])
SB = ComRouter([S, B])
SC = ComRouter([S, C])
SS = ComRouter([S, S])
SK = ComRouter([S, K])
KB = ComRouter([K, B])
KC = ComRouter([K, C])
KS = ComRouter([K, S])
KK = ComRouter([K, K])

# # %% Debug
# x = Egg(S2,O0)
# y = 4
# Program([CB,[B,mulnn,getStripe],I]).run([x,y])

# # %% Task set up
# pm_terms = list(range(5)) + [
#   S0, S1, S2, S3, S4,
#   O0, O1, O2, O3, O4,
#   getStripe, getDot, addnn, subnn, mulnn, I,
#   {'terms': '[B,I,I]', 'arg_types': 'num', 'return_type': 'num', 'type': 'program'},
#   {'terms': '[KB,I,I]', 'arg_types': 'egg_num', 'return_type': 'num', 'type': 'program'},
#   {'terms': '[BK,I,I]', 'arg_types': 'egg_num', 'return_type': 'egg', 'type': 'program'},
# ]

# pm_setup = []
# for pt in pm_terms:
#   if isinstance(pt, dict):
#     terms = pt['terms']
#     arg_types = pt['arg_types']
#     return_type = pt['return_type']
#     type = pt['type']
#   elif isinstance(pt, bool) or isinstance(pt, int):
#     terms = str(pt)
#     arg_types = ''
#     return_type = 'bool' if isinstance(pt, bool) else 'num'
#     type = 'base_term'
#   elif pt.ctype == 'dot' or pt.ctype == 'length' or pt.ctype == 'stripe':
#     terms = pt.name
#     arg_types = ''
#     return_type = pt.ctype
#     type = 'base_term'
#   else:
#     terms = pt.name
#     arg_types = '_'.join(secure_list(pt.arg_type))
#     return_type = pt.return_type
#     type = 'primitive'
#   pm_setup.append({'terms':terms,'arg_types':arg_types,'return_type':return_type,'type':type,'count':1})

# pm_task = (pd.DataFrame.from_records(pm_setup)
#   .groupby(by=['terms','arg_types','return_type','type'], as_index=False)
#   .agg({'count': pd.Series.count})
#   .sort_values(by=['type','return_type','arg_types','terms'])
#   .reset_index(drop=1))
# pm_task['is_init'] = int(1)
# pm_task[['terms', 'arg_types', 'return_type', 'type', 'is_init', 'count']].to_csv('data/task_pm.csv')

# %%
