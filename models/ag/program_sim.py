# %%
import pandas as pd

from task_terms import *
from program_lib import Program_lib
from helpers import normalize, softmax

# %%
def get_pred(program_lib, partial_data, depth=3, type_sig=[['egg', 'num'], 'num']):
  pm_info = program_lib.generate_program(type_sig,max_step=depth)
  if 'ERROR' in pm_info['terms']:
    return None
  else:
    pm = Program(eval(pm_info['terms']))
    return pm.run([partial_data['agent'], partial_data['recipient']])
# get_pred(pl, data)

def sim_preds(partial_data, program_lib, n, softmax_base=0):
  # ret_df = program_lib.get_all_objs()[['terms']]
  ret_df = pd.DataFrame({'terms': list(range(17))})
  ret_df['count'] = 0
  for _ in range(n):
    result = get_pred(program_lib, partial_data)
    if result is not None:
      result = 16 if result > 16 else result
      result = 0 if result < 0 else result
      found_index = ret_df[ret_df['terms']==result].index.values[0]
      ret_df.at[found_index, 'count'] += 1
  ret_df['prob'] = normalize(ret_df['count']) if softmax_base == 0 else softmax(ret_df['count'], softmax_base)
  return ret_df
# sim_preds(data, pl, 100)

def sim_for_all(data_list, program_lib, n, softmax_base=0):
  # ret_df = program_lib.get_all_objs()[['terms']]
  ret_df = pd.DataFrame({'terms': list(range(17))})
  for i in range(len(data_list)):
    preds = sim_preds(data_list[i], program_lib, n, softmax_base)
    preds = preds.rename(columns={"count": f"count_{i+1}", "prob": f"prob_{i+1}"})
    ret_df = pd.merge(ret_df, preds, on='terms', how='left')
  return ret_df

# Trun str objects to objects
def objstr_to_stone(obj):
  ret_obj = {}
  ret_obj['agent'] = eval(obj['agent'])
  ret_obj['recipient'] = eval(obj['recipient'])
  if len(obj) > 2:
    ret_obj['result'] = eval(obj['result'])
  return ret_obj

# Read tuple as task objects
def transform_obj(str, is_agent=True):
  if is_agent:
    stripe = int(str.split(',')[0][1:])
    dot = int(str.split(',')[1])
    return f'Egg(S{stripe},O{dot})'
  else:
    return int(str.split(',')[2][:-1])
