import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)

gls_spec=open("GSL.md", "r").read()
gls_compile=open("gsl_compile.txt", "r").read()


def gsl_generate(game_idea):
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=8192,
        temperature=0,
        system=gls_spec,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": game_idea
                    }
                ]
            }
        ]
    )
    #print(message.content)

    output_text=message.content[0].text

    return output_text


import re
import os

def generate_random_64bit_string():
    return os.urandom(8).hex()

def gsl_compile(gsl_game_idea):

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=8192,
        temperature=0,
        system=gls_spec+gls_compile,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": gsl_game_idea
                    }
                ]
            }
        ]
    )
    #print(message.content)

    output_text=message.content[0].text

    #find everything between ```html line and ``` and return it
    try:
        html= re.search(r'```html(.*?)```', output_text, re.DOTALL).group(1)
    except:
        return output_text
    
    
    return html

def save(html):
    
    #get a unique filename in /static/games/
    os.makedirs("static/games", exist_ok=True)
    unique_prefix="game"+generate_random_64bit_string()
    filename=f"static/games/{unique_prefix}.html"
    
    with open(filename, "w") as f:
        f.write(html)
    
    #add a / to the filename
    filename="/"+filename
        
    return filename


import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate a game from a game idea')
    
    parser.add_argument('--game_idea', type=str, help='The game idea', default="make a game where you click on squirrels to make them jump. the player should get 1 'squirrel badge' when they win.")
    
    args = parser.parse_args()
    
    game_idea=args.game_idea
    gsl_game_idea=gsl_generate(game_idea)
    print(gsl_game_idea)
    html=gsl_compile(gsl_game_idea)
    print(html)
    filename=save(html)
    print(filename)


