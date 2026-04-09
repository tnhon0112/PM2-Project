# PM2-Project – Horse Game with Camera Control

This project is a simple horse runner game controlled by a **camera** using OpenCV. It aims to provide a more interactive experience where the player can control the character with body movements instead of only using the keyboard.

## Demo

_(Add screenshots or GIFs here if you have them, for example from an `Assets/` folder.)_

## Features

- Control the horse character using a webcam and OpenCV.
- Optionally support keyboard control (if implemented in your code).
- Simple and lightweight UI suitable for learning and experimentation.
- Pure Python code that is easy to read, modify, and extend.

## Requirements

- Python 3.x
- Python libraries:
  - `opencv-python`
  - (Add any other libraries you use, such as `numpy`, `pygame`, etc.)
- A working webcam on your computer.

Install dependencies (example):

```bash
pip install opencv-python
# Add other required libraries here
```

## Installation and Usage

1. Clone this repository:

```bash
git clone https://github.com/tnhon0112/PM2-Project.git
cd PM2-Project
```

2. Install the required libraries:

```bash
pip install -r requirements.txt
```

_(If you do not have a `requirements.txt` yet, you can create one or list the libraries in this README.)_

3. Run the game (camera version):

```bash
python3 game.py
```

4. (Optional) If you have another mode (for example, keyboard-only), add instructions such as:

```bash
python3 <another_file>.py
```

## Project Structure

Key files and folders (you can adjust this to match your actual structure):

- `game.py`: Main entry point to run the game with OpenCV and the camera.
- `camera_logic.py`: Handles image processing from the webcam and maps movements/gestures to game actions.
- `ui.py`: Manages drawing the player, obstacles, and updating the game screen.
- `Assets/`: Images, sprites, and other resources used by the game.
- `AGENT.MD`: Internal notes or agent description (update this if needed).
- `.pycache/`: Auto-generated Python cache, not important for understanding the project.

## How It Works

- The webcam is opened using OpenCV in `camera_logic.py`.
- Each frame from the camera is processed to detect the user’s movement or gestures.
- These detected gestures are converted to game actions (jump, duck, run, etc.) in `game.py`.
- `ui.py` is responsible for rendering the horse, obstacles, and updating the game every frame.
- The player must avoid obstacles for as long as possible to achieve a higher score.

You should update this section to describe the exact gestures and detection method you implemented.

## How to Play

- Make sure your webcam is connected and working.
- Sit or stand within the camera’s field of view.
- Perform the defined gestures to control the horse (for example: raise hand to jump, lower body to duck — replace with your real mapping).

- Watch the screen and avoid hitting obstacles.





## Author
- Name: Hồ Quang Huy : 11525018
        Trần Thành Nhơn : 11525035
        Nguyễn Thanh Huy Nhật : 11525017
- Instructor: Bien Minh Tri
- University:VGU
