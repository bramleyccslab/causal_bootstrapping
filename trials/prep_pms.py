
# %%
from os import rename
from numpy import column_stack
import pandas as pd

import sys

from pandas._config import config
sys.path.append('../')
from task_terms import *
from helpers import normalize, softmax

# %% Get all intermediate samples
# programs_df = pd.DataFrame(columns=['terms','comp_lp','log_prob','n_exceptions'])
# prefixes = [
#   'combine_0a', 'combine_0b', 'combine_1a', 'combine_1b', 'combine_2a', 'combine_2b',
#   'construct_0a', 'construct_0b', 'construct_1a', 'construct_1b', 'construct_2a', 'construct_2b',
#   'decon_1a', 'decon_1b', 'decon_2a', 'decon_2b',
# ]
# for pr in prefixes:
#   for i in range(100):
#     iter = str(i+1).zfill(3)
#     programs_df = programs_df.append(pd.read_csv(f'tmp/{pr}_filtered_{iter}.csv', index_col=0).reset_index(drop=True), ignore_index=True)

# %%
# For the "flip" conditions, only care about two alternatives
programs_df = pd.DataFrame({
  'terms': [
    "[SC,[BB,subnn,[BC,[B,mulnn,[B,I,I]],getDot]],getStripe]",
    "[SB,[B,mulnn,getDot],[BC,[B,subnn,[B,I,I]],getStripe]]",
  ]
})

# %% Prep data
config_data = pd.read_json('../for_exp/config.json')
all_pairs_df = pd.DataFrame(columns=['agent', 'recipient'])
for i in range(len(config_data)):
  agent_info = config_data.agent[i].split(',')
  recipient_info = config_data.recipient[i].split(',')
  all_pairs_df.at[i,'agent'] = f'Egg(S{agent_info[0][1:]},O{agent_info[1][1:]})'
  all_pairs_df.at[i,'recipient'] = int(recipient_info[2][:-1])

# %% Collapse into equivalent classes
eq_class_df = pd.DataFrame(columns=['pred_list', 'terms', 'count'])
for i in range(len(programs_df)):
  terms = programs_df.at[i, 'terms']
  pm = Program(eval(terms))
  pred_list = []
  for j in range(len(all_pairs_df)):
    data = [eval(all_pairs_df.at[j,'agent']), int(all_pairs_df.at[j,'recipient'])]
    pred = pm.run(data)
    pred_rounded = 0 if pred < 0 else pred
    pred_rounded = 16 if pred_rounded > 16 else pred_rounded
    pred_list.append(pred_rounded)
  pred_list_joined = ','.join([str(x) for x in pred_list])
  matched_idx = eq_class_df.index[eq_class_df['pred_list'] == pred_list_joined].tolist()
  if len(matched_idx) == 0: # new eq class
    eq_class_df = eq_class_df.append(pd.DataFrame({
      'pred_list': [pred_list_joined],
      'terms': [terms],
      'count': [1]
    }), ignore_index=True)
  else:
    found_idx = matched_idx[0]
    found_terms = eq_class_df.at[found_idx, 'terms']
    if len(terms) < len(found_terms):
      eq_class_df.at[found_idx, 'terms'] = terms
    eq_class_df.at[found_idx, 'count'] += 1

eq_class_df.to_csv('data/flip_all_eqc.csv')

# %%
