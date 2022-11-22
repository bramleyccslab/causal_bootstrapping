# Supplementary Code and Data

Implementations for manuscript *How cognition bootstraps its way to complex concepts*, by [Bonan Zhao](https://zhaobn.github.io), [Christopher G. Lucas](https://homepages.inf.ed.ac.uk/clucas2/), and [Neil R Bramley](https://www.bramleylab.ppls.ed.ac.uk/member/neil/).

## Repo structure

```
causal_bootstrapping/
├── LICENSE
├── README.md
├── experiment
│   ├── css
│   │   └── style.css
│   ├── js
│   │   ├── config.js
│   │   ├── config_2.js
│   │   ├── config_3.js
│   │   ├── config_4.js
│   │   ├── config_5.js
│   │   ├── funcs.js
│   │   └── task.js
│   └── p
│       ├── task.html
│       └── welcome.html
├── models
│   ├── ag
│   │   ├── base_classes.py
│   │   ├── base_methods.py
│   │   ├── data
│   │   │   ├── task_frames.csv
│   │   │   ├── task_pm.csv
│   │   │   └── tasks
│   │   │       ├── exp_1.csv
│   │   │       ├── exp_2.csv
│   │   │       ├── exp_3.csv
│   │   │       └── exp_4.csv
│   │   ├── helpers.py
│   │   ├── program_inf.py
│   │   ├── program_lib.py
│   │   ├── program_sim.py
│   │   ├── sims
│   │   │   ├── construct.py
│   │   │   ├── construct_a_post_samples.csv
│   │   │   ├── decon.py
│   │   │   ├── runGenerator.js
│   │   │   └── simGenerator.js
│   │   └── task_terms.py
│   ├── gp
│   │   ├── gp_reg.py
│   │   └── gp_reg_results.csv
│   ├── pcfg
│   │   ├── Rational_rules.py
│   │   ├── prediction.py
│   │   └── training.py
│   └── requirements.txt
├── openai
│   ├── gpt3-predictions.csv
│   ├── gpt3-reports.csv
│   └── playground.ipynb
└── trials
    ├── data
    │   ├── PM_LL.csv
    │   ├── all_eqc.csv
    │   ├── eig_trials.csv
    │   ├── final_trials.csv
    │   ├── final_trials_2.csv
    │   ├── final_trials_flip.csv
    │   └── flip_all_eqc.csv
    ├── get_pms.py
    ├── get_trials.py
    └── prep_pms.py
```

The `experiment/` folder contains code for the online experiment. A live demonstration is at <https://bramleylab.ppls.ed.ac.uk/experiments/bootstrapping/p/welcome.html>

The `models/` folder contains python code (python 3.9) for the adaptor grammar model (`models/ag/`), the rational rules model (`models/pcfg/`), and the gaussian process regression model (`models/gp/`). 

For the adaptor grammar model, folder `sims` contains example scripts (`construct.py`, `decon.py`) to run the model. The `runGenerator.js` and `simGenerator.js` scripts can generative python scripts for each experimental condition in batch.

In `models/ag`, there are object-oriented implementaion treating programs, terms and routers all as classes (`base_classes.py`, `task_terms.py`, `program_lib.py`). Correpondingly, their "causal influence" are implemented as functions and methods in the classes (`base_methods.py`, `program_inf.py`, `program_sim.py` and `helpers.py`).  The `data/` folder contains necessary prep data, eg. task setups.

The `trials/` folder has python code for selecting generalization trials for Experiment 1 (see SI section in the linked manuscript).

Folder `openai/` contains an ipython notebook that I used to batch-retrieve self-reports and generalization predictions from GPT-3, and the corresponding results (`gpt3-reports.csv` and `gpt3-predictions.csv`).

## Useful links

* Experiment data, pre-regs and data analysis scripts are available in OSF repo <https://osf.io/9awhj/>
* A live experiment demo: <https://bramleylab.ppls.ed.ac.uk/experiments/bootstrapping/p/welcome.html>
* Knitted analysis for manuscript: <https://bramleylab.ppls.ed.ac.uk/experiments/bootstrapping/analysis.html>
* Working github repo with all dev history and some un-reported attempts: https://github.com/zhaobn/comlog
* Cogsci paper [Powering up causal generalization: A model of human conceptual bootstrapping with adaptor grammars](https://escholarship.org/uc/item/8sh6k4rd)








