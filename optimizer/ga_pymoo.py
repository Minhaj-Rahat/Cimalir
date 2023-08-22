from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import ElementwiseProblem, Problem
from pymoo.operators.crossover.ux import UniformCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.util.display.output import Output
from pymoo.util.display.column import Column

import multiprocessing
from pymoo.core.problem import StarmapParallelization

import numpy as np
import random

# ours
import weight_test_genetic_helper as wh
import os


gaf = []
ts = []
mir = []
dofl = []
haji = []

get_files = lambda path: (os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files)
fold = 'tune_cube_db_now/'  # path to tuning dataset

# generate random integer from a range except a specific number
def rand_execept(s):
    num = random.randint(0,4)
    while num == s:
        num =random.randint(0,4)
    return num

# generate two random number from a range
def rand_two(rang):
    n1 = random.randint(0,rang)
    n2 = random.randint(0,rang)
    return n1,n2

#files = []
for name in get_files(fold):
    if name.split('/')[-2] == 'gafgyt':
        gaf.append(name)
    elif name.split('/')[-2] == 'tsunami':
        ts.append(name)
    elif name.split('/')[-2] == 'mirai':
        mir.append(name)
    elif name.split('/')[-2] == 'dofloo':
        dofl.append(name)
    elif name.split('/')[-2] == 'hajime':
        haji.append(name)
    #files.append(name)

family_list = [gaf, ts, mir, dofl, haji]
# variables for NSGAII
variable_num = 7
objective_num = 1
constraint_num=0
#offspring_num = 20
population_size= 50
gen_num = 50
samples_per_family=30

# bounds
j_min = 0
j_max = 1
w_min = 0
w_max = 100

# min max values
x_min = [0,1,1,1,1,1,0]
x_max = [1,100,100,100,100,100,1]




def optimize():
    # define result printout function
    class MyOutput(Output):
        def __init__(self):
            super().__init__()
            self.jaccard = Column("jaccard", width=7)
            self.euclidean = Column("euclidean", width=7)
            self.caller = Column("caller", width=7)
            self.callee = Column("callee", width=7)
            self.param = Column("param", width=7)
            self.ctrans = Column("ctrans", width=7)
            self.cthresh = Column("cthresh", width=7)
            self.columns += [self.jaccard, self.euclidean, self.caller, self.callee, self.param, self.ctrans,
                             self.cthresh]

        def update(self, algorithm):
            super().update(algorithm)
            self.jaccard.set(algorithm.pop.get("X")[0][0])
            self.euclidean.set(algorithm.pop.get("X")[0][1])
            self.caller.set(algorithm.pop.get("X")[0][2])
            self.callee.set(algorithm.pop.get("X")[0][3])
            self.param.set(algorithm.pop.get("X")[0][4])
            self.ctrans.set(algorithm.pop.get("X")[0][5])
            self.cthresh.set(algorithm.pop.get("X")[0][6])

    # define fitness function

    class Fitness_class(ElementwiseProblem):
        def __init__(self, **kwargs):
            super().__init__(n_var=variable_num, n_obj=objective_num, n_constr=constraint_num, xl=x_min, xu=x_max,
                             **kwargs)

        def _evaluate(self, x, out, *args, **kwargs):
            jaccard_threshold = x[0]
            similarity_threshold = x[1]
            similarity_weight = []
            similarity_weight.append(x[2])
            similarity_weight.append(x[3])
            similarity_weight.append(x[4])
            similarity_weight.append(x[5])

            call_graph_threshold = x[6]

            score_sum_diff = 0

            for k in range(samples_per_family):
                # randomly select first family
                ind = random.randint(0, 4)
                f1 = family_list[ind]
                # randomly select two samples from the same family
                n1, n2 = rand_two(len(f1) - 1)
                # randomly select different family
                f2 = family_list[rand_execept(ind)]
                n3 = random.randint(0, len(f2) - 1)

                s1 = wh.sim_func(jaccard_threshold, similarity_threshold, similarity_weight, call_graph_threshold,
                                 f1[n1],
                                 f1[n2])
                s2 = wh.sim_func(jaccard_threshold, similarity_threshold, similarity_weight, call_graph_threshold,
                                 f1[n1],
                                 f2[n3])

                score_sum_diff += s1 - s2

            f1 = -score_sum_diff  # minimize this will maximize the similarity

            out["F"] = f1

    # initialize threadpool and create the runner
    n_process = 10
    pool = multiprocessing.Pool(n_process)
    runner = StarmapParallelization(pool.starmap)

    problem = Fitness_class(elementwise_runner=runner)
    # problem = Fitness_class()

    # algortihm = GA(pop_size=population_size,n_offsprings=offspring_num,crossover=UniformCrossover(),eliminate_duplicates=True)
    algortihm = GA(pop_size=population_size, eliminate_duplicates=True)

    termination = get_termination("n_gen", gen_num)

    result = minimize(problem, algortihm, termination, seed=7, save_history=True, output=MyOutput(), verbose=True)

    X = result.X
    F = result.F

    print("Best:")
    print(X)
    print("Objective")
    print(F)



