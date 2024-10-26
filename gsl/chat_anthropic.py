import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)



def chat(
    input_text,
    system_prompt="do your best",
    history=None,
    json_mode=False,
    max_history=8,
    verbose=False,
):
    
    
    if history is None:
        history=[]
    
    #trim history
    if len(history)>max_history:
        history=history[-max_history:]
    
    messages=history+[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": input_text
                }
            ]
        }
    ]
    
    if json_mode:
        #prefill with {
        messages+=[
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "{"
                    }
                ]
            }
        ]
    
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=8192,
        temperature=0,
        system=system_prompt,
        messages=messages,
    )
    #print(message.content)

    output_text=message.content[0].text
    
    new_history=history+[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": input_text
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": output_text
                }
            ]
        }
    ]

    return output_text, new_history
