
# %%
import math
import numpy as np
import pandas as pd
from pandas.io.stata import StataMissingValue
pd.set_option('mode.chained_assignment', None)

from task_terms import *
from helpers import secure_list, names_to_string, print_name, normalize, softmax
from program_lib import Program_lib

# %%
class Gibbs_sampler:
  def __init__(self, program_lib, frames, data_list, iteration, burnin=0, lib_is_post=False):
    input_lib = program_lib.content
    self.init_lib = input_lib.copy()                        # Initial program library
    self.post_samples = input_lib[input_lib['is_init']==1]  # Place holder for posterior samples
    self.sample_cache = None                                # Temp cache for each iteration

    self.frames = frames
    self.frames['prob'] = self.frames.apply(lambda row: math.exp(row['log_prob']), axis=1)

    self.data = secure_list(data_list)
    self.iter = iteration
    self.burnin = burnin
    self.lib_is_post = lib_is_post

  # Frames => programs consistent with data
  def find_programs(self, iter_log, pm_lib, frame_sample=20, fs_cap=100, exceptions_allowed=0):
    pl = Program_lib(pm_lib)
    data = self.data
    frames_left = self.frames.copy()
    filtered = pd.DataFrame({'terms': [], 'comp_lp': [], 'log_prob': [], 'n_exceptions': []})
    ns = 0
    while (len(filtered)) < 1 and ns < fs_cap+1:
      ns += 1
      # Sample frames
      if len(frames_left) <= frame_sample:
        sampled_frames = frames_left.copy()
      else:
        sampled_frames = frames_left.sample(n=frame_sample, weights='prob').reset_index(drop=True)
      frames_left = frames_left[~frames_left['terms'].isin(sampled_frames['terms'])]
      for k in range(len(sampled_frames)):
        # Unfold programs wrt current library
        all_programs = pl.unfold_programs_with_lp(sampled_frames.iloc[k].at['terms'], sampled_frames.iloc[k].at['log_prob'], data)
        # Filter consistency wrt learning data
        if len(all_programs) > 0:
          for d in range(len(data)):
            all_programs[f'consistent_{d}'] = all_programs.apply(lambda row: pl.check_program(row['terms'], data[d]), axis=1)
          all_programs['total_consistency'] = all_programs[all_programs.columns[pd.Series(all_programs.columns).str.startswith('consistent')]].sum(axis=1)
          all_programs['n_exceptions'] = len(data) - all_programs['total_consistency']
          passed_pm = all_programs.query(f'n_exceptions<={exceptions_allowed}')
          # Likelihood with exceptions
          passed_pm['log_prob'] = passed_pm['log_prob'] - 2*passed_pm['n_exceptions'] # likelihood: exp(-2 * n_exceptions)
          print(f"[{iter_log}|{k}/{len(sampled_frames)}, -{ns}th] {sampled_frames.iloc[k].at['terms']}: {len(passed_pm)} passed") if len(iter_log)>0 else None
          filtered = filtered.append(passed_pm[['terms', 'comp_lp', 'log_prob', 'n_exceptions']], ignore_index=True)
    return filtered

  # Sample extracted programs for reuse
  def sample_extraction(self, filtered, top_n=1, sample=True, base=0):
    if len(filtered) <= top_n or sample == 0:
      to_add = filtered.copy()
    else:
      # Sample according to log_prob (adaptor grammar prior considered)
      filtered['prob'] = filtered.apply(lambda row: math.exp(row['log_prob']), axis=1)
      filtered['prob'] = normalize(filtered['prob']) if base == 0 else softmax(filtered['prob'], base)
      to_add = filtered.sample(n=top_n, weights='prob')
    # Prep extraction in required format
    to_add['arg_types'] = 'egg_num'
    to_add['return_type'] = 'num'
    to_add['type'] = 'program'
    to_add['count'] = 1
    if len(to_add) > 1:
      extracted = (to_add
        .groupby(by=['terms','arg_types','return_type','type'], as_index=False)
        .agg({'count': pd.Series.count, 'comp_lp': pd.Series.max, 'log_prob': pd.Series.max})
        .reset_index(drop=1))
    else:
      extracted = to_add[['terms','arg_types','return_type','type','count','comp_lp','log_prob']]
    return extracted

  @staticmethod # Add extractions to program lib; use_ag: update adaptor grammar prior
  def merge_lib(extracted_df, target_df, use_ag=True):
    if extracted_df is None or len(extracted_df) < 1:
      return target_df
    else:
      merged_df = pd.merge(target_df, extracted_df, how='outer', on=['terms','arg_types','return_type','type']).fillna(0)
      # Increase counter
      merged_df['count'] = merged_df['count_x'] + merged_df['count_y']
      set_df = (merged_df
        .query('count_x>0')[['terms','arg_types','return_type','type','is_init','count','comp_lp_x']]
        .rename(columns={'comp_lp_x': 'comp_lp'}))
      # Take care of newly-created programs
      to_set_df = (merged_df
        .query('count_x==0')[['terms','arg_types','return_type','type','count','comp_lp_y']]
        .rename(columns={'comp_lp_y': 'comp_lp'}))
      to_set_df['is_init'] = 0
      # Merge & take care of probabilities
      temp_lib = Program_lib(pd.concat([set_df, to_set_df], ignore_index=True))
      if use_ag:
        temp_lib.update_lp_adaptor()
        temp_lib.update_overall_lp()
      return temp_lib.content.copy()

  # Main sampling procedure
  def run(
    self, top_n=1, sample=True, frame_sample=20, fs_cap=100, exceptions_allowed=0, base=0,
    logging=True, save_prefix='', save_intermediate=False, save_iters=[],
  ):
    for i in range(self.iter):
      iter_log = f'Iter {i+1}/{self.iter}' if logging else ''
      # Prep starting point
      if self.lib_is_post:
        df_init = self.init_lib[self.init_lib['is_init']==1]
        df_posts = self.init_lib[self.init_lib['is_init']==0]
        df_sampled = df_posts.sample(top_n+exceptions_allowed, weights='count')
        df_to_start = pd.concat([df_init, df_sampled], ignore_index=True)
        df_to_start['count'] = 1.0
        helper_pm = Program_lib(df_to_start)
        helper_pm.update_lp_adaptor()
        helper_pm.update_overall_lp()
        init_lib = helper_pm.content
      else:
        init_lib = self.init_lib
      # Prep current lib
      if i > 0:
        cur_pm = self.merge_lib(self.sample_cache.copy(), init_lib.copy())
      else:
        cur_pm = init_lib.copy()
      filtered = self.find_programs(iter_log, cur_pm, frame_sample, fs_cap, exceptions_allowed)
      # Extract resusable bits
      if len(filtered) < 1:
        print('Nothing consistent, skipping to next...') if logging else None # TODO: random sample?
      else:
        extracted = self.sample_extraction(filtered, top_n, sample, base)
        print(extracted) if logging else None
        # Add to cache => use in next iteration
        self.sample_cache = extracted.copy()
        # Collect for posterior
        if i >= self.burnin:
          self.post_samples = self.merge_lib(extracted.copy(), self.post_samples.copy(), use_ag=False)
        # Save
        if len(save_prefix) > 0:
          self.post_samples.to_csv(f'{save_prefix}post_samples.csv')
          if save_intermediate:
            padding = len(str(self.iter))
            filtered.to_csv(f'{save_prefix}filtered_{str(i+1).zfill(padding)}.csv')
          if len(save_iters) > 0 and i in save_iters:
            self.post_samples.to_csv(f'{save_prefix}post_samples_{i}.csv')

            # extracted.to_csv(f'{save_prefix}extracted_{str(i+1).zfill(padding)}.csv')
            # cur_pm.to_csv(f'{save_prefix}curpm_{str(i+1).zfill(padding)}.csv')
            # self.post_samples.to_csv(f'{save_prefix}post_{str(i+1).zfill(padding)}.csv')


