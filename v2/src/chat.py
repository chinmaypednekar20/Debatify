from src.retriever import retrieve
from src.llm import generate_answer

def chat():

    print("🏛 Parliament Debate Chat Ready\n")

    while True:
        question = input("Ask: ")

        results = retrieve(question)

        context = ""

        for r in results:
            context += f"""
Asked By: {r['summary']['asked_by']}
Ministry: {r['summary']['ministry']}
Category: {r['summary']['category']}

Question Summary:
{r['summary']['question_summary']}

Answer Summary:
{r['summary']['answer_summary']}

---
"""

        answer = generate_answer(question, context)

        print("\n🧠 Answer:\n")
        print(answer)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    chat()