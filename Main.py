import json
import gradio as gr
import os
import openai
import requests
import time
# import db_connect
import psycopg2
from converter import Converter
## 업무목표 주간보고 >> 월간 >> 반기보고
## 1. 받은 이름을 바탕으로 데이터베이스에 일일보고 내용 저장
## 2. 생성된 주간보고서 내용을 이름을 기준으로 db에 저장
## 스키마 테이블


## 전역으로 설정
instruction_message_list_system = [

    ## 소개 > 보고요청 > 주간보고서를만들어 줄지 물어보기 > 아니오면 보고요청모드 예면 보고만들기
    ## 이렇게 하지말고 모드 설정으로 가는게 나을거같다 일일보고모드, 주간보고 버튼, 월간 보고 모드
    "안녕하세요 아래에 성함을 입력해주세요 ",
    "일일보고 버튼을 누르면 일일보고를 할 수 있습니다. 주간보고 버튼을 누르면 일일보고 내용을 바탕으로 주간보고서를 만들어 줍니다.",

]
instruction_message_list_today = [
    "일일보고를 기록하는 모드입니다.",
    "일자와 업무내용, 추후계획에 대해 적어주세요 정확할수록 좋습니다.",
    "입력완료.",

]

instruction_message_list_weekly = [
    "사용자가 입력한 내용을 주간보고로 편집할 것입니다.",
    "입력받은 내용에서 일자를 확인하여 올해의 월과 몇 주차인지를 파악합니다."
    "확인한 월과 주차를 바탕으로 보고서 제목은 확인된 월 주차 보고서로 정합니다.",
    "입력받은 내용을 일자별로 분리합니다. 이때 없는 일자에 대한 내용은 생성하지 않습니다. 또한 추후 계획이란 말이 들어있다면 따로 저장해놓습니다.",
    "일자별로 분리한 내용을 보고내용 항목에 넣습니다.",
    "추후계획으로 저장해 놓은 내용을 추후계획이란 항목을 생성하여 입력합니다.",
    "완성된 주간보고서를 보여줍니다."
]

## 현재 유저, 현재 모드를 전역으로 설정
mode = 0
# 이름
user = ''


# db = Databases()
# crud = CRUD(db)


# currentMode = gr.State()


## 현재 모드는 크게 3가지 0은 일일보고 1은 주간보고 2는 월간보고
def saveId(name):
    global user
    user = name




def get_environment(input_message):
    with open('C:\\Users\\고명섭\\PycharmProjects\\OrganazieReports\\api_key.txt', 'r') as f:
        api_key = f.read().strip()
    openai.api_key = api_key
    # f = open("/api_key.txt", 'r')

    ## 직접 노출시키면 open ai 가 지워버림 파일로 저장해서 불러오는게 나음
    # openai.api_key = line

    start = time.time()
    ## message는 role 과 content로 들어가야함
    res = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                       messages=input_message)
    # print(res)
    ret = res['choices'][0]['message']['content']
    # print(ret)
    return ret


#
#
visit = False
data = []
dataForUser = []
first = True


def process_scenario():
    global pred_func

    # 1. 지금 처리하는게 처음이라면 모드 설정후 인스트럭션을 넣게 만들고
    # 2. 만약에 이전에 방문했다면 mode설정은 무시하고 처리
    ## 데모로 시작될때를 생각해야돼
    ## 지금은 첫방문이라 가정

    # dataForUser.append(user_message)
    if mode == 2:
        # print("주간보고모드입니다.")
        ## db에서 지금까지 작업했던 내용을 불러와서 입력
        ## 리스트로 전달가능한지 확인
        a = ''.join(dataForUser)
        # a.append(d[0])
        data.append({"role": "system", "content": instruction_message_list_weekly[0]})
        data.append({"role": "user", "content": "{} 이걸 사용해서 주간보고서를 만들어줘".format(a)})
        for msg in instruction_message_list_weekly:
            data.append({"role": "system", "content": "{}".format(msg)})

    # 여기에 name으로 얘가 지금까지 ai랑 대화했던 내역 ()
    query_message = []
    for msg in data:
        query_message.append(msg)
    print("쿼리메시지", query_message)
    assistant_message = pred_func(query_message)

    return assistant_message


