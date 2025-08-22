import threading

from google import genai

from .secret_manager import retrieve_api_key


def ask_gemini(
    question,
    image=None,
    think=False,
    on_result=None,
    on_error=None,
):
    thread = threading.Thread(
        target=_ask_gemini,
        args=(
            question,
            image,
            think,
            on_result,
            on_error,
        ),
    )
    thread.start()


def _ask_gemini(
    question,
    image=None,
    think=False,
    on_result=None,
    on_error=None,
):
    try:
        api_key = retrieve_api_key()
        client = genai.Client(api_key=api_key)
        think_conf = genai.types.ThinkingConfig(thinking_budget=-1 if think else 0)
        contents = [question]
        if image:
            contents.append(client.files.upload(file=image))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=genai.types.GenerateContentConfig(thinking_config=think_conf),
        )
        if on_result:
            in_tokens = response.usage_metadata.prompt_token_count
            out_tokens = response.usage_metadata.candidates_token_count
            on_result(response.text, in_tokens, out_tokens)
    except Exception as err:
        if on_error:
            on_error(err)
