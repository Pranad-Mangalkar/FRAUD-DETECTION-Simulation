# FRAUD-DETECTION-Simulation

A real-time machine learning fraud detection simulator built with Python, Scikit-learn, Pandas, and Pygame.

## Overview

This project trains a Decision Tree classifier on a financial transaction dataset and visualizes the fraud detection process through an interactive conveyor-belt simulation.

Transactions move through a virtual pipeline where the machine learning model classifies them as either:

- Safe Transactions
- Fraudulent Transactions

The dashboard displays:

- Safe transactions routed successfully
- Transactions flagged and dropped
- Actual frauds present in the dataset
- Frauds successfully detected
- Frauds missed by the model

## Features

- Decision Tree based fraud detection
- Real-time graphical visualization using Pygame
- Train/Test split (80/20)
- Live fraud detection metrics
- Interactive simulation dashboard

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Pygame

## Dataset

The project uses the PaySim financial transaction dataset:

PS_20174392719_1491204439457_log.csv

The dataset is not included in this repository due to file size limitations.

Place the dataset in the project root directory before running the program.

## Installation

Install dependencies:

```bash
pip install pandas numpy scikit-learn pygame
```

## Run

```bash
python main.py
```

## Project Structure

```
FRAUD-DETECTION-Simulation/
│
├── main.py
├── README.md
├── requirements.txt
└── PS_20174392719_1491204439457_log.csv
```

## Machine Learning Pipeline

1. Load dataset
2. Select transaction features
3. Split data (80% train, 20% test)
4. Train Decision Tree classifier
5. Generate predictions
6. Visualize results using Pygame

## Future Improvements

- Random Forest implementation
- XGBoost support
- Neural Network fraud detection
- Confusion matrix visualization
- ROC-AUC metrics
- Adjustable simulation speed

## Author

Pranad Mangalkar
