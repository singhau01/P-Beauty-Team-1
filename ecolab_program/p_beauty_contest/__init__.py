from tokenize import group
from otree.api import *


doc = """
    p_beauty_contest
"""


class C(BaseConstants):
    NAME_IN_URL = 'p_beauty_contest'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 4

    timeout_sec = 30  # 每一回合的決策時間
    timer_sec = 20  # 出現timer的剩餘時間
    alert_sec = 10  # 出現提醒字樣的剩餘時間

    p = 2/3
    min_number = 0
    max_number = 100

    winning_prize = 100
    consolation_prize = 10
    
    big_group_player_num = 2
    small_group_player_num = 1






class Subsession(BaseSubsession):
    pass
    


class Group(BaseGroup):
    time_pressure = models.BooleanField
    is_treatment = models.BooleanField(initial=False)  #實驗組與控制組

    num_list_big = models.StringField(initial="被選到的號碼有：")
    winner_number_big = models.StringField(initial="本回合贏家的數字是：")
    p_mean_num_big = models.FloatField(initial=-100)

    num_list_small = models.StringField(initial="被選到的號碼有：")
    winner_number_small = models.StringField(initial="本回合的贏家數字是：")
    p_mean_num_small = models.FloatField(initial=-100)


class Player(BasePlayer):
    guess_num = models.IntegerField(min=C.min_number, max=C.max_number, label='請輸入您所猜測的非負整數：')
    is_winner = models.BooleanField(initial=False)
    is_big_group =  models.BooleanField(initial=False)
    is_small_group = models.BooleanField(initial=False)
    decision_duration = models.FloatField(initial=0)  # 決策時間
    is_no_decision = models.BooleanField(initial=False)  # 是否有進行決策


# FUNCTIONS

def creating_session(subsession):  # 把組別劃分成實驗組與控制組、大組或小組
    import random

    if subsession.round_number == 1:

        treatment = random.sample(subsession.get_players(), C.PLAYERS_PER_GROUP) # 一半分到對照組，一半分到實驗組
        control = list(set(subsession.get_players()) - set(treatment))

        treatment_big = random.sample(treatment, C.big_group_player_num) # 實驗組抽10個，分為大組
        treatment_small = list(set(treatment) - set(treatment_big)) # 實驗組剩3個為小組
        control_big = random.sample(control, C.big_group_player_num) # 控制組抽10個，分為大組
        control_small = list(set(control) - set(control_big)) # 控制組抽3個，分為小組

            
        for player in subsession.get_players():
            if player in treatment:
                player.group.is_treatment == True

            if player in treatment_big or player in control_big:
                player.is_big_group = True

            


def set_payoffs(group: Group):
    players_guess_dict_big = {}  # {guess_num: players}
    players_guess_dict_small = {}
    total_big = 0
    total_small = 0
    playing_player_big = 0
    playing_player_small = 0


    # 將所有受試者的數字以 dictionary 形式存下來
    for player in group.get_players():
        if player.is_big_group:
            if player.is_no_decision == False:
                players_guess_dict_big[player] = player.guess_num
                total_big += player.guess_num
                group.num_list_big += str(player.guess_num) + " "
                playing_player_big += 1

        else:
            if player.is_no_decision == False:
                players_guess_dict_small[player] = player.guess_num
                total_small += player.guess_num
                group.num_list_small += str(player.guess_num) + " "
                playing_player_small += 1
        


    if playing_player_big > 0:
        mean_big = total_big / C.big_group_player_num
        group.p_mean_num_big = mean_big * C.p
        min_distance_big = 100
        for p in group.get_players():
            if p.is_big_group == True:
                if abs(players_guess_dict_big[p] - group.p_mean_num_big) <= min_distance_big:
                    min_distance_big = abs(players_guess_dict_big[p] - group.p_mean_num_big)
        n_winners_big = 0 # 有多少個贏家
        win_num = -100
        win2_num = -100
        for player, num in players_guess_dict_big.items():
            if abs(num - group.p_mean_num_big) == min_distance_big:
                player.is_winner = True
                n_winners_big += 1
                if win_num != num and win_num != win2_num:
                    win2_num = num
                else:
                    win_num = num
            else:
                player.payoff = C.consolation_prize
        if win2_num == -100:
            group.winner_number_big += str(win_num)
        else:
            group.winner_number_big += str(win_num) + "、" + str(win2_num)


    elif playing_player_small > 0:
        mean_small = total_small / C.small_group_player_num
        group.p_mean_num_small = mean_small * C.p
        min_distance_small = 100
        for p in group.get_players():
            if p.is_small_group == True:
                if abs(players_guess_dict_small[p] - group.p_mean_num_small) <= min_distance_small:
                    min_distance_small = abs(players_guess_dict_small[p] - group.p_mean_num_small)
        n_winners_small = 0 # 有多少個贏家
        win3_num = -100
        win4_num = -100
        for player, num in players_guess_dict_big.items():
            if abs(num - group.p_mean_num_small) == min_distance_small:
                player.is_winner = True
                n_winners_small += 1
                if win3_num != num and win3_num != win4_num:
                    win4_num = num
                else:
                    win3_num = num
            else:
                player.payoff = C.consolation_prize
        if win4_num == -100:
            group.winner_number_small += str(win3_num)
        else:
            group.winner_number_small += str(win3_num) + "、" + str(win4_num)

    

    for player in group.get_players():
        if player.is_winner:
            if player.is_big_group:
                player.payoff = C.winning_prize / n_winners_big
            elif player.is_small_group:
                player.payoff = C.winning_prize / n_winners_small
            else:
                player.payoff = C.no_playing_prize
    group.num_list_big = group.num_list_big[:-1]
    group.num_list_small = group.num_list_small[:-1]

        


# PAGES
class Instruction(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.round_number == 1  # 只有 round 1 要有實驗說明

class DecisionPage(Page):
    form_model = 'player'
    form_fields = ['guess_num', 'decision_duration']
    timeout_seconds = C.timeout_sec  # built-in

    @staticmethod
    def before_next_page(player, timeout_happened):  # built-in methods
        if timeout_happened:
            player.is_no_decision = True  # 若回合時間到，將 player 設定為沒有做決策


class ResultsWaitPage(WaitPage): # built-in
    after_all_players_arrive = set_payoffs  # built-in methods，所有受試者都離開決策頁後，執行 set_payoffs


class Results(Page):
    pass


class Finish(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
        
    @staticmethod
    def vars_for_template(player: Player):  # built-in methods，將 total_payoff 的值傳到 html 頁面
        return {
            "total_payoff": sum([p.payoff for p in player.in_all_rounds()])
	    }


page_sequence = [Instruction, DecisionPage, ResultsWaitPage, Results, Finish]
