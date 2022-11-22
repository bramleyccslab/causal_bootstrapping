#%%
import numpy as np
import pandas as pd
import math

# import multiprocessing as mp
# print("Number of processors: ", mp.cpu_count())

import sys
sys.path.append('../')
from task_terms import *
from helpers import normalize, softmax, add_motor_noise

# %% Global vars
CAND_PROGRAMS = pd.read_csv('data/flip_all_eqc.csv', index_col=0)
N_PROGRAMS = len(CAND_PROGRAMS)
print(N_PROGRAMS)

# %% Prep data
config_data = pd.read_json('../for_exp/config.json')
results_col = pd.DataFrame({'result':range(16+1)})
results_col['joiner'] = 0

ALL_PAIRS = pd.DataFrame(columns=['agent', 'recipient'])
for i in range(len(config_data)):
  agent_info = config_data.agent[i].split(',')
  recipient_info = config_data.recipient[i].split(',')
  ALL_PAIRS.at[i,'agent'] = f'Egg(S{agent_info[0][1:]},O{agent_info[1][1:]})'
  ALL_PAIRS.at[i,'recipient'] = int(recipient_info[2][:-1])
ALL_PAIRS['pair_index'] = ALL_PAIRS.index
ALL_PAIRS['joiner'] = 0
ALL_OBS = pd.merge(ALL_PAIRS, results_col, how='outer', on='joiner')[['pair_index','agent','recipient','result']]

PM_LL = ALL_OBS.copy()
for i in CAND_PROGRAMS.index:
  PM_LL[f'pm_{str(i)}'] = 0
  preds = CAND_PROGRAMS.at[i, 'pred_list'].split(',')
  for pi in range(len(ALL_PAIRS)):
    predicted_idx = PM_LL[(PM_LL['pair_index']==pi)&(PM_LL['result']==int(preds[pi]))].index[0]
    PM_LL.at[predicted_idx, f'pm_{str(i)}'] = 1

PM_WEIGHTS = normalize(CAND_PROGRAMS['count'])
# PM_WEIGHTS = [1/len(CAND_PROGRAMS)]

# %%
def get_sim(program_id, pair_ids, n=50, noise=4):
  ret_data = pd.DataFrame(columns=['pair_index', 'agent', 'recipient', 'result', 'count'])
  for pi in pair_ids:
    data = PM_LL[PM_LL['pair_index']==pi][['pair_index', 'agent', 'recipient', 'result', program_id]]
    data['prob'] = add_motor_noise(list(data[program_id]), noise)
    data['count'] = 0
    i = 0
    while i < n:
      data.at[data.sample(1, weights='prob').index[0], 'count'] += 1
      i += 1
    ret_data = ret_data.append(data[['pair_index', 'agent', 'recipient', 'result', 'count']])
  return ret_data
# get_sim('pm_1', [3,7], n=50, noise=4)

def conditional_entropy(sim_data, noise=4, weights=PM_WEIGHTS, sample=False):
  post_pp = []
  for mi in range(len(CAND_PROGRAMS)): # If sample, check just a few of programs
    pm_id = f'pm_{mi}'
    pm_counts = sim_data[['count', pm_id]].copy()
    pm_counts['ll'] = softmax(pm_counts[pm_id], noise)
    pm_counts = pm_counts[pm_counts['count']>0]
    pm_counts['pp'] = pm_counts.apply(lambda row: row['ll'] ** row['count'], axis=1)
    post_pp.append(sum(pm_counts['pp']))
  if weights is not None:
    post_pp = [ a*b for (a,b) in list(zip(post_pp, weights))]
  post_pp = normalize(post_pp)
  return -sum([x * math.log(x) for x in post_pp])

# %%
trials_df = pd.DataFrame(columns=['pair_index', 'agent', 'recipient','EIG'])
# # For testing
# CAND_PROGRAMS = CAND_PROGRAMS.sample(3)
# N_PROGRAMS = len(CAND_PROGRAMS)

prior_entropy = -sum([x * math.log(x) for x in PM_WEIGHTS])

# Get learned pair indices
# learned_pair_idx = [x+1 for x in [23, 42, 61, 35, 50, 65, 27, 31, 35]] # config_data.task_id := index+1
learned_pair_idx = [22, 41, 60, 26, 30, 34]
task_phase = ALL_PAIRS[ALL_PAIRS.index.isin(learned_pair_idx)]

# Get the first one
candidate_pairs = ALL_PAIRS[~ALL_PAIRS['agent'].isin(task_phase['agent'])].reset_index(drop=True)
pair_eigs = []
for pi in range(len(candidate_pairs)):
  info_gain = []
  for mi in range(len(CAND_PROGRAMS)):
    pm_id = f'pm_{mi}'
    sim_counts = get_sim(pm_id, [pi])
    pm_lls = PM_LL[PM_LL['pair_index']==pi]
    post_df = pd.merge(sim_counts, pm_lls, how='left', on=['pair_index', 'agent', 'recipient', 'result'])
    info_gain.append(prior_entropy - conditional_entropy(post_df))
  info_gain = [ a*b for (a,b) in list(zip(info_gain, PM_WEIGHTS))] # Weighted
  pair_eigs.append(sum(info_gain)/len(info_gain)) # Weighted average

best_pair = candidate_pairs[candidate_pairs.index==pair_eigs.index(max(pair_eigs))]
best_pair['EIG'] = max(pair_eigs)
trials_df = trials_df.append(best_pair, ignore_index=True)
print(best_pair)
trials_df.to_csv('../data/flip_eig_trials.csv')

# Build greedily
while (len(trials_df) < 20):
  prev_pair_ids = list(trials_df['pair_index'])
  #candidate_pairs = candidate_pairs[~candidate_pairs['pair_index'].isin(prev_pair_ids)].reset_index(drop=True)
  candidate_pairs = candidate_pairs[~candidate_pairs['agent'].isin(trials_df['agent'])].reset_index(drop=True)
  pair_eigs = []
  for pi in range(len(candidate_pairs)):
    info_gain = []
    for mi in range(len(CAND_PROGRAMS)):
      pm_id = f'pm_{mi}'
      sim_counts = get_sim(pm_id, prev_pair_ids+[pi])
      pm_lls = PM_LL[PM_LL['pair_index'].isin(prev_pair_ids+[pi])]
      post_df = pd.merge(sim_counts, pm_lls, how='left', on=['pair_index', 'agent', 'recipient', 'result'])
      info_gain.append(prior_entropy - conditional_entropy(post_df))
    pair_eigs.append(sum(info_gain)/len(info_gain)) # Average information gain, no weighting
  best_pair = candidate_pairs[candidate_pairs.index==pair_eigs.index(max(pair_eigs))]
  best_pair['EIG'] = max(pair_eigs)
  trials_df = trials_df.append(best_pair, ignore_index=True)
  print(best_pair)
  trials_df.to_csv('../data/flip_eig_trials.csv')

trials_df.to_csv('../data/flip_eig_trials.csv')
