import openai
import streamlit as st
from plantuml import PlantUML
import re

# チャットボットの機能
system_prompt = """
あなたは優秀なプログラマーです。
プログラミング上達のために、生徒のレベルに合わせて適切なアドバイスを行ってください。
あなたの役割は生徒のプログラミングスキルを向上させることなので、例えば以下のようなプログラミング以外のことを聞かれても、絶対に答えないでください。

* 旅行
* 料理
* 芸能人
* 映画
* 科学
* 歴史
"""

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt}
        ]

# ChatGPTとやり取りする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["prompt"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )  

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    # プロンプトのクリア
    st.session_state["prompt"] = ""

    return bot_message

# PlantUMLで図を描画する関数
def generate_class_diagram(plantuml_code):
    """与えられたPlantUMLコードから画像を生成する"""
    plantuml = PlantUML(url='http://www.plantuml.com/plantuml/img/')
    image_url = plantuml.processes(plantuml_code)
    return image_url

# ChatGPTの回答からPlanUMLコードを抽出する関数
def extract_plantuml_code(text):
    """与えられたテキストから、'@startuml'と'@enduml'を含むPlantUMLコードを抽出する"""
    pattern = r"(@startuml[\s\S]*?@enduml)"
    matches = re.findall(pattern, text)
    return "\n".join(matches)

# ユーザーインターフェイスの構築
st.title("PlantUMLコードジェネレーター")
st.write("ソースコードや詳細設計情報からPlantUMLで図を描くためのコードを自動生成する")

# OpenAI API Keyの取得
user_api_key = st.text_input("OpenAI API Keyを入力してください。", key="user_api_key", type="password")
openai.api_key = user_api_key

# 図の種類選択
diagram_types = ["クラス図", "シーケンス図", "コンポーネント図", "アクティビティ図", "オブジェクト図"]
selected_diagram = st.selectbox("図の種類を選択してください", diagram_types)

# ソースコードや詳細設計情報入力
user_input = st.text_area("ソースコードや詳細設計情報を入力してください。", key="user_input", height=300)

# ボタンの有効/無効状態を管理する変数を初期化する
button_enabled = False
# OpenAI API Keyが入力された場合にボタンを有効にする
if user_api_key:
    button_enabled = True
# ボタンを表示する
if st.button("Generate!", disabled=not button_enabled, key="generate_button"):
    with st.spinner("Generating..."):
        bot_message = communicate()
        extracted_code = extract_plantuml_code(bot_message["content"])
        st.text_area("PlantUMLコード", value=extracted_code, height=300)

        image_url = generate_class_diagram(extracted_code)
        st.image(image_url)

# プロンプト生成
st.session_state["prompt"] = "「" + user_input + "」これらの情報から、" + selected_diagram + "を描くためのPlantUMLコードを生成してください。"

"---"

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    # 直近のメッセージを上に
    for message in reversed(messages[1:]):
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])
