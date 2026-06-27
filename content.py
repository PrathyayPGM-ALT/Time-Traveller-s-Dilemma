"""All narrative + world *content* (not layout).

Era layouts are generated procedurally in worldgen.py; here we author only
the meaning: themes, the puzzle (a cryptic directive + clues + a code lock),
the people, and the props that may be scattered. Several helpers weave the
persistent soul (past lives) into the boss, the Troi, and the trap.
"""

import random

import config

SPEAKERS = {
    "boss":       ("THE BOSS", "textures/boss.png", config.BLOOD),
    "titor":      ("TIMETRAVEL_0", "textures/npc1.png", config.TITOR),
    "john":       ("THE BOY", "textures/npc1.png", config.RIFT),
    "keeper":     ("TIME KEEPER", "textures/npc2.png", config.WARN),
    "warden":     ("BROKEN KEEPER", "textures/npc2.png", config.WARN),
    "clerk":      ("CLERK", "textures/npc1.png", config.ASH),
    "patron":     ("PATRON", "textures/npc3.png", config.ASH),
    "astronomer": ("ASTRONOMER", "textures/npc3.png", config.WARN),
    "figure":     ("THE FIGURE", "textures/npc3.png", config.RIFT),
    "stranger":   ("?", "textures/npc3.png", config.ASH),
    "self":       ("YOU", None, config.WHITE),
}


def say(who, text):
    return {"who": who, "text": text}


def _ordinal(n):
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


BOSS_INTRO = [
    say("boss", "There you are. I almost missed you — you wear that body so loosely."),
    say("boss", "Prisoner 7. No, you don't remember the name they gave you. Good — remembering is for people with futures."),
    say("boss", "The year is 4200. The sky is the colour of rust and old smoke. We all did that."),
    say("boss", "You will travel. Every jump passes through the Troi, where the lost ones float."),
    say("boss", "DO NOT SPEAK TO WHAT FLOATS THERE."),
    say("boss", "I won't hold your hand in the past. Read the place, work out what it wants, and leave."),
    say("boss", "Avoid the Time Keepers. Whatever you think you remember — you are wrong. Now go."),
]


def boss_intro(flags):
    """The opening briefing — darker and more knowing the more lives you've lived."""
    lives = flags["lives"]
    lines = list(BOSS_INTRO)
    if lives and lives > 1:
        pre = [
            say("boss", f"Welcome back. This is your {_ordinal(lives)} waking, though you'll call it the first."),
            say("boss", "A new body. A new soul, they keep telling me. The same hands, I keep noticing."),
        ]
        ever = flags["ever_eras"]
        if ever:
            pre.append(say("boss",
                           f"Some of this you've done before — in {ever[-1]}, in another life. "
                           "Your fingers will remember even when you do not."))
        lines = pre + lines
    return lines


HUB_SUBTITLES = [
    "The earth is a spoil. The machine hums anyway.",
    "Post-war, post-everything. Mostly just post.",
    "The sky forgot how to be blue. You forgot the rest.",
    "Nobody left up here to disappoint but the boss.",
    "Cold concrete, colder company.",
]

RETURN_FIRST = [
    "Orientation survived. I'm nearly impressed. Nearly.",
    "There — you can move, press, and type. The bar was on the floor; you cleared it.",
    "No, you haven't travelled yet. Yes, it gets worse. Choose a year.",
    "The machine is warm. You are not ready. These rarely align in your favour.",
]

RETURN_BACK = [
    "Back. The Troi spat you out again — it never did have taste.",
    "Still wearing that body. The Troi's standards are famously low.",
    "You returned. Statistically, one of these times you won't.",
    "The floaters let you through. Don't thank them. They only want the company.",
    "Home, more or less. You came back as someone slightly less than you left. Normal.",
    "You made it past the others. They waved. You waved. Nobody meant it.",
    "Out and back, and the year behind you is already forgetting your face. Lucky year.",
]

RETURN_PICK = [
    "Pick a year.",
    "Choose a destination. Try to return from this one too.",
    "Select. They're all waiting — which is to say, none of them are.",
    "Where to, then? They rot at different speeds, if that helps.",
]


def boss_return(flags):
    if not flags["visits"]:
        return [say("boss", random.choice(RETURN_FIRST))]
    return [say("boss", random.choice(RETURN_BACK)),
            say("boss", random.choice(RETURN_PICK))]


