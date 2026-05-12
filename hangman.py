import random

HANGMAN_PICS = [
    """
      +---+
          |
          |
          |
         ===
    """,
    """
      +---+
      O   |
          |
          |
         ===
    """,
    """
      +---+
      O   |
      |   |
          |
         ===
    """,
    """
      +---+
      O   |
     /|   |
          |
         ===
    """,
    """
      +---+
      O   |
     /|\  |
          |
         ===
    """,
    """
      +---+
      O   |
     /|\  |
     /    |
         ===
    """,
    """
      +---+
      O   |
     /|\  |
     / \  |
         ===
    """
]

WORDS = ["python", "hangman", "game", "programming", "computer", "keyboard", "internet", "software"]

def hangman():
    word = random.choice(WORDS)
    guessed_letters = []
    wrong_guesses = 0
    
    print("欢迎来到绞刑架游戏！")
    
    while wrong_guesses < len(HANGMAN_PICS) - 1:
        print(HANGMAN_PICS[wrong_guesses])
        display_word = "".join([letter if letter in guessed_letters else "_" for letter in word])
        print(f"\n当前单词: {display_word}")
        print(f"已猜字母: {', '.join(guessed_letters) if guessed_letters else '无'}")
        
        guess = input("请猜一个字母: ").lower()
        
        if len(guess) != 1 or not guess.isalpha():
            print("请输入一个有效的字母！")
            continue
        
        if guess in guessed_letters:
            print("你已经猜过这个字母了！")
            continue
        
        guessed_letters.append(guess)
        
        if guess in word:
            print("猜对了！")
            if all(letter in guessed_letters for letter in word):
                print(f"\n恭喜你！你猜对了单词: {word}")
                break
        else:
            wrong_guesses += 1
            print(f"猜错了！还剩 {len(HANGMAN_PICS) - 1 - wrong_guesses} 次机会。")
    
    if wrong_guesses == len(HANGMAN_PICS) - 1:
        print(HANGMAN_PICS[-1])
        print(f"\n游戏结束！正确的单词是: {word}")

if __name__ == "__main__":
    hangman()