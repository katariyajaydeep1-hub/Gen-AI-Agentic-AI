from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain_openai import ChatOpenAI
from datetime import datetime
from dotenv import load_dotenv

import os


# =========================================================
# LOAD ENV VARIABLES
# =========================================================
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")


# =========================================================
# CREATE CHAT MODEL ONCE
# =========================================================
chat = ChatOpenAI(
    openai_api_key=api_key,
    model="gpt-4o-mini",
    temperature=0.3
)


# =========================================================
# HISTORY QUIZ CLASS
# =========================================================
class HistoryQuiz():

    def create_history_question(self, topic):

        system_template = (
            "You write a single quiz question about {topic}. "
            "Return ONLY the question."
        )

        system_message_prompt = (
            SystemMessagePromptTemplate.from_template(system_template)
        )

        human_template = (
            "Give me a quiz question where the correct answer is a specific historical date."
        )

        human_message_prompt = (
            HumanMessagePromptTemplate.from_template(human_template)
        )

        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            human_message_prompt
        ])

        request = chat_prompt.format_prompt(
            topic=topic
        ).to_messages()

        result = chat.invoke(request)

        return result.content.strip()


    def get_AI_answer(self, question):

        system_template = (
            "You answer the quiz question using ONLY a date "
            "in this exact format: YYYY-MM-DD"
        )

        system_message_prompt = (
            SystemMessagePromptTemplate.from_template(system_template)
        )

        human_template = """
Answer this history question with the exact date:

{question}
"""

        human_message_prompt = (
            HumanMessagePromptTemplate.from_template(human_template)
        )

        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            human_message_prompt
        ])

        request = chat_prompt.format_prompt(
            question=question
        ).to_messages()

        result = chat.invoke(request)

        try:
            correct_datetime = datetime.strptime(
                result.content.strip(),
                "%Y-%m-%d"
            )

            return correct_datetime

        except Exception:
            print("\n[ERROR] Could not parse AI date:")
            print(result.content)

            return None


    def get_user_answer(self, question):

        print("\n=================================================")
        print("QUESTION:")
        print(question)
        print("=================================================")

        while True:

            try:
                year = int(input("Enter the year  : "))
                month = int(input("Enter the month : "))
                day = int(input("Enter the day   : "))

                user_datetime = datetime(year, month, day)

                return user_datetime

            except ValueError:
                print("\nInvalid date entered. Try again.\n")


    def check_user_answer(self, user_answer, ai_answer):

        if ai_answer is None:
            print("\nCould not evaluate answer.")
            return

        result = abs((user_answer - ai_answer).days)

        print("\n=================================================")
        print("RESULT")
        print("=================================================")

        print("Correct Answer :", ai_answer.strftime("%B %d, %Y"))
        print("Your Answer    :", user_answer.strftime("%B %d, %Y"))
        print("Difference     :", result, "days")


# =========================================================
# RUN QUIZ
# =========================================================
quiz = HistoryQuiz()

topic = "World War 2"

question = quiz.create_history_question(topic)

ai_answer = quiz.get_AI_answer(question)

user_answer = quiz.get_user_answer(question)

quiz.check_user_answer(user_answer, ai_answer)