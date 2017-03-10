import numpy as np
import pandas as pd
import copy
import pickle
import input_output as inout

def combine_hypotheses_per_phrase(ann_mel_dict, oc_dict):
    """ takes a melody dictionary with annotated values for 
    information content, pitch proximity, and pitch reversal,
    and a dictionary listing whether a given phrase occurs in a given melody.
    Returns a dataframe with columns for all hypotheses and occurrence info"""
    for oc in oc_dict:
        melody = next((a['symbols'] for a in ann_mel_dict 
         if a['filename']==oc['query_filename']))
        phrase = [s for s in melody 
         if s['phrase_id']==int(oc['query_segment_id'])]
        oc['IC'] = get_segment_average([p['IC'] for p in phrase])
        oc['pitch_proximity'] = get_segment_average([p['pitch_proximity'] 
         for p in phrase])
        oc['pitch_reversal'] = get_segment_average([p['pitch_reversal'] 
         for p in phrase])
        oc['phrase_length'] = len(phrase)
    oc_df = pd.DataFrame(oc_dict)
    return oc_df

def get_segment_average(values):
    """ return phrase average for 
    Information Content, pitch proximity and pitch reversal """
    okvalues = [v for v in values if v is not np.nan]
    return np.nanmean(okvalues)

################ Rehearsal ###########################
def phrase_repetitions(mel_dict, oc_dict):
    for mel in mel_dict:
        print(mel['filename'])
        phrase_ids = set([s['phrase_id'] for s in mel['symbols']])
        phrase_start_onset = 0.0
        pitch_onset = []
        phrase_list = []
        for i,s in enumerate(mel['symbols']):
            if i>0 and s['phrase_id']>mel['symbols'][i-1]['phrase_id']:
                phrase_start_onset = s['onset']
                phrase_list.append(pitch_onset)
                pitch_onset = []
            pitch_onset.append((s['onset']-phrase_start_onset, s['pitch']))
        phrase_list.append(pitch_onset)
        for i,p in enumerate(phrase_list):
            repetitions = len([phr for phr in phrase_list if phr==p])
            oc_dict_entries = [oc for oc in oc_dict 
             if oc['query_filename']==mel['filename'] 
             and oc['query_segment_id']==i]
            for oc in oc_dict_entries:
                oc['phrase_repetitions'] = repetitions
    return oc_dict

################## Motif repetivity #####################
def return_entropy_FANTASTIC(csvpath, oc_dict):
    """ takes a file for which ngram entropy has been generated
    with the FANTASTIC toolbox, and a dictionary of occurrences
    returns the occurrence dict with entropy values added """
    phrase_dict = inout.csv_to_dict(csvpath)
    for phr in phrase_dict:
        oc_dict_entries = [oc for oc in oc_dict if 
         oc['query_filename']==phr['file.id'] and 
         oc['query_segment_id']==int(phr['phr.id'])-1]
        for oc in oc_dict_entries:
            oc['mean.entropy'] = phr['mean.entropy']
    return oc_dict

################## Expectancy #############################
################## IDyOM
def return_expectancy_IDyOM(idyomfile,mel_dict) :
    """ takes an idyom csv file and a melody dictionary
    for each note in the melodies, pulls probability,
    information content and probability and adds it to the dictionary
    """
    idyomdf = pd.read_csv(idyomfile,sep=" ")
    filenames = set([idyomdf.ix[i, 'melody.name'] for i in range(len(idyomdf))])
    sub_dict = [m for m in mel_dict if m['filename'] in filenames]
    for mel in sub_dict :
        idyom_notes = [idyomdf.ix[i] for i in range(len(idyomdf)) if 
         idyomdf.ix[i,'melody.name']==mel['filename']]
        if not idyom_notes :
            print(mel['filename'])
            continue
        for i,s in enumerate(mel['symbols']) :
            s['IC'] = idyom_notes[i]['information.content']
    return mel_dict
    
################## Schellenberg
def return_expectancy_Schellenberg(mel_dict):
    """ takes a dictionary of melodies with pitch interval representations,
    the factors for pitch proximity and pitch reversal and 
    returns how well expectations are fulfilled according to the two-factor 
    model by Schellenberg (1997).
    """
    for m in mel_dict :
        pitchIntervals = [s['pitch_interval'] for s in m['symbols']]
        for i,p in enumerate(pitchIntervals) :
            regDirection = np.nan
            regReturn = np.nan
            if i==0:
                pitchProximity = np.nan
                pitchReversal = np.nan
            # only from the second pitch interval (i.e. third note)
            # I-R theory can make predictions
            elif i>=2:
                # pitch proximity and pitch reversal 
                # are only defined below octave
                if abs(pitchIntervals[i-1]) <= 11 and abs(p) <= 12:
                    pitchProximity = abs(p)
                    if abs(pitchIntervals[i-1]) != 6:
                        # pitch reversal is not defined if 
                        # implicative interval is a tritone
                        if abs(pitchIntervals[i-1]) < 6:
                        # small pitch interval - direction could go either way
                            regDirection = 0
                        elif abs(pitchIntervals[i-1]) > 6:
                            if pitchIntervals[i-1] + p > 0:
                                # large interval but same direction
                                # this is less expected
                                regDirection = -1
                            else:
                                regDirection = 1
                        if ((pitchIntervals[i-1] * p) < 0 and 
                            abs(abs(pitchIntervals[i-1]) - abs(p)) <= 2):
                            # intervals have different direction 
                            # and are similar in size
                            regReturn = 1.5
                        else:
                            regReturn = 0
                        pitchReversal = regDirection + regReturn
                    else:
                        pitchReversal = np.nan
                else:
                    pitchReversal = np.nan
                    pitchProximity = np.nan
            m['symbols'][i]['pitch_proximity'] = pitchProximity
            m['symbols'][i]['pitch_reversal'] = pitchReversal
    return mel_dict.copy()