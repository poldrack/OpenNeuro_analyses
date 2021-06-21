# process tasks

import pandas as pd
from collections import defaultdict

def process_taskname(name, verbose=True):
    # return matching labels for task name
    matchdict = {'stop_signal': ['stopsignal', 'stop signal'],
                 'working_memory': ['workingmemory', 'working memory', 'wm', 'memoryspan'],
                 'simple_rt': ['simplert', 'simple rt', 'simple reaction time'],
                 'movie_watching': ['movie', 'film', 'clips watching'],
                 'oddball': ['oddball'],
                 'reward': ['reward'],
                 'resting': ['rest', 'eyes closed', 'eyes open'],
                 'math': ['math', 'arithm', 'multipl', 'subtract', 'numerosity'],
                 'language': ['verbal', 'language', 'langage'],
                 'semantic': ['semantic', 'meaning'],
                 'reading': ['visual rhym', 'visual spell', 'reading'],
                 'phonological': ['rhyming', 'phonolog'],
                 'auditory': ['auditory', 'audio', 'lpp'],
                 'olfactory': ['olfactory', 'olfaction', 'smell'],
                 'gustatory': ['gustatory', 'taste', 'flavour', 'flavor'],
                 'breath_holding': ['breath-hold', 'breath hold', 'breath_hold'],
                 'visual': ['vision', 'visual', 'visuo'],
                 'scene': ['scene'],
                 'spatial': ['spatial', 'space'],
                 'motor': ['motor', 'fingertap'],
                 'music': ['music', 'chord'],
                 'face': ['face', 'facial', 'iaps'],
                 'reasoning': ['reasoning', 'inductive', 'deductive', 'induction', 'deduction'],
                 'decision_making': ['choice'],
                 'stroop': ['stroop'],
                 'emotion': ['emot', 'mood', 'iaps', 'affect'],
                 'social': ['trust', 'social'],
                 'theory_of_mind': ['tom', 'theory of mind'],
                 'fixation': ['fixation'],
                 'retinotopy': ['retinot', 'prf'],
                 'n-back': ['n-back', '1-back', '2-back', '3-back'],
                 'intertemporal': ['intertemporal', 'delay discount'],
                 'episodic_memory': ['episodic memory', 'free recall'],
                 'memory': ['memory'],
                 'go_nogo': ['gonogo'],
                 'somatosensory': ['whisker'],
                 'imagery': ['imagery'],
                 'game_playing': ['game'],
                 'simon': ['simon'],
                 'reinforcement_learning': ['reinforcementlearning', 'reinforcement learning'],
                 'ravens': ['rapm'],
                 'axcpt': ['ax-cpt', 'axcpt'],
                 'task_switching': ['cuedts']

    }
    matches = []
    for k, targets in matchdict.items():
        for t in targets:
            if t in name:
                matches.append(k)
    matches = list(set(matches))
    return(matches)


if __name__ == "__main__":
    taskdata = pd.read_csv('../data/openneuro/task_info.csv')
    taskdata['taskname'] = [i.lower().strip() for i in taskdata.taskname]

    task_labels = defaultdict(lambda: [])
    for i in taskdata.index:
        dsnum = taskdata.loc[i, 'dsnum']
        taskname = taskdata.loc[i, 'taskname']
        labels = process_taskname(taskname)
        print(dsnum, taskname, labels)
        for l in labels:
            task_labels[dsnum].append(l)