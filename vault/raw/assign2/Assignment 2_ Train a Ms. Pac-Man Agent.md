# Class 3 Assignment: Train a Ms. Pac-Man Agent

## Choose three hyperparameters, train the agent, and explain what it actually learned.

# Overview

Use the ready-made notebook to train a Deep Q-Network (DQN) on Ms. Pac-Man. Choose exploration, episodes, and learning rate. Submit one public GitHub repository URL with the notebook and your evidence in its README.

# What You Are Submitting

* Your executed notebook saved after your final training and evaluation run, with your three hyperparameters and all cell outputs visible. Submit this final-run version, not the unexecuted starter notebook or a copy saved before training.  
* An untrained gameplay GIF and the best trained gameplay GIF.  
* Intermediate gameplay GIFs and checkpoints if your run reaches 25 episodes or more.  
* A training plot and all five before/after evaluation scores.  
* A short explanation of the agent's observations, actions, rewards, and one limitation.

# Open the Notebook

* [Pac-Man project on GitHub](https://github.com/pepealonso95/pacman-dqn)  
* Local Jupyter or VS Code: open the notebook and select a Python 3.11–3.13 kernel.  
* [Open pacman\_dqn.ipynb in Google Colab. Select a GPU under Runtime → Change runtime type if available.](https://colab.research.google.com/github/pepealonso95/pacman-dqn/blob/main/pacman_dqn.ipynb)  
* The notebook installs its packages and checks the available GPU or CPU automatically.

# Your Three Hyperparameters

* Exploration: a number from 0 to 1\. For example, 0.20 makes about 20% of training moves random after warm-up.  
* Episodes: a positive whole number of training games. Try 5 to check setup; 100 is the notebook's starting value.  
* Learning rate: the size of each update. Start with 0.0001 if you need a reference point.  
* Edit only those three values in section 1\. Explain why you chose them before you run training.  
* Exploration stays constant after 1,000 random warm-up decisions. An episode ends at game over or the notebook's fixed time limit.  
* You can tune the other hyperparameters, but explain what you did and why.

# Evaluate the Behavior Fairly

* Keep the notebook's evaluation settings unchanged: the same five seeds, 5% exploration, and time limit before and after training.  
* Report every evaluation score and both means. The baseline is an untrained network, not a random-action agent.  
* Watch the GIFs as well as the scores. The best GIF is selected from five games and shows at most their first 20 seconds.  
* Lower training loss does not guarantee better play. Report failed runs or a lack of improvement honestly.

# Save Your Results

Every run saves a new folder under pacman\_runs/ and creates a ZIP. In Colab, download it before ending the session. Keep the full ZIP locally and copy the evidence you want to publish into a results/ folder.

* The folder contains settings, hardware/package versions, training.csv, training\_summary.json, comparison.json, the training plot, GIFs, and playback checkpoints.  
* If you stop early, interrupt training once, then run the evaluation and download cells. Record the completed episodes and actual learning updates.

# README Requirements

The README is the grading entry point. A grader should be able to understand and reproduce your experiment from your public repository.

* A brief overview and instructions to open and run the notebook.  
* Your exploration, episode budget, and learning rate, with a short reason for each choice.  
* What you expected before training, followed by what you observed.  
* Actual completed episodes, decisions, learning updates, elapsed time, and hardware used.  
* A plain-language explanation: four game screens are the observations; joystick moves are the actions; game points supply the reward.  
* One observed limitation and one next experiment. Explain which single setting you would change and why.

# Suggested Workflow

1. Download the notebook and make your own copy.  
2. Choose your three settings. A five-episode run is a setup check, not a promise of useful play.  
3. Select Run All. Let setup, baseline evaluation, training, and final evaluation finish.  
4. Inspect the plot and gameplay, and compare all five before/after scores.  
5. Download your results, write the README, and publish your notebook and evidence on GitHub.

# Starter Prompt for Your AI Assistant

Help me run pacman\_dqn.ipynb for Class 3\. Before training, ask me which exploration rate, number of episodes, and learning rate I want to use. Explain the choices briefly and wait for my answer. Edit only those three settings, then run the notebook in order. Keep the evaluation settings unchanged, help me save the results, and help me explain what happened using the actual outputs.

# Evidence Required in the README

* Embed the untrained GIF, best trained GIF, and any intermediate GIFs produced by your run.  
* Embed training\_dashboard.png so the score, loss, and exploration curves are visible.  
* Include a table with all five baseline scores, all five trained scores, and their means. Link comparison.json.  
* Link your notebook, config.json, training.csv, and training\_summary.json. Identify an interrupted run or a run with no learning updates.

# Submission Checklist

1. After your final run, save the notebook with its outputs, then upload or push that .ipynb file, your README, and selected results to your public GitHub repository. In Colab, download the executed .ipynb after the run. Do not clear the outputs before saving. Open the notebook on GitHub and confirm that the final scores, plots, and gameplay outputs are visible so the instructor can inspect your results without rerunning it.  
2. Open the repository in a private browser window and verify that the notebook, images, GIFs, and evidence links are accessible.  
3. Keep large model checkpoints in your local results ZIP or a GitHub release; explain where they are saved.  
4. [Submit your GitHub repository](https://submissions-portal-eight.vercel.app)

# Rubric and Class Leaderboard

Gameplay performance will be part of the assignment rubric and score. We will have a class leaderboard comparing students' agents using the mean score across the notebook's five trained evaluation games, with the same evaluation settings for everyone. Report all five scores and link comparison.json in your README. Grading will also consider your explanation of the learning process, hyperparameter choices, and the quality and completeness of your evidence. The leaderboard's grading weight will be announced in class.

# Definition of Done

* The notebook runs with your chosen hyperparameters, and your README records the actual training budget.  
* The untrained and trained agents are evaluated under the same settings, with all five scores shown.  
* Your plot, gameplay, and explanation agree with the recorded results.  
* You can explain what the agent observes, what it can do, how it is rewarded, and one limitation.

# Single Deliverable

* One public GitHub repository URL, submitted through the course submission portal. Its README contains the evidence and explanation listed above.

# Scope

* Use the supplied DQN. Building an agent from scratch is optional.  
* No website, backend, or deployment is required for this assignment.  
* Your agent's evaluation score contributes to grading through the class leaderboard. Report results honestly, including runs that do not improve.  
* A proposed next experiment is enough; a second training run is optional.

