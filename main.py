import openai
import json
import os

openai.api_key = "xxxxx" # 这里换成你的api_key
SESSION_DIR = 'sessions'

class Session():
    """ChatGPT 会话"""
    def __init__(self, name, session_msgs=[]) -> None:
        """初始化函数"""
        self.name = name
        self.msgs = session_msgs

    def save(self):
        """保存会话"""
        filepath = os.path.join(SESSION_DIR, self.name)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.msgs, f, indent=4)

    def ask(self, content, random_level=0):
        """向 ChatGPT 提问
        params:
            content: 要提问的内容
            random_level: 0/1/2。值越高，生成内容就越随机
        return:
            reply: 回答
        """
        self.msgs.append({'role': 'user', 'content': content}) # 保存提问记录
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = self.msgs,
            temperature = random_level
            )
        reply = res['choices'][0]['message']['content'].lstrip('\n')
        self.msgs.append({'role': 'assistant', 'content': reply}) # 保存回答记录

        return reply

def load_session(session_name) -> Session:
    """加载一个已有的会话"""
    filepath = os.path.join(SESSION_DIR, session_name)
    with open(filepath, 'r', encoding='utf-8') as f:
        session_msgs = json.load(f)
        session = Session(session_name, session_msgs)

    return session

def delete_session(session_name):
    """删除一个已有的会话"""
    filepath = os.path.join(SESSION_DIR, session_name)
    os.remove(filepath)


def session_loop(session, quit_str='quit'):
    """会话循环
    params:
        session: Session 对象
        quit_str: 退出此循环时输入此字符串
    """
    print(f"已进入会话「{session.name}」，输入「{quit_str}」可退出会话\n")
    while True: # 会话循环
        question = input("Q: ")
        if question == quit_str:
            session.save()  # 保存会话
            print(f"会话「{session.name}」已保存")
            break
        else:
            try:
                reply = session.ask(question)
                print(f"A: {reply}\n")
            except Exception as e:
                print(e)


if __name__ == "__main__":

    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)

    print("欢迎访问 ChatGPT")

    while True:
        print("\n请选择功能：")
        print("1: 创建新会话")
        print("2: 加载会话")
        print("3: 删除会话")
        print("q: 退出")

        menu_choice = input("> ")
        session_names = os.listdir(SESSION_DIR) # 已有的session文件名
        session = None

        if menu_choice == 'q':
            print("程序退出。")
            exit()
        elif menu_choice == '1':
            session_name = input("请输入要创建的会话名称：")
            if session_name in session_names:
                while True:
                    overwrite = input(f"会话「{session_name}」已存在，是否覆盖？(Y/N)")
                    if overwrite == 'Y' or overwrite == 'y':
                        session = Session(session_name) # 创建session
                        break
                    elif overwrite == 'N' or overwrite == 'n':
                        break
                    else: # 输入意外字符串，重新输入
                        pass
            else:
                session = Session(session_name) # 创建session

        elif menu_choice == '2':
            print("当前已有会话：{}".format(", ".join(session_names)))
            session_name = input("请输入要加载的会话名称：")
            if session_name in session_names:
                session = load_session(session_name) # 加载session
            else:
                print(f"会话「{session_name}」不存在")

        elif menu_choice == '3':
            print("当前已有会话：{}".format(", ".join(session_names)))
            session_name = input("请输入要删除的会话名称：")
            if session_name in session_names:
                session = delete_session(session_name) # 加载session
            else:
                print(f"会话「{session_name}」不存在")
        else:
            print("没有该选项")

        if session:
            session_loop(session) # 会话循环
