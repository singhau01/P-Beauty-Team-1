from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    name = models.StringField(label="你的名字：")
    age = models.IntegerField(label="你的年紀：")
    is_eco_or_man_stu = models.BooleanField(label="是否為經濟系或管理學院")
    has_studied_eco_class = models.BooleanField(label="有沒有修過經濟學的課")
    know_pbeauty = models.BooleanField(label="有沒有聽過p-beauty contest")
    guess_goal = models.LongStringField(label="猜猜看實驗目的")

# FUNCTIONS
# PAGES
class Survey(Page):
    form_model = 'player'
    form_fields = ["name", "age", "is_eco_or_man_stu", "has_studied_eco_class", "know_pbeauty", "guess_goal"]

class Finish(Page):
    pass


page_sequence = [Survey, Finish]
