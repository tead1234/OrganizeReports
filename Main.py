import json
import gradio as gr
import os
import openai
import requests
import time


## 업무목표 주간보고 >> 월간 >> 반기보고
# 1. db를 선택하고 그걸 여기에 연결
# 2. method  >> db schema  id, name, 방문여부(0,1), 그간 대화내역 (system으로 입력한거, 유저로 입력한),일일보고 (dic.toString), 주간보고, 월간보고 , 분기보고
# 2-1. db를 다루는 sql 작성  당장 필요한 sql name으로 일일보고 가져오기 , name으로 방문 여부 체크 (True or False), db에 저장하는거
# 3. (주간보고 트리거) ai한테 일일보고를 하다가 특정갯수이상 (5이상 쌓이면) 사용자한테 "주간보고서를 만들까요?" >> "yes or no"
# (2번째 트리거) 수동모드 ai한테 주간보고를 만들어줘(갯수 x) >> "making report"




current_user =''
## 전역으로 설정
instruction_message_list = [

    "당신은 사용자가 입력하는 보고내용을 모아서 보고서로 작성해주는 역할을 합니다.",
    "사용자에게 오늘 한 일에 대해 물어보세요",
    "사용자가 입력한 내용을 모아서 이번주에 있었던 일에 대해 정리해주세요",
    "x월 x일부터 y월 y일까지 보고를 주간보고로 만들어줘"
]

def saveId(name):
    current_user = name
    return current_user
def get_environment(input_message):


    openai.api_key = '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'

    start = time.time()
    ## message는 role 과 content로 들어가야함
    res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "{}".format(input_message)}])
    # print(res)
    ret = res['choices'][0]['message']['content']
    print(ret)
    return ret

#
#
def process_scenario(user_message, instruction_message):
    global pred_func
    ## 원래 함수는 db에 저장해놓은걸 다 긁어와서 한번에 쿼리를 난리는데
    ## 이건 테스트니깐 그냥 원시적으로 넣음



    ## pred_func == get_environment 즉 model한테 질문하는것
    # add_message(user_id, str({"role": "user", "content": user_message}))
    ## instruction_message는 미리 모델한테 인지시키는것
    # if len(instruction_message) > 0:
        # add_message(user_id, str({"role": "system", "content": instruction_message}))

    # all_message = get_message_history(user_id)
    ## role >> system , assistant >> ai의 대답, user >> 질문하는거야
    # {"role": "user", "content": user_message}, {"role": "system", "content": instruction_message}
    # 여기에 name으로 얘가 지금까지 ai랑 대화했던 내역 ()
    query_message = []

    # for msg in all_message:
    #     query_message.append(eval(msg[0]))
    ## 어시스턴스 메시지는 open ai한테 물어보고 나온 답변
    assistant_message = pred_func(query_message)
    ##

    # add_message(user_id, str({"role": "assistant", "content": assistant_message}))

    return assistant_message
#
def predict_demo(user_input, state):
    instruction_message = ''
    ## USER_INPUT을 사용하는 부분이 ㅇ벗는데 ?????

    # instruction_message_idx = get_instruction_message_count(user_id)

    # history_count = get_message_log_history_count(user_id)

    # if instruction_message_idx < len(instruction_message_list):

        # if instruction_message_idx == 0:

    additional_comment = '첫 방문한 사용자이니 첫방문에 대해 감사의 말을 작성합니다.'
    instruction_message = instruction_message_list[0]
        #     if history_count > 0:
        #         additional_comment = '재방문한 사용자이니 다시 찾아온 것에 대해 감사의 말을 작성합니다.'
        #
        #     instruction_message = additional_comment + instruction_message_list[instruction_message_idx]
        # else:
    instruction_message += additional_comment
    ## 이부분이 assistant에게 알려주는 역할?
    response = process_scenario(user_input, instruction_message)

    state = state + [(user_input, None)]

    response_items = response.split('\n\n')

    for item in response_items:
        state = state + [(None, item)]


    ## state는 지금까지 대화 내용을 저장하는것
    # print(state)
    return state, state
# 유저가 입력한 값과, chat_state를 가지고 predic_demo로 넘기는 부분
def demo_load(user_input,chat_state):

    chat_state, _ = predict_demo(user_input, chat_state)

    return chat_state, chat_state
#
#
#
def demo_start(func):
    global pred_func

    # init_db()

    try:
        pred_func = func

        # gr.Textbox(show_label= False, placeholder= "이름을 입력해주세요")
        with gr.Blocks() as demo:
            userid = gr.Textbox(show_label=False, placeholder="이름을 입력해주세요")
            # userid.submit(saveId, inputs=[userid], outputs= [current_user])
            print(current_user)
            chatbot = gr.Chatbot()
            chat_state = gr.State([])

            with gr.Row():
                user_input = gr.Textbox(show_label=False, placeholder="메시지를 입력한 후 엔터를 눌려주세요.").style(container=False)
            ## load에서 inputs = componet 중 무엇을 사용할 것인지, output은 무엇을 뱉어낼 것인지
            demo.load(demo_load,
                      inputs=[user_input,chat_state],
                      outputs=[chatbot, chat_state]
                      )

            user_input.submit(predict_demo,
                              inputs=[user_input, chat_state],
                              outputs=[chatbot, chat_state])

            user_input.submit(lambda: "", None, user_input)
        demo.launch()
        # demo.launch(server_name="0.0.0.0", debug=True)

    except Exception as e:
        # sendResultForDemoAPI(str(e))
        print(e)
if __name__ == "__main__":
    demo_start(get_environment)