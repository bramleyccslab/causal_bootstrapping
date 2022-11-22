
import sys
sys.path.append('../')
from program_sim import *
from task_terms import *
from program_inf import *

# Read task data
task_data = {
  'learn_a': [],
  'learn_b': [],
  'gen': [],
}
tasks = pd.read_csv('../../data/tasks/exp_1.csv', index_col=0)
tasks = tasks[tasks['condition']=='decon']

learn_a_tasks = tasks[tasks['batch']=='A'].reset_index()
for i in learn_a_tasks.index:
  task_dt = learn_a_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['learn_a'].append(task_obj)

learn_b_tasks = tasks[tasks['batch']=='B'].reset_index()
for i in learn_b_tasks.index:
  task_dt = learn_b_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['learn_b'].append(task_obj)

gen_tasks = tasks[tasks['batch']=='gen'].reset_index()
for i in gen_tasks.index:
  task_dt = gen_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['gen'].append(task_obj)


# Run sim
all_frames = pd.read_csv('../data/task_frames.csv',index_col=0)
pl = Program_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))

# Gen predictions A
a_gen = sim_for_all(task_data['gen'], pl, 10000)
a_gen.to_csv(f'preds/decon_preds_a.csv')

b_gen = sim_for_all(task_data['gen'], pl, 10000)
b_gen.to_csv(f'preds/decon_preds_b.csv')
