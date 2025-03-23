# Tic-Tac-Toe AI 

## Overview
This is a variation of Tic-Tac-Toe where the board has a flexible rectangular shape, with both width and height ranging between **4 and 10**. Unlike the traditional game, the game does not end when a player forms a line. Instead, the winner is the player who forms the most **square-shaped patterns** by the time the board is full.

## Installation & Running
To run the game, first ensure that you have the required dependencies installed. You can install them using:
   ```bash
   pip install pygame
   ```

## Game Modes
The game supports multiple play modes. Two human players can compete against each other, or a human player can challenge an AI opponent. Additionally, the game includes an AI vs AI mode, where different AI algorithms play against each other.

## AI & Strategy
The AI makes decisions using the **Minimax** algorithm with optional **Alpha-Beta Pruning** for optimization. The evaluation function is based on the number of completed square patterns on the board. Players can select different AI difficulty levels to adjust the challenge.

## Demo
