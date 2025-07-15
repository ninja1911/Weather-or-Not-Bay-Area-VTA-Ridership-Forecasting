# Weather or Not: Bay Area VTA Ridership Forecasting 🚆☀️🌧️

## Overview

**Weather or Not** is a machine learning project that predicts daily ridership on Valley Transportation Authority (VTA) stops in the Bay Area by integrating transit data with local weather conditions. By leveraging various regression models and ensemble techniques, this repository provides a robust pipeline—from data collection and preprocessing to model training, evaluation, and inference.

## Table of Contents

* [Repository Structure](#repository-structure)
* [Getting Started](#getting-started)

  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Workflow](#workflow)

  1. [Data Preprocessing](#1-data-preprocessing)
  2. [Data Modeling](#2-data-modeling)
  3. [Final Model](#3-final-model)
  4. [Inference](#4-inference)
* [Results & Evaluation](#results--evaluation)
* [Usage Examples](#usage-examples)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

## Repository Structure

```
├── data_preprocessing/              # Jupyter notebooks for preprocessing steps
├── data_preprocessing_py_files/     # Python scripts mirroring notebooks
├── data_modeling/                   # Jupyter notebooks for model training & evaluation
├── data_modeling_py_files/          # Python scripts for modeling
├── final_model/                     # Trained model artifacts (plots, pickle file)
├── inference/                       # Notebooks for running inference on new data
├── inference_py_files/              # Python scripts for inference
├── ridership.csv                    # Raw VTA ridership dataset
├── requirements.txt                 # Project dependencies
└── README.md                        # Project overview and instructions
```

## Getting Started

### Prerequisites

* Python 3.8+
* `pip` package manager

### Installation

```bash
# Clone the repo
git clone https://github.com/<your_username>/vta-ridership-forecasting.git
cd vta-ridership-forecasting

# Create & activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Workflow

### 1. Data Preprocessing

* `clean_ridership.py` / `clean_ridership.ipynb`: Clean & aggregate VTA ridership data
* `generate_dates.py` / `generate_dates.ipynb`: Create continuous date features
* `merge_stops.py` / `merge_stops.ipynb`: Join ridership with stop metadata
* `merge_climate.py` / `merge_climate.ipynb`: Integrate nearby NOAA weather data

### 2. Data Modeling

* `linear_regression.py` / `linear_regression.ipynb`: Baseline linear & ElasticNet models
* `decision_tree.py` / `decision_tree.ipynb`: Decision Tree regression
* `random_forest.py` / `random_forest.ipynb`: Random Forest with hyperparameter tuning
* `ridership_gbt.py` / `ridership_gbt.ipynb`: Gradient Boosted Trees
* `xg.py` / `xg.ipynb`: XGBoost regression
* `results.py` / `results.ipynb`: Compare models with & without weather data

### 3. Final Model

* Located in `/final_model/` folder
* Contains:

  * `final_model.pkl`: Serialized Random Forest model (best performer)
  * Diagnostic plots: errors, residuals, feature importance, tree visualization

### 4. Inference

* `inference.py` / `inference.ipynb`: Load `final_model.pkl` & predict on new samples
* `inference_helpers.py`: Utility functions for preprocessing & prediction pipeline

## Results & Evaluation

* Achieved an **R² score of 0.8050** on the test set with the tuned Random Forest model
* Other metrics: MAE = 5.7359, RMSE = 21.7712, Explained Variance Score = 0.8051
* See `final_model/` for detailed diagnostic plots

```
