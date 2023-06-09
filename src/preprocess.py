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

    parser.add_argument("--corpus", nargs='+', type=str, default=['childes', 'Eng-NA', 'Braunwald'], 
                        help='Path (space seperated) to the transcripts in the CHILDES database, default = childes Eng-NA Braunwald')
    
    args = parser.parse_args()
        
    return(args)

def main(corpus):
    
    # fecth meta data
    print('[INFO]: Fetching names of transcripts from CHILDES')
    transcripts = tbdb.getTranscripts( {'corpusName': 'childes', 
                                        'corpora': [corpus]} )
    
    transcripts = [transcript[1] for transcript in transcripts['data']]

    # load nlp pipeline from spacy
    print('[INFO]: Downloading spaCy pipeline')
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

        # apply nlp pipeline to all utterances of transcript (one doc per utterance)
        docs = nlp.pipe(utterance, batch_size=20)

        # define word classes (parts of speech) of interest, assign empty list to each
        w_classes = ['NOUN', 'VERB', 'ADJ', 'ADV', 'ADP', 'AUX', 'PRON', 'CCONJ', 'SCONJ', 'PROPN']

        NOUN, VERB, ADJ, ADV, ADP, AUX, PRON, CCONJ, SCONJ, PROPN = [], [], [], [], [], [], [], [], [], []
        w_class_lists = [NOUN, VERB, ADJ, ADV, ADP, AUX, PRON, CCONJ, SCONJ, PROPN]

        # define entity type of interest
        PER = []

        # empty list for storing length of utterance
        length = []

        # loop over utterances (docs)
        for doc in docs:

            # count length of utterance
            count = len(doc)
            length.append(count)

            # loop over word classes
            for w_class, w_class_list in zip(w_classes, w_class_lists):

                # count number of words in utterance belonging to given word class
                count = np.sum( [1 for token in doc if token.pos_ == w_class] )
                w_class_list.append(count)
            
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
    df['age_collapsed'] = [a[1]+';'+a[2:4] for a in df['age']]

    # group non-child speakers
    df['role'] = ['child' if s == 'CHI' else 'child-directed' for s in df['speaker']]

    # calculate mean length of utterance
    mean_utt_len = df.groupby(['age_collapsed', 'role'])['utterance_len'].mean()

    # summarise counts within groups
    df_sum = df.groupby(['age_collapsed', 'role']).sum(numeric_only = True)

    # add mean length of utterance
    df_sum['mean_utt_len'] = round(mean_utt_len, 3)

    # calculate relative frequencies per 10,000 words
    w_classes.append('PER')
    for cls in w_classes:
        df_sum[f'{cls}_freq'] = round((df_sum[cls] / df_sum['utterance_len']) * 10000, 3)
    
    # save dataframe
    outpath = os.path.join("..", "data", f"{corpus[-1]}.csv")
    df_sum.to_csv(outpath)

if __name__ == "__main__":
    args = input_parse()
    main(args.corpus)