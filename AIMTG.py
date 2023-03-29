import json
import openai
import os
from pathlib import Path
from tkinter import Tk, Text, BOTH, Entry, StringVar, BOTTOM, X, Frame, Menu, END, filedialog
from tkinter import Label

API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = API_KEY
AIModel = "gpt-3.5-turbo"
AIMessages = [
    {"role": "system", "content": """You are an AI used to generate Magic: The Gathering card concepts. You will return cards in the following JSON format, with no additional text or explanation: {"name": "Card Name", "manaCost": "{1}{B}{G}", "cmc": 3, "colors": ["Black", "Green"], "types": ["Creature"], "subtypes": ["Zombie", "Plant"], "text": "Some text describing the card's effect.", "power": 2, "toughness": 2, "flavorText": "The zombies rose from the ground, their vines tangling with those of the plants. Together they made an unstoppable force."}"""},
    {"role": "user", "content": "Generate a card based on a valkyrie from Norse mythology."},
    {"role": "assistant", "content": """{"name": "Valkyrie's Charge", "manaCost": "{3}{W}{B}", "cmc": 5, "colors": ["White", "Black"], "types": ["Creature"], "subtypes": ["Valkyrie"], "text": "Flying, lifelink. Whenever Valkyrie's Charge attacks, choose one - \n• Creatures you control gain indestructible until end of turn. \n• Each opponent loses 2 life and you gain 2 life.", "power": 3, "toughness": 3, "flavorText": "In battle, the Valkyries swoop down from the skies to claim the souls of the worthy."}"""}
  ]

def get_card_bg_color(colors):
        COLOR_MAPPING = {"white": "white","blue": "light blue","black": "gray","red": "light coral","green": "pale green"}
        if len(colors) > 1:
            return "gold"
        elif len(colors) < 1:
            return "silver"
        else:
            return COLOR_MAPPING.get(colors[0].lower(), colors)

def load_card_data():
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if not file_path:
        return

    with open(file_path, "r") as file:
        card_data = json.load(file)
    AIMessages.append({"role": "assistant", "content": json.dumps(card_data)})
    display_card(json.dumps(card_data))

def save_card_data(card_data, directory=None):
    if directory:
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{card_data['name']}.json")
    else:
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return

    with open(file_path, "w") as file:
        json.dump(card_data, file)

def display_card(card_json):
    card_data = json.loads(card_json)
    save_card_data(card_data, "MTGCards")
        
    root = Tk()
    root.title("Magic: The Gathering Card")

    card_bg_color = get_card_bg_color(card_data['colors'])
    card_frame = Frame(root, bg=card_bg_color, padx=10, pady=10)
    card_frame.pack()

    name_label = Label(card_frame, text=card_data['name'], font=("Helvetica", 14, "bold"), bg=card_bg_color, anchor="w")
    name_label.pack(fill="both")

    mana_cost_label = Label(card_frame, text=card_data['manaCost'], font=("Helvetica", 12), bg=card_bg_color, anchor="e")
    mana_cost_label.pack(fill="both")

    types = card_data.get('types', [])
    subtypes = card_data.get('subtypes', [])
    types_label_text = " - ".join(types + subtypes) if subtypes else " ".join(types)
    types_label = Label(card_frame, text=types_label_text, font=("Helvetica", 12), bg=card_bg_color, anchor="w")
    types_label.pack(fill="both")

    text_label = Label(card_frame, text=card_data['text'], wraplength=200, font=("Helvetica", 10), bg=card_bg_color, justify="left", pady=5)
    text_label.pack(fill="both")

    flavor_text_label = Label(card_frame, text=card_data['flavorText'], wraplength=200, font=("Helvetica", 10, "italic"), bg=card_bg_color, justify="left", pady=5)
    flavor_text_label.pack(fill="both")

    power_toughness_label = Label(card_frame, text="{} / {}".format(card_data['power'], card_data['toughness']), font=("Helvetica", 12, "bold"), bg=card_bg_color, anchor="e")
    power_toughness_label.pack(fill="both", side="right")

    root.mainloop()

def enter_pressed(event):
    input_get = input_field.get()
    chat_history.insert(END, 'You: %s\n' % input_get)

    AIMessages.append({"role": "user", "content": input_get})

    completion = openai.ChatCompletion.create(
        model=AIModel,
        messages=AIMessages
    )

    response = completion.choices[0].message.content
    AIMessages.append({"role": "assistant", "content": response})
    chat_history.insert(END, 'AI: %s\n' % response)

    user_input.set('')
    display_card(response)
    return "break"

window = Tk()
window.title("Chat Window")

chat_history = Text(window)
chat_history.pack(fill=BOTH, expand=True)

user_input = StringVar()
input_field = Entry(window, text=user_input)
input_field.pack(side=BOTTOM, fill=X)

menu_bar = Menu(window)
window.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Load", command=lambda: load_card_data())
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)

frame = Frame(window)
input_field.bind("<Return>", enter_pressed)
frame.pack()

window.mainloop()