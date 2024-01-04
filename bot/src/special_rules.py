# choose

CHOOSE_CHEATS = {
    # "everyone": rules for  everyone
    # talking_crow 334626027961712642
    'everyone': {
        'active': True,
        'combos': [  # the first one is always picked
            ['d', 'a'],
            ['m', 'p'],
            ['dm', 'ap'],
            ['md', 'pa']
        ]
    }
}


def check_choose_cheat(choices, user):
    rules = CHOOSE_CHEATS.get(str(user), None) or CHOOSE_CHEATS.get('everyone', None)
    if not rules:
        return False, None

    lower_choices = [ch.lower() for ch in choices]
    for combo in rules['combos']:
        if all(ch in combo for ch in lower_choices):
            return True, choices[lower_choices.index(combo[0])]

    return False, None
