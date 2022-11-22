
####################### General imports ###############################
from copy import copy
from math import exp, fabs

# Get human-readable translation of a list of objects
# Expensive operation (recursion), be careful
def print_name(mylist):
  retlist = []
  for x in mylist:
    if isinstance(x, list):
      named_list = print_name(x)
      retlist.append(named_list)
    elif isinstance(x, bool) or isinstance(x, int):
      retlist.append(str(x))
    else:
      retlist.append(x.name)
  return retlist

# Return a list
def secure_list(input):
  output = input if isinstance(input, list) else [ input ]
  return output

# Return copy of a list (of objects)
def copy_list(lt):
  ret = []
  for _l in lt: ret.append(copy(_l))
  return ret

# Join a list of arg types into underscore-separated string
def args_to_string(arg_list):
  return '_'.join(secure_list(arg_list))

# Stringify a list of term names for dataframe evaluation
def names_to_string(names_list):
  return str(names_list).replace("'", '')

# Normalize a list
def normalize(mylist):
  total = sum(mylist)
  return [ l/total for l in mylist ]

# Apply softmax on a list
def softmax(mylist, base):
  exp_list = [ exp(l*base) for l in mylist ]
  total = sum(exp_list)
  return [ el/total for el in exp_list ]

# Term a term object into dict
def term_to_dict(term):
  if isinstance(term, bool):
    terms = 'True' if term == True else 'False'
    arg_types = ''
    return_type = 'bool'
    type = 'base_term'
  elif isinstance(term, int):
    terms = str(term)
    arg_types = ''
    return_type = 'num'
    type = 'base_term'
  elif term.ctype == 'primitive':
    terms = term.name
    arg_types = args_to_string(term.arg_type)
    return_type = term.return_type
    type = term.ctype
  else: # base term
    terms = term.name
    arg_types = ''
    return_type = term.ctype
    type = 'base_term'
  return dict(terms=terms, arg_types=arg_types, return_type=return_type,type=type)

# Approximate motor noise
# Input choice_list should be a one-hot coded list
def add_motor_noise(choice_list, softmax_base=0):
  center_index = choice_list.index(1)
  weights = [ exp(-1*fabs(x-center_index)) for x in range(len(choice_list))]
  if softmax_base==0:
    return normalize(weights)
  else:
    return softmax(weights, softmax_base)