#
def predict_demo(user_input, state):
    global mode

    if mode == 2:
        ## ai한테 물어본 결과거든?
        response = process_scenario()
        state = state + [(user_input, None)]
        ## user별 주간보고 저장
        response_items = response.split('\n\n')
        cv = Converter(response_items[0], response_items[1:-1], response_items[-1])
        cv.setting()
        for item in response_items:
            state = state + [(None, item)]


    ## mode가 0이면 처음설명
    elif mode == 0:
        saveId(user_input)
        state = state + [(user_input, None)]
        state = state + [(None, "입력완료")]


    ## 1번모드가 일일보고하는 모드야
    elif mode == 1:
        ## 처음 버튼을 눌렀을 때만 작동하도록

        state += [(user_input, None)]

        state += [(None, instruction_message_list_today[2])]
        ## 나중에 지우고
        dataForUser.append(user_input)
        ## 여기다가 이름별로 일일보고 저장
    print("chat state", state, user_input)
    ## state는 지금까지 대화 내용을 저장하는것
    # print(state)
    return state, state


# 유저가 입력한 값과, chat_state를 가지고 predic_demo로 넘기는 부분
def demo_load(user_input, chat_state):
    # print(mode, user)
    # print(type(chat_state))
    chat_state += [(None, instruction_message_list_system[0])]
    chat_state += [(None, instruction_message_list_system[1])]

    # chat_state += [(user_input, None)]
    # chat_state, _ = predict_demo("", chat_state)

    return chat_state, chat_state


def choiceMode1(chat_state):
    global mode
    ## 모드의 종류에 따라 instruction이 달라짐
    mode = 1
    # dataForUser.append
    for i in range(2):
        chat_state += [(None, instruction_message_list_today[i])]
    # chat_state, _ = predict_demo("", chat_state)
    # print(mode)
    return chat_state, chat_state


def choiceMode2(chat_state):
    ## 내가 버튼을 누르면 지금까지 내가 했던 내용을 db에서 불러오고
    global mode
    ## 모드의 종류에 따라 instruction이 달라짐
    mode = 2

    chat_state += [(None, "주간보고서 모드입니다.")]
    chat_state, _ = predict_demo("", chat_state)
    ## 여기서 워드파일로 바꿔주는 부분이 필요함


    return chat_state, chat_state







#
#
#
def demo_start(func):
    global pred_func

    # db = init_db()

    try:
        pred_func = func

        with gr.Blocks() as demo:
            # user = gr.State([])
            ## 여기가 사람들한테 보여지는 내용
            chatbot = gr.Chatbot()

            chat_state = gr.State([])

            with gr.Row():
                ## 버튼 인터페이스 > 보고 모드, 주간보고 출력, 월간보고 출력, 분기보고 출력
                btn1 = gr.Button(value="일일보고모드")
                btn2 = gr.Button(value="주간보고 출력")
                # btn3 = gr.Button(value="월간보고 출력")

                btn1.click(choiceMode1, inputs=[chat_state], outputs=[chatbot, chat_state])
                btn2.click(choiceMode2, inputs=[chat_state], outputs=[chatbot, chat_state])
                # btn3.click(choiceMode3)
            # print(mode)
            with gr.Row():
                user_input = gr.Textbox(show_label=False, placeholder="메시지를 입력한 후 엔터를 눌려주세요.").style(container=False)
            ## load에서 inputs = componet 중 무엇을 사용할 것인지, output은 무엇을 뱉어낼 것인지
            demo.load(demo_load,
                      inputs=[user_input, chat_state],
                      outputs=[chatbot, chat_state]
                      )

            user_input.submit(predict_demo,
                              inputs=[user_input, chat_state],
                              outputs=[chatbot, chat_state])

            user_input.submit(lambda: "", None, user_input)
        demo.launch(share= True)

    except Exception as e:
        print("errror", e)


if __name__ == "__main__":
    demo_start(get_environment)
