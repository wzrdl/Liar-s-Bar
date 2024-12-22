# Liar's Bar Game: A Game Theory Analysis

This repository contains the implementation and analysis of the **Liar's Bar Game**, a two-player strategic card game developed as a case study for exploring game theory concepts, including Nash Equilibrium, Bayesian belief updates, and backward induction.

## Overview

The **Liar's Bar Game** blends elements of bluffing, probabilistic reasoning, and sequential decision-making to offer a rich framework for analyzing strategic interactions under conditions of uncertainty.

### Key Features
- **Game-Theoretic Foundations**: Analysis of payoff matrices, utility functions, and equilibrium strategies.
- **Bayesian Belief Updates**: Dynamic adjustment of strategies based on probabilistic reasoning.
- **Backward Induction**: Optimal decision-making in sequential games.
- **Experimental Validation**: Simulation results to compare Bayesian strategies and non-Bayesian methods.

---

## Game Rules

- The game uses a simplified deck of 20 cards: 2 Jokers (wild cards), 6 Queens, 6 Kings, and 6 Aces.
- Each player is dealt 5 cards, and the game progresses through rounds where players:
  1. Play a truthful set of cards.
  2. Bluff by playing mismatched cards.
  3. Call a bluff to challenge the opponent's play.
- The game ends when one player either successfully plays all their cards or fails a challenge.

For detailed rules and examples, refer to the paper.

---

## Game-Theoretic Analysis

### Payoff Matrix
The game's strategic outcomes are modeled using a payoff matrix that includes truthful plays, bluffs, and bluff calls. 

### Bayesian Belief Updates
Players utilize Bayesian inference to estimate probabilities and refine their strategies dynamically based on observed actions.

### Sequential Decision-Making
Backward induction is employed to determine optimal strategies at each stage of the game, ensuring long-term utility maximization.

---

## Experimental Results

Simulations demonstrate the effectiveness of:
1. Bayesian belief updates in adapting to the opponent's strategies.
2. Sequential decision-making for minimizing the opponent's chances of winning.

### Key Findings
- Bayesian strategies showed a 2% higher win rate compared to standard backward induction.
- Games with frequent bluffing exhibited longer durations due to recalibrations of Bayesian beliefs.

---

## Limitations

While the analysis provides valuable insights, it assumes:
1. Fixed opponent types during gameplay.
2. Complete knowledge of the action space and payoff structure.
3. Simplified experimental setups that may not capture real-world complexities.

---

## Future Work

Potential extensions include:
- Incorporating multiplayer dynamics.
- Exploring more complex utility functions.
- Adjusting game rules to mimic real-world scenarios.

