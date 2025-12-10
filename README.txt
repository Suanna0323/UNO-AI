# UNO AI Project
- UNO game in python implemented with minimax  Alpha-Beta pruning AI 

## Files
1. main_game.py - main file for UNO logic, including Graphical User Interface using tkinter library
2. AI_uno.py - AI logic file
3. README - read me! You're currently reading this file


## Compile
- use python main_game.py or any compiler you desire, make sure all files are inside same directory.
- make sure when dealing a card, the card is overlapping with card in the center(discard pile).
- be aware python is rendering frames by frames, so our dealing/drawing card animation could be lagging due to equipment environments.
- change parameter "difficulty" in main_game.py line 497 for difficulty, default is "medium"


## Dependencies
- Python 3.10+
- tkinter(built-in, include in Python standard libraries)
- random(built-in, include in Python standard libraries)

## MIT License

Copyright(c) 2025 Suanna Shih, Avyakt Rout, Miguel Romero Mojica

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.