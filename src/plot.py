print('[INFO]: Importing packages')
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def input_parse():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default='Braunwald.csv', help="dataset to be visualised, default=Braunwald.csv")
    parser.add_argument("--figsize", type=int, nargs='+', default=[9,5], help="choose appropriate figure size, default=(9,5)")
    args = parser.parse_args()

    return(args)

def nlp_plot(data, dataset, measure, figsize, freq=True):

    # prepare data
    x = list(data['age_collapsed'].unique())
    y_c = list(data.loc[data['role']=='child', measure])
    y_cd = list(data.loc[data['role']=='child-directed', measure])

    # plot
    fig, ax = plt.subplots(figsize=figsize)
    plt.plot(x, y_c, color='#5382b8', linestyle='-', label='Child speech')
    plt.plot(x, y_cd, color='#5382b8', linestyle='--', label='Child-directed speech')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tick_params(axis='x', which='major', pad=0)
    plt.legend()
    plt.xlabel("Years;Months")
    if freq:
        plt.title(measure.replace('_freq', '') ) 
        ylabel = "Relative frequency per 10,000 words"
        plt.ylabel(ylabel)
    else: plt.title('Mean Length of Utterance') 

    plt.savefig(os.path.join('..','plots',f"{dataset.replace('.csv','')}_{measure}.png"))


def main(dataset, figsize):
    
    # load dataset
    datapath = os.path.join('..','data',dataset)
    data = pd.read_csv(datapath)

    # convert figsize
    figsize = tuple(figsize)

    # plot lexical categories except for PROPN (and PERSONS)
    print('[INFO]: Plotting')
    measures = list(data.columns[15:-2])
    for i in range(len(measures)):
        nlp_plot(data, dataset, measures[i], figsize)

    # plot mean lenght of utterance
    nlp_plot(data, dataset, 'mean_utt_len', figsize, freq=False)
    
    # plot with both PROPN and PERSON
    x = list(data['age_collapsed'].unique())
    per_c = list(data.loc[data['role']=='child', 'PER_freq'])
    per_cd = list(data.loc[data['role']=='child-directed', 'PER_freq'])
    propn_c = list(data.loc[data['role']=='child', 'PROPN_freq'])
    propn_cd = list(data.loc[data['role']=='child-directed', 'PROPN_freq'])


    fig, ax = plt.subplots(figsize=figsize)
    plt.plot(x, propn_c, color='#5382b8', linestyle='-', label='PROPN child speech')
    plt.plot(x, propn_cd, color='#5382b8', linestyle='--', label='PROPN child-directed speech')
    plt.plot(x, per_c, color='#87baf5', linestyle='-', label='PER child speech')
    plt.plot(x, per_cd, color='#87baf5', linestyle='--', label='PER child-directed speech')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tick_params(axis='x', which='major', pad=0)
    plt.legend()
    plt.title(f"PROPN and PERSON")
    plt.xlabel("Years;Months")
    plt.ylabel("Relative frequency per 10,000 words")

    plt.savefig(os.path.join('..','plots',f"{dataset.replace('.csv','')}_PROPN-PER.png"))

if __name__ == '__main__':
    args = input_parse()
    main(args.dataset, args.figsize)
