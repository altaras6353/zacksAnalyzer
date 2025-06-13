# zacksAnalyzer

This project provides a minimal GUI tool that attempts to fetch the Top 5 VGM-ranked stocks from **Zacks.com**. The data is shown in a table with a single button click.

## Usage

Run the script with Python:

```bash
python3 main.py
```

Press the **"Fetch Top VGM Stocks"** button to retrieve the latest data. The results display the timestamp of retrieval, company name, ticker, and the Value, Growth, Momentum, and VGM scores.

> **Note**: Network access is required to fetch live data from Zacks.com. If network access or dependencies are unavailable, the program displays an error dialog.
