// Read command line args
const expId = process.argv.slice(2)[0];
const cond = process.argv.slice(2)[1];


// Task settings
TOP_N = 3
EXCEPTS = 0
LEARN_ITER = 1000
GEN_ITER = 10000


// Output python script
let pyScript = `
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
tasks = pd.read_csv('../data/tasks/exp_${expId}.csv', index_col=0)
tasks = tasks[tasks['condition']=='${cond}']

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

# Learning phase A
pl = Program_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
g1 = Gibbs_sampler(pl, all_frames, task_data['learn_a'], iteration=${LEARN_ITER})
g1.run(top_n=${TOP_N}, save_prefix=f'libs/exp${expId}_${cond}_a_', save_intermediate=False)

# Gen predictions A
a_learned = pd.read_csv(f'libs/exp${expId}_${cond}_a_post_samples.csv', index_col=0, na_filter=False)
a_gen = sim_for_all(task_data['gen'], Program_lib(a_learned), ${GEN_ITER})
a_gen.to_csv(f'preds/exp_${expId}/${cond}_preds_a.csv')

# Learning phase B
pl2 = Program_lib(pd.read_csv(f'libs/exp${expId}_${cond}_a_post_samples.csv', index_col=0, na_filter=False))
pl2.update_lp_adaptor()
pl2.update_overall_lp()
g2 = Gibbs_sampler(pl2, all_frames, task_data['learn_a']+task_data['learn_b'], iteration=${LEARN_ITER}, lib_is_post=True)
g2.run(top_n=${TOP_N}, save_prefix=f'libs/exp${expId}_${cond}_b_', save_intermediate=False)

# Gen predictions B
b_learned = pd.read_csv(f'libs/exp${expId}_${cond}_b_post_samples.csv', index_col=0, na_filter=False)
b_gen = sim_for_all(task_data['gen'], Program_lib(b_learned), ${GEN_ITER})
b_gen.to_csv(f'preds/exp_${expId}/${cond}_preds_b.csv')

`;

console.log(pyScript)