BOSS_ALL_DONE = [
    say("boss", "You've done all of it. Every thread. Every warning, planted exactly where I needed it."),
    say("boss", "The man on the forums. The old computer. The burned page. The dead spire. The fire in the cave."),
    say("boss", "People read the warnings. People panicked. People built the very bombs that made 4200."),
    say("boss", "You were never sent to stop the war, Prisoner 7. You were sent to start it. On schedule. As always."),
    say("boss", "And now you know. Which means it's time to forget again. Step into the machine."),
]

TROI_WHISPERS = [
    "you've stood here before",
    "i know your walk",
    "we were the same once",
    "don't go to that year. you always go to that year.",
    "the boss is not a person",
    "count the ones who float. it's always one more.",
    "did the bombs fall, or did we drop them on purpose?",
    "you left something in 2001. it's still waiting.",
    "i remember a face that isn't mine",
    "this is the third time we've met. you said that last time too.",
]

TROI_FIRST = [
    "This is the Troi.",
    "It is not a place. It is the seam between places.",
    "The figures around you are travellers, like you. Some never left.",
    "Walk to the rift. Try not to recognise anyone.",
]

TROI_LATER = [
    "The Troi again. It does not get easier.",
    "One more figure floats here than last time. You decide not to count.",
]


def troi_whispers(flags):
    pool = list(TROI_WHISPERS)
    for e in flags["echoes"][-6:]:
        tail = e.split(":", 1)[-1].strip().rstrip(".").lower()
        pool.append(f"(a life you forgot) {tail}")
    return pool


def troi_floaters(flags):
    base = 4 + flags["visits"] + max(0, flags["lives"] - 1)
    base += len(flags["echoes"]) // 3
    return min(base, 18)


TRAPPED_INTRO = [
    "The Keepers took you.",
    "There is no rift here. Not for you. Not anymore.",
    "Only the others. Walk among them. They have been waiting to talk.",
    "(There is no way out but to stop. Press Q or Esc when you can bear no more.)",
]

NARR_KEEPER_WATCH = "Something in this year has started to watch you."
NARR_KEEPER_SPAWN = "Time Keepers. Get to a rift. Do not let them touch you."
NARR_LEAVE = "Leaving with the work undone. The boss will smile. He always smiles."
NARR_WORK_DONE = [
    "The work is done. The year exhales.",
    "Find a rift when you are ready to leave.",
]
NARR_DIVERT = [
    "That wasn't what you came for. You know that.",
    "Curiosity is how travellers end up floating in the Troi.",
    "The boss didn't send you here to wander.",
]

_TRAPPED_AUTHORED = [
    [say("stranger", "You're new. We're all new. That's the joke."),
     say("stranger", "The Keepers don't end you. They just stop letting you leave.")],
    [say("stranger", "I counted us once. The number only ever goes up. Never down."),
     say("stranger", "Do you still think the boss is someone else? That's sweet.")],
    [say("stranger", "There's no rift here. Not for us. We are the rift now."),
     say("stranger", "Listen — when you start again, and you will, leave us a kinder note.")],
    [say("stranger", "I had a name. I traded it for one more jump. Bad deal. Don't.")],
]


def trapped_voices(flags):
    """Beings to converse with while trapped — past lives among them."""
    voices = [list(v) for v in _TRAPPED_AUTHORED]
    for e in flags["echoes"][-6:]:
        tail = e.split(":", 1)[-1].strip()
        voices.append([
            say("stranger", tail),
            say("stranger", "...that was me. Or you. The grammar gave up centuries ago."),
        ])
    return voices


