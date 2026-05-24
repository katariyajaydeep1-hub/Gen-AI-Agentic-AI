"""
Assignment 3.3 — LangChain Quiz Master
A 10-question history quiz that scores you on how close your date answers
are to the AI's.
"""

import os
import random
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers.datetime import DatetimeOutputParser
from langchain_openai import ChatOpenAI


# ===================================================================
# Configuration
# ===================================================================
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY missing in .env")

chat_model = ChatOpenAI(
    api_key=api_key,
    model="gpt-4o-mini",
    temperature=0.3,
)


# ===================================================================
# Topics Pool
# ===================================================================
HISTORY_TOPICS = [
    "World War II",
    "the Indian independence movement",
    "the Apollo space program",
    "the Cold War",
    "the French Revolution",
    "the discovery of penicillin",
    "the Berlin Wall",
    "the American Civil War",
    "the invention of the telephone",
    "the September 11 attacks",
    "the fall of Constantinople",
    "the Mughal Empire in India",
    "the Russian Revolution",
    "the founding of the United Nations",
    "the Wright Brothers' first flight",
]


# ===================================================================
# Quiz Class
# ===================================================================
class HistoryQuiz:

    def __init__(self, chat):
        self.chat = chat
        self.date_parser = DatetimeOutputParser()

    def create_history_question(self, topic):
        system_template = (
            "You write a single quiz question about {topic}. "
            "The correct answer MUST be a specific historical date "
            "(day, month, year — or at minimum month and year). "
            "Return ONLY the question text."
        )

        system_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_prompt = HumanMessagePromptTemplate.from_template(
            "Give me a quiz question where the correct answer is a specific date."
        )

        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

        request = chat_prompt.format_prompt(topic=topic).to_messages()

        result = self.chat.invoke(request)
        return result.content.strip()

    def get_AI_answer(self, question):
        system_template = (
            "You answer the quiz question with JUST a date. No explanation."
        )

        system_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_template = (
            "Answer with the exact historical date:\n"
            "{question}\n\n"
            "Format instructions:\n{instructions}"
        )

        human_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

        request = chat_prompt.format_prompt(
            question=question,
            instructions=self.date_parser.get_format_instructions(),
        ).to_messages()

        result = self.chat.invoke(request)

        try:
            return self.date_parser.parse(result.content)
        except Exception:
            print(f"[Warning] Could not parse AI answer: {result.content}")
            return None

    def get_user_answer(self, question):
        print("\n" + question)

        while True:
            try:
                year = int(input("Year  (e.g., 1945): "))
                month = int(input("Month (1-12): "))
                day = int(input("Day   (1-31): "))
                return datetime(year, month, day)
            except ValueError:
                print("Invalid input. Try again.")

    def check_user_answer(self, user_answer, ai_answer):
        if ai_answer is None:
            return 0, None

        diff_days = abs((user_answer - ai_answer).days)

        if diff_days == 0:
            return 10, 0
        elif diff_days <= 30:
            return 7, diff_days
        elif diff_days <= 365:
            return 5, diff_days
        elif diff_days <= 365 * 5:
            return 3, diff_days
        elif diff_days <= 365 * 20:
            return 1, diff_days
        else:
            return 0, diff_days


# ===================================================================
# Main Quiz Runner
# ===================================================================
def run_quiz():
    print("=" * 60)
    print("HISTORY QUIZ MASTER — OpenAI + LangChain")
    print("=" * 60)

    input("\nPress Enter to start...")

    quiz = HistoryQuiz(chat_model)
    topics = random.sample(HISTORY_TOPICS, 10)

    total_score = 0

    for i, topic in enumerate(topics, 1):
        print(f"\nQuestion {i} — Topic: {topic}")

        try:
            question = quiz.create_history_question(topic)
            ai_answer = quiz.get_AI_answer(question)
            user_answer = quiz.get_user_answer(question)

            points, diff = quiz.check_user_answer(user_answer, ai_answer)

            if ai_answer:
                print("\nCorrect Answer:", ai_answer.strftime("%B %d, %Y"))
                print("Your Answer   :", user_answer.strftime("%B %d, %Y"))
                print("Difference    :", diff, "days")
                print("Points        :", points)
            else:
                print("Could not evaluate this question.")

            total_score += points

        except Exception as e:
            print("Error:", e)

    print("\n" + "=" * 60)
    print("FINAL SCORE:", total_score, "/ 100")
    print("=" * 60)


# ===================================================================
# Entry Point
# ===================================================================
if __name__ == "__main__":
    run_quiz()