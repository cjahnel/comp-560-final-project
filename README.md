# COMP 560 Final Project
This repository contains our code attempting to beat 2048 with AI by using expectimax on the state tree. Each board is a unique state,
and the player can move to the next state by moving the tiles in one of the four directions.
After a move, there a 2 or a 4 tile gets randomly filled in in an empty space in the grid.

## Visual Simulation
Run main.py for an interactive simulation with Tkinter of our AI running in practice with a custom heuristic.
You can step through each action and set the depth to see the the possible actions ranked by our custom heuristic,
which incentivizes smooth gradients across tiles, a snake pattern of powers of 2 up the board, and maximal empty tiles.
You can also put the moves on AutoPlay with a slider to change the speed (as depth increases, however, the rate will slow beyond the limit).

## Model Evaluation
Check the Jupyter Notebook for our model evaluation with multiple heuristics, including our combined.
There is a seed for reproducibility, so rerunning the code will not change anything.
Running the simulation across depths and heuristics can take several minutes depending on your system.

## Report and Presentation
If you would like to see our writeup of the evaluation, you can take a look at our report.
Our slides are also attached with a timelapse of the AI achieving 2048.

See if you can beat the machine!
