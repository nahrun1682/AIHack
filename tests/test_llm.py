import pytest
from core.llm import stream_ally_message

# Mocking OpenAI response might be needed if we don't want to hit real API, 
# but for reproduction of "silence" which might be due to API error or model name,
# hitting the real API (if keys allow) or mocking the client is better.
# However, the user said "gpt-5". 

@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo", "gpt-4o", "gpt-5"])
def test_stream_ally_message_generates_content(model_name):
    """
    Test that stream_ally_message generates content for various models.
    This assumes a valid OPENAI_API_KEY is set in the environment.
    """
    player_system_prompt = "Say 'Hello'"
    conversation_history = []
    
    chunks = []
    try:
        stream = stream_ally_message(
            player_model=model_name,
            player_system_prompt=player_system_prompt,
            conversation_history=conversation_history
        )
        for chunk in stream:
            chunks.append(chunk)
    except Exception as e:
        pytest.fail(f"Stream failed for {model_name}: {e}")
    
    full_response = "".join(chunks)
    assert len(full_response) > 0, f"Model {model_name} returned empty response"
