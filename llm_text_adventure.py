# %% [markdown]
# # Curl example
# ```
# curl http://localhost:1234/v1/chat/completions \
#   -H "Content-Type: application/json" \
#   -d '{
#     "model": "meta-llama-3.1-8b-instruct",
#     "messages": [
#       { "role": "system", "content": "Always answer in rhymes. Today is Thursday" },
#       { "role": "user", "content": "What day is it today?" }
#     ],
#     "temperature": 0.7,
#     "max_tokens": -1,
#     "stream": false
# }'
# ```

# %%
import requests
import json
import textwrap
import pandas as pd
from datetime import datetime

max_width = 80

url = "http://localhost:1234/v1/chat/completions"

headers = {
    'Content-Type': 'application/json'
}

# initial state of data
data = {
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [
            { "role": "system", "content": "You will always make a description of a scene or action happening with in it" }
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

# import spreadsheet data
df = pd.read_csv('llm_game_data/llm_game_data/Sheet 1-locations.csv')

# %%
# write function to gather initial user preferences (setting, character types, conflict)
def game_setting():
    setting = input("What type of setting would you like to interact with (desert, rainforest, etc). Be as specific as you'd like.")
    people_animals = input("What type of people/animals would be in this setting? Describe a few different personalities.")
    conflict_goal = input("Is there any kind of conflict or goal you'd like to see in this environment?")

    # append info to data
    setting = { "role": "system", "content": f"The scene looks like {setting}" }
    data['messages'].append(setting)
    people_animals = { "role": "system", "content": f"The people/animals in the setting are {people_animals}" }
    data['messages'].append(people_animals)
    conflict_goal = { "role": "system", "content": f"The user wishes to resolve or achieve {conflict_goal}" }
    data['messages'].append(conflict_goal)

# %%
# Export data
def save_data(x, y, location):
    # TODO: save location to file as well
    data['x'] = x
    data['y'] = y
    data['location'] = location
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"saves/output_{current_datetime}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# %%
def load_data():
    # TODO: add in option to load most recent file
    # read in file and append all but the first system message to the data
    filename = input("Which file do you want to load?")
    # output_2025-01-03_16-34.json (old format, lots of location prompts)
    # output_2025-01-03_16-44.json (no extra location prompts)
    # output_2025-01-04_00-36.json - sky island
    # output_2025-01-04_00-49.json - sky island cont'd
    # output_2025-01-06_17-34.json - sky island cont'd
    try:
        with open(f"saves/{filename}", "r") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON data - {e}")
    # append messages to data object
    saved_messages = json_data['messages'][1:]
    data['messages'] = data['messages'] + saved_messages
    # update location from file
    data['x'] = json_data['x']
    data['y'] = json_data['y']
    data['location'] = json_data['location']

    # print the last message after load
    print(f"\n({data['x']}, {data['y']}): {data['location']}\n")
    wrapped_text = textwrap.wrap(data['messages'][-1]['content'], width=max_width)
    print("\n".join(wrapped_text))

# %%
# create a function that queries API, prints a descripton and then asks for user input
def game_loop(data):
    # gather input
    headers = {
        'Content-Type': 'application/json'
    }

    # prompt user for loading
    load_save = input('Do you wish to load a previous saved game? (y/n): ')
    if load_save.lower() == 'y':
        load_data()
        # load location into x/y/location variables
        x = data['x']
        y = data['y']
        location = data['location']
    else:
        # prompt for initial settings from user
        create_world = input('Do you wish to create a new, specific game world? (y/n): ')
        if create_world.lower() == 'y':
            game_setting()

        # initial location
        x = 0
        y = 0
        location = df[(df['x'] == x) & (df['y'] == y)]['description'].values[0]

    user_prompt = ''
    while user_prompt.lower() != 'exit':
        user_prompt = input("What would you like to do (use n, s, e, w for movement)?\n")

        # TODO: implement turn-based method that ramps up drama the more the user chats


        # grid method of story progression
        # pull location from df
        if user_prompt.lower() in ['n', 's', 'e', 'w']:
            # update x/y values
            if user_prompt.lower() == 'n':
                y+=1
                user_prompt = "I move north"
            elif user_prompt.lower() == 's':
                y-=1
                user_prompt = "I move south"
            elif user_prompt.lower() == 'e':
                x+=1
                user_prompt = "I move east"
            elif user_prompt.lower() == 'w':
                x-=1
                user_prompt = "I move west"
        
        # this handles extra prompt when exit is typed (optimize later)
        if user_prompt.lower() != 'exit':
            # add user's response to data and print out
            data['messages'].append({ "role": "user", "content": user_prompt })
            print(f'\nUser: {user_prompt}\n')

            # add location to system messages only if location hasn't changed from previous loop
            old_location = location
            location = df[(df['x'] == x) & (df['y'] == y)]['description'].values[0]
            if old_location == location:
                data['messages'].append({ "role": "system", "content":f"Present at the current location is {location}" })
            print(f'\n({x}, {y}): {location}')

            

            response = requests.post(url, headers=headers, json=data)

            # print response
            response_json = response.json()
            message = response_json["choices"][0]["message"]["content"]
            wrapped_text = textwrap.wrap(message, width=max_width)
            print("\n".join(wrapped_text))

            # add assistant response to data
            data['messages'].append(response_json["choices"][0]["message"])
        else:
            # save data
            save_data(x, y, location)

# %%
data

# %%
game_loop(data)

# %%



