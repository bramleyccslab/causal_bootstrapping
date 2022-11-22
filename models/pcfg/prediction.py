# %%
import math
import pandas as pd
from Rational_rules import *

from multiprocessing import Pool


# %%
# initialize model
N_TERMS = 17
productions = [
  ['S', ['add(A,A)', 'sub(A,A)', 'mult(A,A)']],
  ['A', ['S', 'B']],
  ['B', ['C', 'D']],
  ['C', ['stripe(d)', 'spot(d)', 'stick(d)']],
  ['D', ['0', '1', '2', '3']]
]
rt_model = Rational_rules(productions, cap=100)

# %%
# get preds per condition
configs = [
  ('batch1', 'construct_preds_a'),
  ('batch12', 'construct_preds_b'),

  ('batch2', 'decon_preds_a'),
  ('batch12', 'decon_preds_b'),

  ('batch1', 'combine_preds_a'),
  ('batch13', 'combine_preds_b'),

  ('batch3', 'flip_preds_a'),
  ('batch13', 'flip_preds_b'),
]


# %%
def get_prediction (n):
  for df, cond in configs:
    # read data
    task_condition = cond.split('_')[0]
    exp_id = 3 if task_condition == 'flip' else 1

    tasks = pd.read_csv(f'../../data/tasks/exp_{str(exp_id)}.csv', index_col=0)
    tasks = tasks[tasks['condition']==task_condition]
    gen_tasks = tasks[tasks['batch']=='gen'].reset_index()

    gen_data = []
    for i in gen_tasks.index:
      task_dt = gen_tasks.iloc[i]
      task_obj = (f"Egg(S{task_dt['stripe']},O{task_dt['dot']})", str(task_dt['block']), str( task_dt['result_block']))
      gen_data.append(task_obj)

    # read learned rules
    rules = pd.read_csv(f'data/process_{str(n)}/{df}.csv', index_col=0)

    if len(rules) < 1:
      # use a sampled prior
      rules = pd.DataFrame({
        'rule': pd.Series(dtype='str'), 'log_prob': pd.Series(dtype='float'),
      })
      k = 0
      while k<n:
        generated = rt_model.generate_tree()
        if generated is not None:
          to_append = pd.DataFrame({'rule': [generated[0]], 'log_prob':[generated[1]]})
          rules = pd.concat([rules, to_append], ignore_index=True)
        k+=1
      rules = rules.drop_duplicates(ignore_index=True)

    # Initialize prediction df
    predictions = pd.DataFrame({'terms': [str(x) for x in list(range(N_TERMS))]})

    # Get predictions
    for (ix, gd) in enumerate(gen_data):
      probs = [0.]*N_TERMS
      for rix in rules.index:
        rule, lp = list(rules.iloc[rix])
        term, term_lp = rt_model.predict((rule, lp), gd)
        probs[int(term)] += math.exp(term_lp)
      normed_probs = [x/sum(probs) for x in probs]
      df_gen = pd.DataFrame({f'prob_{ix+1}': normed_probs})
      predictions = pd.concat([predictions, df_gen], axis=1)

    # Save
    predictions.to_csv(f'data/process_{str(n)}/{cond}.csv')


# %%
# LEARN_ITERS = [10,50,100] + list(range(200, 1001, 200)) + list(range(2000, 10001, 2000)) + list(range(20000, 100001, 20000))
# LEARN_ITERS = list(range(100, 1001, 100)) + list(range(2000, 10001, 1000))
LEARN_ITERS = list(range(100, 1001, 100))

if __name__ == '__main__':
  with Pool(5) as p:
    p.map(get_prediction, [n for n in LEARN_ITERS])
