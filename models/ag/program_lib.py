
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import numpy as np
from numpy import random as np_random
from math import log, exp
from itertools import product as itertools_product

from task_terms import *
from helpers import args_to_string, names_to_string, term_to_dict, secure_list, print_name

# %%
class Program_lib_light:
  def __init__(self, df):
    self.content = df
  def add(self, entry_list):
    entry_list = secure_list(entry_list)
    for et in entry_list:
      # check existence
      if isinstance(et, dict) == 0:
        et = term_to_dict(et)
      found_terms = self.content.query('terms=="'+et['terms']+'"&arg_types=="'+et['arg_types']+'"&return_type=="'+et['return_type']+'"&type=="'+et['type']+'"')
      if len(found_terms) > 0:
        self.content.at[found_terms.index.values[0],'count'] += 1
      else:
        self.content = self.content.append(pd.DataFrame({
          'terms': [et['terms']],
          'arg_types': [et['arg_types']],
          'return_type': [et['return_type']],
          'type': [et['type']],
          'count': [1],
        }), ignore_index=True)

class Program_lib(Program_lib_light):
  def __init__(self, df):
    Program_lib_light.__init__(self, df)
    self.ERROR_TERM = {'terms': 'ERROR', 'arg_types': '', 'return_type': '', 'type': 'ERROR'}
    self.SET_MARKERS = set(list(self.content[self.content['type']=='base_term'].return_type))

  # List all the possile objects (task specific)
  def get_all_objs(self):
    eggs_df = pd.DataFrame({'terms': [], 'count':[]})
    stripe_df = self.content.query('return_type=="stripe"&type=="base_term"')
    dot_df = self.content.query('return_type=="dot"&type=="base_term"')
    for s in range(len(stripe_df)):
      for o in range(len(dot_df)):
        egg_feats = [
          stripe_df.iloc[s].at['terms'],
          dot_df.iloc[o].at['terms'],
        ]
        counts = [
          stripe_df.iloc[s].at['count'],
          dot_df.iloc[o].at['count'],
        ]
        eggs_df = eggs_df.append(pd.DataFrame({'terms': [f'Egg({",".join(egg_feats)})'], 'count': [sum(counts)]}), ignore_index=True)
    total = eggs_df['count'].sum()
    eggs_df['log_prob'] = eggs_df.apply(lambda row: math.log(row['count']/total), axis=1)
    return eggs_df[['terms', 'log_prob']]

  # Sample base terms (task specific)
  def sample_base(self, type, add):
    if type == 'obj':
      stripe = self.sample_base('stripe', add)
      dot = self.sample_base('dot', add)
      egg = f'Egg({stripe},{dot})'
      return {'terms': egg, 'arg_types': '', 'return_type': 'egg', 'type': 'base_term'}
    else:
      bases = self.content.query(f'return_type=="{type}"&type=="base_term"')
      if bases is None or bases.empty:
        print('No base terms found!')
        return self.ERROR_TERM
      else:
        sampled = bases.sample(n=1, weights='count').iloc[0].to_dict()
        if add:
          self.add(sampled)
        return sampled

  # Flat priors for PCFG
  def initial_comp_lp(self):
    grouped = self.content.groupby(['arg_types', 'return_type', 'type']).sum().reset_index()
    grouped['comp_lp'] = grouped.apply(lambda row: math.log(1/row['count']), axis=1)
    self.content = pd.merge(self.content, grouped[['arg_types', 'return_type', 'type', 'comp_lp']], on=['arg_types', 'return_type', 'type'], how='left')
    return None

  # Adaptor grammar prior in log, see Percy Liang et al. 2010
  def update_lp_adaptor(self, alpha=1, d=0.2):
    df = self.content.copy()
    df['sum_comp_lp'] = df['count'] * df['comp_lp']
    grouped = df.groupby(['arg_types', 'return_type', 'type']).agg(
      type_count = ('count','count'), total_comp = ('sum_comp_lp','sum'),
    ).reset_index()
    temp = pd.merge(self.content, grouped, on=['arg_types', 'return_type', 'type'], how='left')
    temp['num_1'] = temp['type_count']*alpha + d*(temp['type_count']*(temp['type_count']+1)/2 - temp['type_count'])
    temp['num_2'] = temp['total_comp']
    temp['num_3'] = (temp['count']-1)*temp['count']/2 - d*(temp['count']-1)
    temp['denom'] = temp['type_count']*alpha + (temp['type_count']-1)*temp['type_count']/2
    temp['adaptor_lp'] = temp['num_1'] + temp['num_2'] + temp['num_3'] - temp['denom']
    self.content = (pd.merge(
      self.content[['terms', 'arg_types', 'return_type', 'type', 'is_init', 'count', 'comp_lp']],
      temp[['terms', 'arg_types', 'return_type', 'type', 'adaptor_lp']],
      on=['terms', 'arg_types', 'return_type', 'type'],
      how='left'))
    return None

  def update_overall_lp(self, tune = 1):
    bases = self.content[self.content['type']!='program']
    composes = self.content[self.content['type']=='program']
    bases['log_prob'] = bases['comp_lp']
    composes['log_prob'] = composes['adaptor_lp'] + tune*composes['comp_lp']
    self.content = pd.concat([bases, composes], ignore_index=True)
    return None

  # Program generation helpers
  def get_cached_program(self, type_signature, include_base_terms=False):
    arg_t, ret_t = type_signature
    exclusion = '' if include_base_terms else '&type!="base_term"'
    matched_pms = self.content.query(f'arg_types=="{args_to_string(arg_t)}"&return_type=="{ret_t}"{exclusion}')
    return matched_pms if not matched_pms.empty else None

  def get_matched_program(self, return_type, filter_pm=False):
    filter_program = '&type!="program"' if filter_pm else ''
    matched_pms = self.content.query(f'return_type=="{return_type}"&type!="base_term"{filter_program}')
    return matched_pms if not matched_pms.empty else None

  def sample_program(self, p_source, add=False, weight_col = 'count'):
    if p_source is None:
      print('No cache found!')
      return self.ERROR_TERM
    else:
      sampled = p_source.sample(n=1, weights=weight_col).iloc[0].to_dict()
      if add:
        self.add(sampled)
      return sampled

  def sample_cached_program(self, type_signature, add=False):
    cached = self.get_cached_program(type_signature)
    if cached is None:
      print('No cache found!')
      return self.ERROR_TERM
    else:
      return self.sample_program(cached, add)

  def sample_matched_program(self, return_type, filter_pm = False, add=False):
    matched = self.get_matched_program(return_type, filter_pm)
    if matched is None:
      print('No match found!')
      return self.ERROR_TERM
    else:
      sampled = self.sample_program(matched, add)
      return sampled

  @staticmethod
  def sample_router(arg_list, free_index):
    assert len(arg_list) > 0, 'No arguments for router!'
    if free_index < 0:
      return 'B' * len(arg_list)
    else:
      return ''.join([np_random.choice(['C', 'B', 'S', 'K']) for _ in arg_list])

  @staticmethod
  def get_all_routers(arg_list, left_arg_list, free_index):
    assert len(arg_list) > 0, 'No arguments for router!'
    candidates = ['B']
    if free_index >= 0:
      candidates.append('K')
    if free_index > 0: #and len(arg_list) <= len(left_arg_list):
      candidates.append('C')
      candidates.append('S')
    routers = []
    for r in list(itertools_product(candidates, repeat=len(arg_list))):
      routers.append(''.join(r))
    return routers

  # Tail-recursion; righthand-side tree
  def generate_program(self, type_signature, cur_step=0, max_step=5, alpha=1, d=0.2, add=True):
    if cur_step > max_step:
      print('Max step exceeded!')
      return self.ERROR_TERM
    else:
      # Pitman-Yor process
      cached = self.get_cached_program(type_signature)
      if cached is None:
        cache_param = 1
      else:
        Nt = len(cached)
        Ct = sum(cached['count'])
        cache_param = (alpha+Nt*d)/(alpha+Ct)
      # print(f'threashold: {cache_param}')
      if np_random.random() < cache_param: # Construct
        cur_step += 1
        arg_t, ret_t = type_signature
        if len(arg_t) < 1:
          # return a base term
          base_term = self.sample_base(ret_t, add)
          return base_term
        else:
          # generate new program
          left = self.sample_matched_program(ret_t, True, add)
          left_args = left['arg_types'].split('_')
          free_index = len(left_args) - 2
          router = self.sample_router(arg_t, free_index)
          routed_args = eval(router).run({'left': [], 'right': []}, arg_t)
          # expand left side until no un-filled arguments
          left_pm = self.expand_program(left, routed_args['left'], free_index, cur_step, max_step, alpha, d, add)
          right_pm = self.generate_program([routed_args['right'], left_args[-1]], cur_step, max_step, alpha, d, add)
          terms = [router, left_pm['terms'], right_pm['terms']]
          program_dict = {
            'terms': names_to_string(terms),
            'arg_types': args_to_string(type_signature[0]),
            'return_type': type_signature[1],
            'type': 'program',
          }
          # add to program lib
          if add:
            self.add(program_dict) if 'ERROR' not in program_dict['terms'] else None
          return program_dict
      else:
        cached['weight'] = (cached['count']-d)/(Ct-Nt*d)
        sampled = self.sample_program(cached, add, weight_col='weight')
        return sampled

  # Lefthand-side tree
  def expand_program(self, candidate, arg_list, free_index, cur_step, max_step, alpha, d, add):
    if free_index < 0:
      return candidate
    else:
      left_args = candidate['arg_types'].split('_')
      if len(arg_list) < 1:
        left_pm = self.expand_program(candidate, arg_list, free_index - 1, cur_step, max_step, alpha, d, add)
        right_pm = self.generate_program([arg_list, left_args[free_index]], cur_step, max_step, alpha, d, add)
        terms = [left_pm['terms'], right_pm['terms']]
      else:
        router = self.sample_router(arg_list, free_index-1)
        routed_args = eval(router).run({'left': [], 'right': []}, arg_list)
        left_pm = self.expand_program(candidate, routed_args['left'], free_index-1, cur_step, max_step, alpha, d, add)
        right_pm = self.generate_program([routed_args['right'], left_args[free_index]], cur_step, max_step, alpha, d, add)
        terms = [router, left_pm['terms'], right_pm['terms']]
      return {
        'terms': names_to_string(terms),
        'arg_types': candidate['arg_types'],
        'return_type': candidate['return_type'],
        'type': 'program',
      }

  def typed_bfs(self, type_signature, depth = 1):
    programs_df = pd.DataFrame({'terms': [], 'log_prob': []})
    arg_types, ret_type = type_signature
    if len(arg_types) < 1:
      programs_df = programs_df.append(pd.DataFrame({'terms': [ret_type], 'log_prob': [0]}), ignore_index=True)
      return programs_df
    else:
      # Compress direct matches
      if self.get_cached_program(type_signature) is not None:
        programs_df = programs_df.append(pd.DataFrame({'terms': [f'PM("{args_to_string(arg_types)}_{ret_type}")'], 'log_prob': [0]}), ignore_index=True)
      # return direct matches
      if depth < 1:
        return programs_df
      # enumerate recursively
      else:
        left_trees = self.get_matched_program(ret_type, True)
        for i in left_trees.index:
          left_terms = left_trees.at[i, 'terms']
          left_arg_types = left_trees.at[i, 'arg_types'].split('_')
          free_index = len(left_arg_types)-1
          # get routers
          routers = self.get_all_routers(arg_types, left_arg_types, free_index)
          for rt in routers:
            routed_args = eval(rt).run({'left': [], 'right': []}, arg_types)
            left = self.typed_expand(left_terms, left_arg_types, free_index-1, routed_args['left'], depth)
            right = self.typed_bfs([routed_args['right'],left_arg_types[free_index]], depth-1)
            if len(left) > 0 and len(right) > 0:
              programs_df = programs_df.append(self.combine_terms(left, right, rt, log(1/len(routers))), ignore_index=True)
        return programs_df

  def typed_expand(self, left_term, left_arg_types, free_index, args, depth):
    if free_index < 0:
      return pd.DataFrame({'terms': [ left_term ], 'log_prob': [0]})
    else:
      if len(args) < 1:
        left = self.typed_expand(left_term, left_arg_types, free_index-1, [], depth)
        right = self.typed_bfs([[],left_arg_types[free_index]], depth-1)
        return self.combine_terms(left, right)
      else:
        routers = self.get_all_routers(args, left_arg_types, free_index)
        terms_df = pd.DataFrame({'terms': [], 'log_prob': []})
        for rt in routers:
          routed_args = eval(rt).run({'left': [], 'right': []}, args)
          left = self.typed_expand(left_term, left_arg_types, free_index-1, routed_args['left'], depth)
          right = self.typed_bfs([routed_args['right'], left_arg_types[free_index]], depth-1)
          if len(left) > 0 and len(right) > 0:
            terms_df = terms_df.append(self.combine_terms(left, right, rt, log(1/len(routers))))
      return terms_df

  @staticmethod
  def combine_terms(left_df, right_df, router = '', router_lp = 0):
    left_df = left_df.add_prefix('left_'); left_df['key'] = 0
    right_df = right_df.add_prefix('right_'); right_df['key'] = 0
    combined = left_df.merge(right_df, how='outer')
    if len(router) < 1:
      combined['terms'] = '[' + combined['left_terms'] + ',' + combined['right_terms'] + ']'
      combined['log_prob'] = combined['left_log_prob'] + combined['right_log_prob']
    else:
      combined['terms'] = '[' + router + ',' + combined['left_terms'] + ',' + combined['right_terms'] + ']'
      combined['log_prob'] = combined['left_log_prob'] + combined['right_log_prob'] + router_lp
    return combined[['terms', 'log_prob']]

  @staticmethod
  def query_obj_lp(obj, df):
    return df.query(f'terms=="{obj}"').log_prob.values[0]

  def unfold_programs_with_lp(self, terms, log_prob, data):
    programs = self.unfold_program(terms, data)
    programs['comp_lp'] = programs['comp_lp'] + log_prob
    programs['log_prob'] = programs['log_prob'] + log_prob
    return programs

  @staticmethod
  def iter_compose_programs(terms_list, cp_list, lp_list):
    programs_list = list(itertools_product(*terms_list))
    programs_list_agg = [','.join(p) for p in programs_list]
    comp_lp_list = list(itertools_product(*cp_list))
    comp_lp_list_agg = [sum(x) for x in comp_lp_list]
    log_probs_list = list(itertools_product(*lp_list))
    log_probs_list_agg = [sum(x) for x in log_probs_list]
    return pd.DataFrame({'terms': programs_list_agg, 'comp_lp':comp_lp_list_agg, 'log_prob': log_probs_list_agg})

  # Task-specific customization
  def unfold_program(self, terms, data):
    if terms[:2]=='PM':
      pm = eval(terms)
      unfolded = self.content.query(f'arg_types=="{args_to_string(pm.arg_types)}"&return_type=="{pm.return_type}"&type=="program"')
      if len(unfolded) > 0:
        return unfolded[['terms', 'comp_lp', 'log_prob']]
      else:
        return pd.DataFrame({'terms': [], 'comp_lp': [], 'log_prob': []})
    else:
      programs_list = []
      comp_lps_list = []
      log_probs_list = []
      term_list = terms.split(',')
      all_obs = self.get_all_objs()
      for i in range(len(term_list)):
        t = term_list[i]
        tm = t.strip('[]')
        if tm in list(self.SET_MARKERS):
          unfolded = self.content.query(f'return_type=="{tm}"&type=="base_term"')
          unfolded_terms = list(unfolded['terms'])
          unfolded_cps = list(unfolded['comp_lp'])
          unfolded_lps = list(unfolded['log_prob'])
        elif tm == 'egg':
          unfolded_terms = list(set([obs['agent'].name for obs in data]))
          unfolded_lps = [self.query_obj_lp(x, all_obs) for x in unfolded_terms]
          unfolded_cps = unfolded_lps.copy()
        elif 'PM' in tm:
          pm = eval(tm)
          qs = '&type=="program"' if (pm.arg_types == ['obj'] and pm.return_type == 'obj') else ''
          unfolded = self.content.query(f'arg_types=="{args_to_string(pm.arg_types)}"&return_type=="{pm.return_type}"{qs}')
          unfolded_terms = list(unfolded['terms'])
          unfolded_cps = list(unfolded['comp_lp'])
          unfolded_lps = list(unfolded['log_prob'])
        elif eval(tm).ctype == 'router':
          unfolded_terms = [tm]
          unfolded_cps = [0] # Taken care of by the frame base lp
          unfolded_lps = [0]
        elif eval(tm).ctype == 'primitive':
          unfolded_terms = [tm]
          unfolded_lps = list(self.content.query(f'terms=="{tm}"&type=="primitive"').log_prob)
          unfolded_cps = unfolded_lps.copy()
        else:
          print('Unknow term!')
        programs_list.append([t.replace(tm, u) for u in unfolded_terms])
        comp_lps_list.append(unfolded_cps)
        log_probs_list.append(unfolded_lps)
      return self.iter_compose_programs(programs_list, comp_lps_list, log_probs_list)

  @staticmethod
  def check_program(terms, data):
    result = Program(eval(terms)).run([data['agent'], data['recipient']])
    return result == data['result']

