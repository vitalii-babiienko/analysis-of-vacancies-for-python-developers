# Analysis of Vacancies for Python Developers

The project for web scraping and analysis vacancies for Python Developers.

## Installation

**Python3 must already be installed!**

```shell
git clone https://github.com/vitalii-babiienko/analysis-of-vacancies-for-python-developers.git
cd analysis-of-vacancies-for-python-developers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Scrapy

```shell
scrapy crawl vacancies -O vacancies.csv
```

## Run Analysis

Open `vacancies.ipynb` and run all cells `Ctrl+Alt+Shift+Enter`
