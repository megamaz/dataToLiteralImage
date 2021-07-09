import json

level = json.load(open("in.json"))
info = json.load(open("Info.dat"))

# create custom events
level["_customData"] = {
    "_customEvents":[],
    "_pointDefinitions":[]
}

paulCount = 0

def getNotesBetweenBeats(start, end):
    return [x for x in level["_notes"] if x["_time"] >= start and x["_time"] <= end]

def createPaulNote(startBeat:float, endbeat:float, noteIndex:int, noteLayer:int, cutDir:int, noteType:int, njs):
    """You have to manually put in the NJS because im too lazy and fuck you"""
    global paulCount
    for n in getNotesBetweenBeats(startBeat, endbeat):
        if n["_lineIndex"] == noteIndex and n["_lineLayer"] == noteLayer and n["_cutDirection"] == cutDir and n["_type"] == noteType:
            level["_notes"][level["_notes"].index(n)]["_customData"] = {
                "_animation":
                {
                    "_dissolve":[[0, 0]],
                    "_dissolveArrow":[[0, 0]]
                }
            }
    
    level["_notes"].append(
        {
            "_time":(startBeat + endbeat) / 2,
            "_lineIndex":noteIndex,
            "_lineLayer":noteLayer,
            "_type":noteType,
            "_cutDirection":cutDir,
            "_customData":
                {
                    "_track":f"paul{paulCount}",
                    "_fake":True,
                    "_interactable":False,
                    "_disableNoteLook":True,
                    "_disableNoteGravity":True
                }
        }
    )

    level["_customData"]["_customEvents"] += [
        {
            "_time":0,
            "_type":"AnimateTrack",
            "_data":
                {
                    "_duration":startBeat-0.01,
                    "_track":f"paul{paulCount}",
                    "_scale":[
                        [1, 1, ((60/info["_beatsPerMinute"]) * 2 * njs), 0]
                    ]
                }
        },
        {
            "_time":startBeat,
            "_type":"AnimateTrack",
            "_data":
                {
                    "_track":f"paul{paulCount}",
                    "_duration":endbeat - startBeat,
                    "_position":[
                        [0, 0, (((60/info["_beatsPerMinute"]) * 2 * njs)/2) + 1 , 0],
                        [0, 0, 1, 1]
                    ],
                    "_time":[
                        [0.5, 0]
                    ],
                    "_scale":[
                        [1, 1, ((60/info["_beatsPerMinute"]) * 2 * njs), 0],
                        [1, 1, 0, 1]
                    ]
                }
        }
    ]
    

    paulCount += 1



createPaulNote(2, 4, 3, 1, 1, 1, 12)

json.dump(level, open("ExpertPlusStandard.dat", 'w'))