# # %%
# pm_task = pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False)[['terms', 'arg_types', 'return_type', 'type', 'is_init', 'count']]
# pl = Program_lib(pm_task)

# pl.initial_comp_lp()
# pl.update_lp_adaptor()
# pl.content.to_csv('data/task_pm.csv')
# # Edit programs comp_lp manually for now

# pl = Program_lib(pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False))
# pl.update_overall_lp()
# pl.content.to_csv('data/task_pm.csv')

# pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
# pl = Program_lib(pm_init)
# # t = [['egg', 'num'], 'num']

# # rf = pl.typed_bfs(t,1)
# rf.to_csv('data/task_frames.csv')

# rf2 = pl.typed_bfs(t,2)
# rf2.to_csv('data/task_frames_2.csv')

# pm_extended = pd.read_csv('data/task_pm_extended.csv',index_col=0,na_filter=False)
# pl = Program_lib(pm_extended)
# t = [['egg', 'num'], 'num']
# rf = pl.typed_bfs(t,1)
# rf_trimmed = rf[~rf.terms.str.contains("ifElse,bol|num_bol")].reset_index(drop=True)
# rf_trimmed.to_csv('data/task_frames_extended.csv')
# pm_extended_final = pm_extended[~pm_extended.terms.str.contains('numBol|baseBol')].reset_index(drop=True)
# pm_extended_final.to_csv('data/task_pm_extended.csv')

# # %%
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
# data = task_data['learn_a']

# pm_task = pd.read_csv('trials/tmp/curpm.csv', index_col=0, na_filter=False)
# pl = Program_lib(pm_task)

# frame_term = '[CC,[BB,mulnn,PM("egg_num_num")],num]'
# frame_lp = -4.1588830833596715

# pl.unfold_program(frame_term, frame_lp)

# %%
