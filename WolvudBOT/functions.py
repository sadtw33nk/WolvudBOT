from random import randint


def get_level_group(messages):
    level = messages // 200

    return level

def get_level_member(messages):
    level = messages // 100

    return level

def get_achievement():
    achievement = 'none'
    rand = randint(0, 1000000)
    if rand == 1000:
        achievement = 'Трап'
    if rand == 10000:
        achievement = 'Хуйня какая-то'
    if rand == 100000:
        achievement = 'Фурри гей'
    if rand == 1000000:
        achievement = 'Название не придумал'

    return achievement
