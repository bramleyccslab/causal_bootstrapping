# %% Imports
import random
from multiprocessing import Pool

import pandas as pd
from Rational_rules import *

# %% Model specification
productions = [
  ['S', ['add(A,A)', 'sub(A,A)', 'mult(A,A)']],
  ['A', ['S', 'B']],
  ['B', ['C', 'D']],
  ['C', ['stripe(d)', 'spot(d)', 'stick(d)']],
  ['D', ['0', '1', '2', '3']]
]
rat_rules_model = Rational_rules(productions, cap=100)
random.seed(10)

# %% Prep data
exp_data = pd.read_json('../for_exp/config.json')
exp_ids = {
  'learn_a': [23, 42, 61],
  'learn_b': [35, 50, 65],
  'learn_c': [27, 31, 35],
}
exp_ids_list = exp_ids['learn_a'] + exp_ids['learn_b'] + exp_ids['learn_c']

ld_all = {}
for (ix, id) in enumerate(exp_ids_list):
  data = exp_data[exp_data.trial_id==id]
  dt_name = f'ld{ix+1}'

  _, agent, recipient, result = list(data.iloc[0])
  converted = (f'Egg(S{agent[1]},O{agent[4]})', recipient[-2], result[-2])
  ld_all[dt_name] = converted


# %% Learning phase
def trainings (n):
  sampled_rules = pd.DataFrame({
    'rule': pd.Series(dtype='str'), 'log_prob': pd.Series(dtype='float'),
  })
  batch1 = sampled_rules.copy()
  batch2 = sampled_rules.copy()
  batch3 = sampled_rules.copy()
  batch12 = sampled_rules.copy()
  batch13 = sampled_rules.copy()

  def save_dfs(prefix):
    batch1.drop_duplicates(ignore_index=True).to_csv(f'{prefix}1.csv')
    batch2.drop_duplicates(ignore_index=True).to_csv(f'{prefix}2.csv')
    batch3.drop_duplicates(ignore_index=True).to_csv(f'{prefix}3.csv')
    batch12.drop_duplicates(ignore_index=True).to_csv(f'{prefix}12.csv')
    batch13.drop_duplicates(ignore_index=True).to_csv(f'{prefix}13.csv')

  k = 0
  while k<n:
    generated = rat_rules_model.generate_tree()
    if generated is not None:
      # evaluate on data
      learned = {}
      for dt in ld_all.items():
        dt_name, data = dt
        learned[dt_name] = Rational_rules.evaluate(generated, data)[0] # Just the bool
      # add to df
      to_append = pd.DataFrame({'rule': [generated[0]], 'log_prob':[generated[1]]})
      if (learned['ld1'] and learned['ld2'] and learned['ld3']):
        batch1 = pd.concat([batch1, to_append], ignore_index=True)
      if (learned['ld4'] and learned['ld5'] and learned['ld6']):
        batch2 = pd.concat([batch2, to_append], ignore_index=True)
      if (learned['ld7'] and learned['ld8'] and learned['ld9']):
        batch3 = pd.concat([batch3, to_append], ignore_index=True)
      if (
        learned['ld1'] and learned['ld2'] and learned['ld3'] and
        learned['ld4'] and learned['ld5'] and learned['ld6']
      ):
        batch12 = pd.concat([batch12, to_append], ignore_index=True)
      if (
        learned['ld1'] and learned['ld2'] and learned['ld3'] and
        learned['ld7'] and learned['ld8'] and learned['ld9']
      ):
        batch13 = pd.concat([batch13, to_append], ignore_index=True)
    k+=1

  save_dfs(f'data/process_{n}/batch')

# %%
# LEARN_ITERS = [10,50,100] + list(range(200, 1001, 200)) + list(range(2000, 10001, 2000)) + list(range(20000, 100001, 20000))
# LEARN_ITERS = list(range(100, 1001, 100)) + list(range(2000, 10001, 1000))
LEARN_ITERS = list(range(100, 1001, 100))

if __name__ == '__main__':
  with Pool(5) as p:
    p.map(trainings, [n for n in LEARN_ITERS])