ERAS = {
    "2001": {
        "year": "2001", "theme": "cafe",
        "title": "The Glow of a Dying Web",
        "place": "An internet café. Cigarette smoke. A CRT humming.",
        "zone_names": ["The Street", "The Café Floor", "The Terminal Corner",
                       "The Back Room", "The Smoking Nook", "The Server Closet",
                       "The Toilets", "The Office", "The Stockroom"],
        "decor_kinds": ["table", "chair", "crt", "server", "shelf", "plant"],
        "brief": [
            say("boss", "2001. A man is about to become a legend on a message board."),
            say("boss", "Find what he claims about himself, and make the board believe it."),
            say("boss", "Read the room. The Keepers here delete what they fear."),
        ],
        "arrival": [
            "2001. The web is still mostly text and patience.",
            "Nobody will tell you what to do. Read. Deduce. Then convince the terminal.",
            "Find the right year, and type it where it counts.",
        ],
        "puzzle": {
            "directive": "Prove you're the soldier — give the TERMINAL your origin year.",
            "lock": "terminal",
            "answer": ["2036"],
            "prompt": "TIMETRAVEL_0  //  STATE YOUR ORIGIN YEAR",
            "solved": [
                say("self", "You type the year. The board believes a stranger from 2036."),
                say("titor", "There is a war coming. You will not believe me. That is how it happens."),
                say("self", "Decades from now this becomes a legend. Then a blueprint. Then a reason."),
            ],
        },
        "objects": [
            {"id": "notice", "label": "NOTICE BOARD", "kind": "lore", "prop": "poster",
             "take": "the warning paper", "lines": [
                say("self", "A printout pinned among the flyers, in a hand you don't remember being yours:"),
                say("titor", "'I am a soldier from the year 2036. I came back for a machine. Do not look for me.'"),
            ]},
            {"id": "deleted", "label": "DELETED THREADS", "kind": "lore", "prop": "computer",
             "risky": True, "take": "a censored printout", "lines": [
                say("self", "You weren't meant to read these."),
                say("stranger", "thread: 'the soldier lies — the war is OURS to start' — locked by [KEEPER]"),
                say("self", "A moderator deleted it a second before you looked. You feel watched."),
            ]},
            {"id": "payphone", "label": "PAYPHONE", "kind": "lore", "prop": "payphone",
             "risky": True, "lines": [
                say("self", "It rings the instant you look at it."),
                say("boss", "Step away from the phone, Prisoner 7. You can't hear me here yet."),
            ]},
            {"id": "terminal", "label": "TERMINAL", "kind": "lore", "prop": "crt", "lines": []},
        ],
        "npcs": [
            {"id": "clerk", "label": "CLERK", "sprite": 1, "radius": 40, "lines": [
                say("clerk", "Terminal's three bucks an hour. You look like you've not slept since a war that hasn't happened."),
                say("clerk", "That guy in the corner won't stop saying he's from 2036. Loon."),
            ]},
            {"id": "patron", "label": "PATRON", "sprite": 3, "radius": 120, "lines": [
                say("patron", "We've all done tonight before, haven't we?"),
                say("patron", "The mod here — KEEPER — deletes anything about the dreams. Careful what you post."),
            ]},
        ],
    },

    "1998": {
        "year": "1998", "theme": "garage",
        "title": "A Photograph of a Boy",
        "place": "A suburban home. A family that doesn't know what it holds.",
        "zone_names": ["The Driveway", "The Garage", "The Workbench", "The House",
                       "The Hallway", "The Attic", "The Yard", "The Den", "The Cellar"],
        "decor_kinds": ["crate", "barrel", "shelf", "cot", "plant", "tree"],
        "brief": [
            say("boss", "1998. The soldier visits family before the world. A machine here must outlive everyone."),
            say("boss", "Work out which machine, exactly. Name it to lock it down. Don't get attached to the child."),
        ],
        "arrival": [
            "1998. A home with the TV murmuring somewhere.",
            "A machine here has to survive to 2036. Work out which one — precisely.",
            "Name it to the lock.",
        ],
        "puzzle": {
            "directive": "Lock the right machine — name its model number.",
            "lock": "computer",
            "answer": ["5100", "ibm 5100", "ibm5100"],
            "prompt": "SECURE UNIT  //  MODEL NUMBER",
            "solved": [
                say("self", "You lock the beige machine down where it'll be found in 2036."),
                say("self", "Scratched on the casing by a child's hand: a spiral. The one that floats in the Troi."),
            ],
        },
        "objects": [
            {"id": "workbench", "label": "WORKBENCH", "kind": "lore", "prop": "desk", "lines": [
                say("self", "A service manual under the clutter. The cover reads: 'IBM 5100 — Maintenance.'"),
                say("self", "A photo tucked inside: a soldier who looks like he's seen everything twice. Like you."),
            ]},
            {"id": "photo", "label": "FAMILY PHOTOS", "kind": "lore", "prop": "poster",
             "take": "a family photo", "lines": [
                say("self", "Polaroids of the soldier holding the boy. On the back, in biro: 'came back for the 5100.'"),
            ]},
            {"id": "toolbox", "label": "TOOLBOX", "kind": "lore", "prop": "crate",
             "risky": True, "take": "a labelled cassette", "lines": [
                say("self", "A cassette labelled 'FOR ME, WHEN I FORGET AGAIN.' You have no player. Mercy, probably."),
            ]},
            {"id": "computer", "label": "OLD COMPUTER", "kind": "lore", "prop": "computer", "lines": []},
        ],
        "npcs": [
            {"id": "boy", "label": "THE BOY", "sprite": 1, "radius": 90, "lines": [
                say("john", "Are you the soldier? The old computer's under Dad's sheet. He says it reads languages nobody speaks yet."),
                say("john", "An IBM, he calls it. A 5100. Will I really go away one day? Did it work?"),
                say("self", "You don't answer. The honest answer is the saddest word you know: 'almost.'"),
            ]},
        ],
    },

    "1683": {
        "year": "1683", "theme": "observatory",
        "title": "The Year the Sky Was Watched",
        "place": "A cold observatory. Men chart a comet and fear it.",
        "zone_names": ["The Antechamber", "The Great Hall", "The Scriptorium",
                       "The Dome", "The Cloister", "The Crypt", "The Bell Tower",
                       "The Library", "The Cells"],
        "decor_kinds": ["pillar", "candle", "bookshelf", "shelf", "telescope", "table"],
        "brief": [
            say("boss", "1683. A man has drawn the Troi centuries too early, and locked it in a reliquary."),
            say("boss", "Open it. The key is in the sky he watches. Then burn what's inside."),
        ],
        "arrival": [
            "1683. Candlelight. Tallow and cold stone.",
            "A reliquary is locked. The astronomer hid the key in the comet's return.",
            "Do the arithmetic the sky keeps.",
        ],
        "puzzle": {
            "directive": "Open the RELIQUARY — the year the comet next returns.",
            "lock": "reliquary",
            "answer": ["1683"],
            "prompt": "RELIQUARY  //  THE YEAR THE COMET RETURNS",
            "solved": [
                say("self", "The lock yields. Inside: a manuscript of floating figures and a spiral named 'le troi.'"),
                say("self", "You hold the candle to it. The last legible line: 'the traveller will burn this. tell him we forgive him.'"),
            ],
        },
        "objects": [
            {"id": "ledger", "label": "STAR LEDGER", "kind": "lore", "prop": "bookshelf",
             "take": "a star-chart page", "lines": [
                say("self", "Columns of comet sightings. A note in the margin:"),
                say("self", "'It returns every 76 years. Last seen in 1607.'"),
            ]},
            {"id": "altar", "label": "ALTAR CANDLE", "kind": "lore", "prop": "candle", "lines": [
                say("self", "A fat candle, untended. You light a taper from it — for the pages, when you find them."),
            ]},
            {"id": "reliquary", "label": "RELIQUARY", "kind": "lore", "prop": "crate", "lines": []},
        ],
        "npcs": [
            {"id": "astronomer", "label": "ASTRONOMER", "sprite": 3, "radius": 90, "lines": [
                say("astronomer", "You. I dreamed you. You come from a tear in the air and burn my life's work."),
                say("astronomer", "The reliquary opens to the comet's next return. Last I saw it in 1607. Do the arithmetic; the sky keeps its appointments."),
                say("self", "He is not afraid. That is worse than if he were."),
            ]},
        ],
    },

    "3744": {
        "year": "3744", "theme": "ruin",
        "title": "Rehearsal for an Ending",
        "place": "A dead city, four centuries before yours. The keepers' home.",
        "zone_names": ["The Approach", "The Dead Plaza", "The Memorial",
                       "The Keeper Spire", "The Collapsed Mall", "The Dry Fountain",
                       "The Barracks", "The Transit Hub", "The Ash Garden"],
        "decor_kinds": ["rubble", "pillar", "barrel", "monument", "server", "crate"],
        "brief": [
            say("boss", "3744. The Keepers were built here. Their core only opens to the one it has counted."),
            say("boss", "It has counted you. Find the number. Shut the core down."),
        ],
        "arrival": [
            "3744. A city that died standing up. Keepers patrol even the empty.",
            "The core opens to a number — how many times it has kept you.",
            "The memorial remembers, even when you don't.",
        ],
        "puzzle": {
            "directive": "Shut down the KEEPER CORE — how many times has it kept you?",
            "lock": "core",
            "answer": ["3", "three"],
            "prompt": "KEEPER CORE  //  ITERATIONS LOGGED",
            "solved": [
                say("self", "You enter the number. The core admits what it has always known."),
                say("keeper", "TRAVELLER. YOU ARE NOT AUTHORISED. AND YET YOU ALWAYS ARRIVE."),
                say("self", "You pull the light apart. In the distance, the Keepers stutter and slump. For now."),
            ],
        },
        "objects": [
            {"id": "memorial", "label": "MEMORIAL", "kind": "lore", "prop": "monument",
             "risky": True, "take": "a name from the memorial", "lines": [
                say("self", "A monument of every traveller the Troi has kept."),
                say("self", "Your name is on it. Three entries. The third one's ink is still wet."),
            ]},
            {"id": "wreck", "label": "WRECKAGE", "kind": "lore", "prop": "crate",
             "risky": True, "take": "a keeper shard", "lines": [
                say("self", "A collapsed Keeper. You strip it for parts you don't need, because you shouldn't."),
                say("warden", "...logged... the city remembers you... it always remembers you..."),
            ]},
            {"id": "core", "label": "KEEPER CORE", "kind": "lore", "prop": "core", "lines": []},
        ],
        "npcs": [
            {"id": "warden", "label": "BROKEN KEEPER", "sprite": 2, "radius": 120, "lines": [
                say("warden", "I was built to stop you. I am too broken to stop anything."),
                say("warden", "The core counts every return. You are not new here. Count your own graves and it will open."),
            ]},
        ],
    },

    "24567 BC": {
        "year": "24567 BC", "theme": "cave",
        "title": "Where the Spiral Was Drawn First",
        "place": "A cave. Firelight. The oldest hand that ever drew the void.",
        "zone_names": ["The Cave Mouth", "The Hearth", "The Painted Wall",
                       "The Deep", "The Bone Pit", "The Drip", "The Hollow",
                       "The First Dark", "The Ledge"],
        "decor_kinds": ["stalagmite", "rubble", "crate"],
        "brief": [
            say("boss", "24567 BC. The deepest I've sent anyone. Someone drew the Troi on a wall here. Someone is waiting."),
            say("boss", "Read their wall. Then answer the figure honestly. I think you finally need to."),
        ],
        "arrival": [
            "24567 BC. The fire is the only modern thing here.",
            "A figure waits in the deep with one question.",
            "Read the wall before you dare to answer it.",
        ],
        "puzzle": {
            "directive": "Answer THE FIGURE: who truly gives the orders?",
            "lock": "figure",
            "answer": ["you", "me", "i", "myself", "us", "yourself", "prisoner 7"],
            "prompt": "THE FIGURE ASKS  //  WHO IS THE BOSS?",
            "solved": [
                say("figure", "Yes. There is no boss. There never was — only us, across the years, ordering ourselves onward."),
                say("figure", "The voice you call 'the boss' is you. An older, tireder you who gave up stopping the war and chose to schedule it."),
                say("self", "You look at the figure's face in the firelight. Of course. Of course it's yours."),
            ],
        },
        "objects": [
            {"id": "painting", "label": "PAINTED WALL", "kind": "lore", "prop": "painting", "lines": [
                say("self", "A figure steps out of a spiral, again and again, in a ring with no beginning."),
                say("self", "Beneath it, a tally. Thousands of marks. The last one is still wet. They are all you."),
            ]},
            {"id": "fire_obj", "label": "THE FIRE", "kind": "lore", "prop": "fire",
             "solid": False, "lines": [
                say("self", "You sit. The fire is warm in a way 4200 forgot. For one breath you almost remember your own name."),
            ]},
            {"id": "relic", "label": "OFFERING", "kind": "lore", "prop": "crate",
             "risky": True, "take": "the IBM 5100 shard", "lines": [
                say("self", "An offering at the wall: a beige shard of plastic that won't exist for twenty-six thousand years."),
                say("self", "Carried here. By you. You don't remember doing it. You will."),
            ]},
        ],
        "npcs": [
            {"id": "figure", "label": "THE FIGURE", "sprite": 3, "radius": 36, "lines": []},
        ],
    },
}

