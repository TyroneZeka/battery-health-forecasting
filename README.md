# Battery Health Forecasting Project

## Overview
This project aims to predict the **Remaining Useful Life (RUL)** of lithium-ion batteries—how many charge cycles remain before failure—using time-series data from two datasets: NASA's Li-ion Battery Aging Dataset and the Oxford Battery Degradation Dataset. We’ll leverage advanced models like BiLSTM or survival analysis to forecast RUL with uncertainty intervals, and visualize results in an interactive dashboard.

The goal is to bridge controlled lab data (NASA) with real-world EV-like conditions (Oxford), delivering insights into battery degradation trends and predictive performance.

## Objectives
- Predict RUL (cycles until capacity < 80% of initial) for batteries in both datasets.
- Model degradation trends using time-series techniques (e.g., BiLSTM, survival analysis).
- Build a dashboard displaying RUL predictions, capacity fade, and uncertainty intervals.
- Compare model performance across lab-controlled and dynamic conditions.

## Datasets
1. **NASA Li-ion Battery Aging Dataset**
   - Source: [NASA Prognostics Center of Excellence](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/)
   - Description: 18650 cells cycled under controlled charge/discharge conditions (e.g., 1C charge, 2C discharge) at varying temperatures.
   - Features: Voltage, current, temperature, capacity over ~100-200 cycles per battery.

2. **Oxford Battery Degradation Dataset**
   - Source: [Oxford Battery Intelligence Lab](https://howey.eng.ox.ac.uk/data/)
   - Description: Commercial 18650 cells cycled with dynamic EV-like discharge profiles.
   - Features: Voltage, temperature, capacity, impedance over varying cycle counts.

## Tools & Methods
- **Modeling**: BiLSTM for temporal patterns, survival analysis for time-to-failure, or Prophet for baselines.
- **Tech Stack**: Python (Pandas, NumPy, Scikit-learn, TensorFlow/Keras), Dash or Streamlit for dashboarding.
- **Uncertainty**: Confidence intervals via Bayesian methods or ensemble predictions.

## Project Structure
battery-health-forecasting/
├── data/
│   ├── nasa/              # NASA dataset files
│   └── oxford/            # Oxford dataset files
├── src/
│   ├── preprocess.py      # Data cleaning and feature extraction
│   ├── model.py           # Model training and prediction
│   └── dashboard.py       # Dashboard code
├── notebooks/             # Exploratory analysis (Jupyter)
├── results/               # Model outputs, plots
└── README.md              # This file

## Setup
1. Clone this repo: `git clone https://github.com/TyroneZeka/battery-health-forecasting.git`
2. Install dependencies: `pip install -r requirements.txt` 
3. Download datasets:
   - NASA: From the Prognostics Center link above.
   - Oxford: From the Oxford Lab link above.
4. Run preprocessing: `python src/preprocess.py`

## Progress
- [x] Define project scope and datasets.
- [ ] Preprocess NASA and Oxford data.
- [ ] Build and train RUL prediction model.
- [ ] Develop dashboard with RUL and uncertainty visuals.
- [ ] Evaluate and compare across datasets.

## Contributors
- [Tyrone Zeka] - MSc Computer Science student exploring time-series forecasting in battery health.

## License
MIT License - feel free to use or adapt this project!