# # %% Debug
# all_data = pd.read_json('for_exp/config.json')
# task_ids = {
#   'learn_a': [23, 42, 61],
#   'learn_b': [35, 50, 65],
#   'gen': [82, 8, 20, 4, 98, 48, 71, 40],
# }
# task_ids['gen'].sort()

# task_data = {}
# for item in task_ids:
#   task_data[item] = []
#   for ti in task_ids[item]:
#     transformed = {}
#     data = all_data[all_data.trial_id==ti]
#     _, agent, recipient, result = list(data.iloc[0])
#     transformed['agent'] = eval(f'Egg(S{agent[1]},O{agent[4]})')
#     transformed['recipient'] = int(recipient[-2])
#     transformed['result'] = int(result[-2])
#     task_data[item].append(transformed)

# # %%
# all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
# pl = Program_lib(pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False))
# g1 = Gibbs_sampler(pl, all_frames, task_data['learn_a'], iteration=10)
# g1.run(top_n=3, save_prefix='test/tt_')

# pp = Program_lib(pd.read_csv('test/tt_post_samples.csv', index_col=0, na_filter=False))
# g2 = Gibbs_sampler(pp, all_frames, task_data['learn_b'], iteration=10, lib_is_post=True)
# g2.run(top_n=3, save_prefix='test/t2_', save_intermediate=1)

# %%
