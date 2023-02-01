import matplotlib.pyplot as plt
import numpy as np
from bot_config import client
import discord

size_map = {
    'a': 1,
    'b': -1,
    'c': 0.5,
    'd': -0.5,
    'e': 2,
    'f': -2,
    'g': 1.5,
    'h': -1.5,
    'i': 3,
    'j': -3,
    'k': 2.5,
    'l': -2.5,
    'm': 4,
    'n': -4,
    'o': 3.5,
    'p': -3.5,
    'q': 5,
    'r': -5,
    's': 4.5,
    't': -4.5,
    'u': 6,
    'v': -6,
    'w': 5.5,
    'x': -5.5,
    'y': 7,
    'z': -7
}

@client.command(aliases=['amplitugrafia',  'amplitude', 'amplitud', 'ampl'])
def amplitugraphy(ctx, **args):
    msg = " ".join(args)
    if len(msg) == 0:
        ctx.channel.send("Nothing to encode.")
        return

    invalid_chars = set()
    x_list = []
    y_list = []
    cumulative_x = 0
    for char in msg.lower():
        if char == ' ':
            cumulative_x += 3
            x_list += [cumulative_x - 3, cumulative_x]
            y_list += [0, 0]
            continue
        elif char in ['.', ',']:
            cumulative_x += 3
            x_list += [cumulative_x - 3, cumulative_x]
            y_list += [(1 if char == '.' else -1)] * 2
            continue
        elif char not in size_map:
            invalid_chars.add(char)
            continue
        x_array = np.arange(-1.5, 1.6, 0.1)
        y_height = size_map[char]
        negative = -(y_height / abs(y_height))
        width = (1.5 ** 2) / abs(y_height)
        y_array = (x_array ** 2) / (negative * width) - negative * abs(y_height)
        x_array += 1.5 + cumulative_x
        cumulative_x += 3

        x_list += list(x_array)
        y_list += list(y_array)

    plt.plot(x_list, y_list)
    plt.axhline(y=0, color='black')
    plt.grid()
    plt.yticks(list(set([int(np.ceil(y)) for y in y_list])))
    plt.xticks(np.arange(0, x_list[-1], 3), labels=[])
    plt.savefig('assets/Ampltugraphy.png', dpi=300)

    if len(invalid_chars) > 0:
        ctx.channel.send(f"Warning! Your message has some invalid characters {invalid_chars}. "
                         f"Those will be omitted in the encoded picture.")
    with open('assets/Ampltugraphy.png', 'rb') as img:
        f = discord.File(img, filename='Ampltugraphy.png')

    ctx.channel.send(file=f)
