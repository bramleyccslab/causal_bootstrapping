# %%
from pandas.core.common import flatten

# %%
def if_else(arg_list):
  cond, ret_1, ret_2 = arg_list
  return ret_1 if cond else ret_2

# Router functions
def send_right(arg_dict, arg_list):
  arg_dict['right'] = list(flatten(arg_dict['right'] + [arg_list]))
  return arg_dict

def send_left(arg_dict, arg_list):
  arg_dict['left'] = list(flatten(arg_dict['left'] + [arg_list]))
  return arg_dict

def send_both(arg_dict, arg_list):
  arg_dict['left'] = list(flatten(arg_dict['left'] + [arg_list]))
  arg_dict['right'] = list(flatten(arg_dict['right'] + [arg_list]))
  return arg_dict

def constant(arg_dict, _):
  return arg_dict

def return_myself(arg_list):
  if isinstance(arg_list, list):
    return arg_list[0]
  else:
    return arg_list
