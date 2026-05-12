import random

def guess_number():
    print("欢迎来到猜数字游戏！")
    print("我已经想好了一个1到100之间的数字。")
    secret_number = random.randint(1, 100)
    attempts = 0
    
    while True:
        try:
            guess = int(input("请输入你的猜测: "))
            attempts += 1
            
            if guess < secret_number:
                print("太小了！再试试。")
            elif guess > secret_number:
                print("太大了！再试试。")
            else:
                print(f"恭喜你！猜对了！答案是 {secret_number}")
                print(f"你用了 {attempts} 次猜对。")
                break
        except ValueError:
            print("请输入有效的数字！")

if __name__ == "__main__":
    guess_number()