print('[INFO]: Importing packages')
# general tools
import os
from tqdm import tqdm
import argparse

# for fetching data
import tbdb

#nlp
import spacy

# data wrangling
import numpy as np
import pandas as pd

def input_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument("--corpora", nargs='+', type=str, default=['childes', 'Eng-NA', 'Braunwald'], 
                        help='Path (space seperated) to the transcripts in the CHILDES database, default = childes Eng-NA Braunwald')
    
    args = parser.parse_args()
        
    return(args)

def main(corpora):
    
    # fecth meta data
    transcripts = tbdb.getTranscripts( {'corpusName': 'childes', 
                                        'corpora': [corpora]} )
    
    transcripts = [transcript[1] for transcript in transcripts['data']]

    # load nlp pipeline from spacy
    nlp = spacy.load("en_core_web_md")

    # final data frame
    df = pd.DataFrame()

    print('[INFO]: Analyzing transcripts')
    # loop over all transcripts
    for transcript in tqdm(transcripts):

        # fetch utterances for current transcript
        utterances = tbdb.getUtterances( {'corpusName': 'childes', 
                                          'corpora': [['childes', 'Eng-NA', 'Braunwald', transcript]],
                                          'lang': ['eng']} )

        # extract info from transcript
        age = [list[0] for list in utterances['data']]
        speaker = [list[3] for list in utterances['data']]
        utterance = [list[7] for list in utterances['data']]
        length = [len(list[7]) for list in utterances['data']]

        # apply nlp pipeline to all utterances of transcript (one doc per utterance)
        docs = nlp.pipe(utterance, batch_size=20)

        # define lexical categories (parts of speech) of interest, assign empty list to each
        lex_cats = ['NOUN', 'VERB', 'ADJ', 'ADV', 'ADP', 'AUX', 'PRON', 'CCONJ', 'SCONJ', 'PROPN']

        NOUN, VERB, ADJ, ADV, ADP, AUX, PRON, CCONJ, SCONJ, PROPN = [], [], [], [], [], [], [], [], [], []
        lex_cat_lists = [NOUN, VERB, ADJ, ADV, ADP, AUX, PRON, CCONJ, SCONJ, PROPN]

        # define entity type of interest
        PER = []

        # loop over utterances (docs)
        for doc in docs:

            # loop over lexical categories
            for lex_cat, lex_cat_list in zip(lex_cats, lex_cat_lists):

                # count number of words in utterance belonging to given lexical category 
                count = np.sum( [1 for token in doc if token.pos_ == lex_cat] )
                lex_cat_list.append(count)
            
            # count number of PERSONS in utterance
            count = np.sum( [1 for ent in doc.ents if ent.label_ == "PERSON"] )
            PER.append(count)
        
        # add data from the transcript to final data frame
        dict_temp = {'age':age, 'speaker':speaker, 'utterance':utterance, 'utterance_len':length,
                     'NOUN':NOUN, 'VERB':VERB, 'ADJ':ADJ, 'ADV':ADV, 'ADP':ADP, 'AUX':AUX, 'PRON':PRON, 'CCONJ':CCONJ,
                     'SCONJ':SCONJ, 'PROPN':PROPN, 'PER':PER}

        df_temp = pd.DataFrame(dict_temp)

        df = pd.concat([df, df_temp])

    # group transcripts according to age of the child in months
    df['age_collapsed'] = [a[1]+a[2:4] for a in df['age']]

    # group non-child speakers
    df['role'] = ['child' if s == 'CHI' else 'child-directed' for s in df['speaker']]

    # summaries counts within groups of interest
    df_sum = df.groupby(['age_collapsed', 'role']).sum(numeric_only = True)

    # calculate relative frequencies per 1000 words
    for category in lex_cats:
        df_sum[f'{category}_freq'] = round((df_sum[category] / df_sum['utterance_len']) * 1000, 2)
    
    # save dataframe
    outpath = os.path.join("..", "data", f"{corpora[-1]}.csv")
    df_sum.to_csv(outpath)

if __name__ == "__main__":
    args = input_parse()
    main(args.corpora)