import csv
import input_output as inout

def convert_melodies(mel_dict, outdir, ticks = 3072):
    """ this function takes a melody dictionary, as rendered by
    music_representations in MelodicOccurrences.
    This file is converted to a mcsv file which can be analyzed by FANTASTIC.
    Populated fields are: onset, onsetics, pitch, durs, durtics, dur16, and
    temperley. The other fields are 0, as they are not used by the toolbox.
    Field "temperley" is used for segmentation of the melody,
    and this function adds the information of the annotated segmentation from
    the Meertens Tune Collections.
    """
    mcsv_keys = ("onset","onsetics","takt","beat","ticks","pitch",
     "durs","durtics","dur16","LBDM1","LBDM2",
     "refLBDM1","refLBDM2","temperley","dummy")
    for mel in mel_dict:
        filename = outdir+mel['filename']+".csv"
        outdict = []
        for i,s in enumerate(mel['symbols']):
            if i==len(mel['symbols'])-1:
                segmentation = 1
            elif mel['symbols'][i+1]['phrase_id']>s['phrase_id']:
                segmentation = 1
            else:
                segmentation = 0
            outdict.append({"onset": float(s['onset']),
             "onsetics": int(s['onset'] * 3072),
             "takt": 0, "beat": 0, "ticks": 0, 
             "pitch": s['pitch'], "durs": float(s['ioi']), 
             "durtics": int(s['ioi']*ticks), "dur16": int(s['ioi']*16), 
             "LBDM1": 0, "LBDM2": 0, "refLBDM1": 0, "refLBDM2": 0, 
             "temperley": segmentation, "dummy": 0})
        inout.dict_to_csv(outdict, mcsv_keys, filename, ";")
        with open(filename, "w+") as f:
            f.write("FANTASTIC expects a first line\n")
            wr = csv.writer(f, delimiter=";")
            wr.writerow(mcsv_keys)
            for item in outdict :
                elements = [item[k] for k in mcsv_keys]
                wr.writerow(elements)
        print(mel["filename"])
    return None



