"""
ui/widgets/animal.py — ASCII art animal widget for the dashboard.

Currently features Oreo the cat. Add more ASCII art strings to ANIMALS
and they'll be picked at random on each render.
"""

from textual.widget import Widget
from textual.app import RenderResult
from rich.text import Text
import random
from datetime import datetime

OREO = r"""                     K_
                   X.XKK.__
                    |  X\_\._X
                    ||   'b..\ ___                     K,.--'X,
                    '|    ' P.|Poo8b=o...     __,...',,-    ,'
                     \.   .,`/8::==P"''''-.KK X_,.'K,'    ,,'/
                     ._           ┘           ''X. |     ,/',
                      \\.                        \.'     /''
                      '\]        ┌┐         ┌┐    ..    ,|'
                      /8\        └┘         └┘    |`_ X/'
                      |8]\    ,.               _   X`\''
                      `Y`'     ''-    \--/   ._'   X¥/
                      p_''    ','      \/    |..    .
                     ,ppp'║    '    __/-\__    '  ,/'
                   ,≈pp≈p\.═╗                    ,.─
                  ,.    \.'\.,_.                ,.
                p,/'     '\.\'\Y]`.._       ,__/'K
              ,K,'         `.`\.]▒b'\bo..,.-_Y'Y'K
             ,.,'             -'\o._'\,:=8YP'\' |K
           ,-',/                 '`-:::,-''''   |K
         ,/'K,+'                                ||\
       ┬,'KK.'|                                 |'|.
     ┌┬/'KK. '                                  |K|K."""

# All animals default to Oreo until others are drawn
ANIMALS = [OREO]

def pick_animal():
    """Return a random ASCII art string from the ANIMALS list."""
    return random.choice(ANIMALS)

class AnimalWidget(Widget):
    """Displays a randomly selected ASCII art animal."""

    def render(self) -> RenderResult:
        return Text(pick_animal(), style="#dddddd")
