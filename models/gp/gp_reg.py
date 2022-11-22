# %%
import sys
sys.path.append('/usr/local/lib/python3.9/site-packages') # why $PYTHONPATH won't work???

# %%
import GPy
import pandas as pd


# %%
task_data = pd.read_csv('../../data/tasks/tasks.csv', index_col=0)
task_results = pd.DataFrame(columns=['condition','batch','trial','mean','variance'])

for cond in ['construct', 'combine', 'decon', 'flip']:
  for batch in ['A', 'B']:
    # Read data
    if batch=='A':
      trainings = task_data.query(f'condition=="{cond}"&batch=="A"')
    else:
      trainings = task_data.query(f'condition=="{cond}"&batch!="gen"')
    trX = trainings[['stripe','dot','block']].to_numpy()
    trY = trainings[['result_block']].to_numpy()

    # Train
    k = GPy.kern.RBF(input_dim=3, variance=1., lengthscale=1.)
    m = GPy.models.GPRegression(trX,trY,k)
    m.optimize(messages=True)

    # Get predictions
    predictions = task_data.query(f'condition=="{cond}"&batch=="gen"')
    prX = predictions[['stripe','dot','block']].to_numpy()
    prY, prV = m.predict(prX)
    df = pd.DataFrame({'mean':prY.flatten(), 'variance': prV.flatten()})

    # Append metadata
    df['condition']=cond
    df['batch']=batch
    df['trial']=df.index+1

    # Put results together
    task_results = pd.concat([task_results, df[['condition','batch','trial','mean','variance']]], ignore_index=True)


task_results.to_csv('gp_reg_results.csv')

# %%
