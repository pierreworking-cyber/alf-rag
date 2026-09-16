import subprocess


MODEL = "gemma4:31b-cloud"


def resolve(question, conversation, document_name):
    if not conversation:
        return question

    history = []

    for exchange in conversation[-5:]:
        history.append(
            f"User: {exchange['question']}\n"
            f"ALF: {exchange['answer']}"
        )

    history_text = "\n\n".join(history)

    prompt = f"""
You are a question-resolution component in a document
question-answering system.

The document currently being discussed is:

{document_name}

Your ONLY job is to turn the user's current question into a
standalone question that can be searched independently.

Use the conversation only to resolve references such as:
- they
- them
- he
- she
- it
- this work
- that event
- there
- previously mentioned names or subjects

When resolving a reference to the current document, include the
document name when it makes the resulting question more explicit.

Do NOT answer the question.

Do NOT add facts that are not present in the conversation.

If the current question is already standalone, return it unchanged.

If the conversation does not provide enough information to resolve
a reference safely, return the current question unchanged.

Return ONLY the standalone question.
Do not add explanations, commentary, quotation marks, or labels.

Conversation:
{history_text}

Current question:
{question}
"""

    result = subprocess.run(
        [
            "ollama",
            "run",
            MODEL,
        ],
        input=prompt,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Ollama failed:\n{result.stderr}"
        )

    output = result.stdout.strip()

    if "...done thinking." in output:
        output = output.split(
            "...done thinking.",
            1,
        )[1].strip()

    return output
