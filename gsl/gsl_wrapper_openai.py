from chat_openai import chat

gls_spec=open("GSL.md", "r").read()
gls_compile=open("gsl_compile.txt", "r").read()


def gsl_generate(game_idea):\
    
    
    output_text,_=chat(
        game_idea,
        system_prompt=gls_spec,
    )

    return output_text


import re
import os

def generate_random_64bit_string():
    return os.urandom(8).hex()

def gsl_compile(gsl_game_idea):
    
    output_text,_=chat(
        gsl_game_idea,
        system_prompt=gls_spec+gls_compile,
    )

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


