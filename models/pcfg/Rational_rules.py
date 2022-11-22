# %%
from random import sample
from math import log

# %%
class Rational_rules:
  def __init__(self, p_rules, cap=10):
    self.NON_TERMINALS = [x[0] for x in p_rules]
    self.PRODUCTIONS = {}
    self.CAP = cap
    for rule in p_rules:
      self.PRODUCTIONS[rule[0]] = rule[1]

  def generate_tree(self, logging=True, tree_str='S', log_prob=0., depth=0):
    current_nt_indices = [tree_str.find(nt) for nt in self.NON_TERMINALS]
    # Sample a non-terminal for generation
    to_gen_idx = sample([idx for idx, el in enumerate(current_nt_indices) if el > -1], 1)[0]
    to_gen_nt = self.NON_TERMINALS[to_gen_idx]
    # Do generation
    leaf = sample(self.PRODUCTIONS[to_gen_nt], 1)[0]
    to_gen_tree_idx = tree_str.find(to_gen_nt)
    tree_str = tree_str[:to_gen_tree_idx] + leaf + tree_str[(to_gen_tree_idx+1):]
    # Update production log prob
    log_prob += log(1/len(self.PRODUCTIONS[to_gen_nt]))
    # Increase depth count
    depth += 1

    # Recursively rewrite string
    if any (nt in tree_str for nt in self.NON_TERMINALS) and depth <= self.CAP:
      return self.generate_tree(logging, tree_str, log_prob, depth)
    elif any (nt in tree_str for nt in self.NON_TERMINALS):
      if logging:
        print('====DEPTH EXCEEDED!====')
      return None
    else:
      if logging:
        print(tree_str, log_prob)
      return tree_str, log_prob

  @staticmethod
  def evaluate(rule, data):
    d = data
    pred = eval(rule[0])
    likelihood = (int(pred)==int(d[2]))
    return likelihood, rule[1]

  @staticmethod
  def predict(rule, data):
    d = data
    pred = eval(rule[0])
    pred = 0 if pred < 0 else pred
    pred = 16 if pred > 16 else pred
    return str(pred), rule[1]


# %%
# #### For evaluation
def add(x, y): return int(x)+int(y)
def sub(x, y): return int(x)-int(y)
def mult(x, y): return int(x)*int(y)
# Example data ('Egg(S1,O0)', '3', '3')
def stripe(d): return d[0][4:-1].split(',')[0][1:]
def spot(d): return d[0][4:-1].split(',')[1][1:]
def stick(d): return d[1]


# # %% Debug
# productions = [
#   ['S', ['add(A,A)', 'sub(A,A)', 'mult(A,A)']],
#   ['A', ['S', 'B']],
#   ['B', ['C', 'D']],
#   ['C', ['stripe(d)', 'spot(d)', 'stick(d)']],
#   ['D', ['0', '1', '2', '3']]
# ]
# test = Rational_rules(productions, cap=100)
# test.generate_tree()


# # x = test.generate_tree()
# # x = test.generate_tree(logging=False)

# demo_rule = ('mult(stick(d),add(spot(d),add(stripe(d),spot(d))))',-14.62)
# demo_data = ('Egg(S1,O4)', '3', '0')

# y = test.evaluate(demo_rule, demo_data)
# test.predict(demo_rule, demo_data)

# # %% Get test data
# # Prep data
# all_data = pd.read_json('../for_exp/config.json')
# task_ids = {
#   'learn_a': [23, 42, 61],
#   'learn_b': [35, 50, 65],
#   'learn_c': [27, 31, 35],
#   'gen': [82, 8, 20, 4, 98, 48, 71, 40],
# }
# task_ids['gen'].sort()

# task_data = {}
# for item in task_ids:
#   task_data[item] = []
#   for ti in task_ids[item]:
#     data = all_data[all_data.trial_id==ti]
#     _, agent, recipient, result = list(data.iloc[0])
#     converted = (f'Egg(S{agent[1]},O{agent[4]})', recipient[-2], result[-2])
#     task_data[item].append(converted)

# task_configs = {
#   'construct': {
#     'phase_1': task_data['learn_a'],
#     'phase_2': task_data['learn_a'] + task_data['learn_b']
#   },
#   'combine': {
#     'phase_1': task_data['learn_a'],
#     'phase_2': task_data['learn_a'] + task_data['learn_c']
#   },
#   'decon': {
#     'phase_1': task_data['learn_b'],
#     'phase_2': task_data['learn_b'] + task_data['learn_a']
#   }
# }

# %%
