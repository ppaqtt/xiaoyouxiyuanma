import random

def get_computer_choice():
    choices = ["石头", "剪刀", "布"]
    return random.choice(choices)

def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "平局"
    elif (player_choice == "石头" and computer_choice == "剪刀") or \
         (player_choice == "剪刀" and computer_choice == "布") or \
         (player_choice == "布" and computer_choice == "石头"):
        return "玩家获胜"
    else:
        return "电脑获胜"

def rock_paper_scissors():
    print("欢迎来到石头剪刀布游戏！")
    print("规则：石头赢剪刀，剪刀赢布，布赢石头")
    
    player_score = 0
    computer_score = 0
    
    while True:
        player_choice = input("请输入你的选择 (石头/剪刀/布): ")
        if player_choice not in ["石头", "剪刀", "布"]:
            print("请输入有效的选择！")
            continue
        
        computer_choice = get_computer_choice()
        print(f"电脑选择了: {computer_choice}")
        
        result = determine_winner(player_choice, computer_choice)
        print(result)
        
        if result == "玩家获胜":
            player_score += 1
        elif result == "电脑获胜":
            computer_score += 1
        
        print(f"当前比分: 玩家 {player_score} - {computer_score} 电脑")
        
        play_again = input("继续游戏吗？(是/否): ")
        if play_again != "是":
            print("游戏结束！")
            break

if __name__ == "__main__":
    rock_paper_scissors()