ERA_ORDER = ["2001", "1998", "1683", "3744", "24567 BC"]


ACHIEVEMENTS = [
    {"id": "titor", "name": "Titor's-traveller",
     "desc": "Beat the 2001 timeline.",
     "check": lambda f: "2001" in f["ever_eras"]},
    {"id": "ibm", "name": "IBM 5100",
     "desc": "Beat the 1998 timeline.",
     "check": lambda f: "1998" in f["ever_eras"]},
    {"id": "forbidden", "name": "They weren't supposed to know",
     "desc": "Burn the manuscript (1683) and shut down the core (3744).",
     "check": lambda f: "1683" in f["ever_eras"] and "3744" in f["ever_eras"]},
    {"id": "theboss", "name": "The Boss",
     "desc": "Learn who the boss really is.",
     "check": lambda f: "24567 BC" in f["ever_eras"]},
    {"id": "theend", "name": "The End..?",
     "desc": "Finish all five timelines.",
     "check": lambda f: all(e in f["ever_eras"] for e in ERA_ORDER)},
    {"id": "panic", "name": "Total Panic",
     "desc": "Slip away from the Time Keepers and escape a timeline.",
     "check": lambda f: f["escaped_keepers"]},
    {"id": "escape_troi", "name": "What",
     "desc": "Escape the Troi after the Keepers take you.",
     "check": lambda f: False},
]
