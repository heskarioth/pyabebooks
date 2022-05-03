# pyabebooks

wrapper for abebooks.com via asyncio for speeding up your book search.

### Installation

#### Dashboard Set up
This project makes use of Google Sheets for the Dashboard front-end and Python for back-end jobs. In order to set up a correct connection between the two,
you need to create a ServiceAccount in Google Developer Console, enable Google Sheets API, share access to Google Sheet File to that ServiceAccount and create API Keys. You can follow [this guide](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html) 
to get you up and running. After downloading the JSON credential file, rename it as <i>sheets_creds.json</i> and place it under the <i>sheets_utils</i> folder. The code is expecting a predefined template to be used as Dashboard, please make sure to copy [this template](https://docs.google.com/spreadsheets/d/1Cds4zfSrhxVSPzneG5EKlQXIj9lL2KfSlxH2d8kNWrc/edit?usp=sharing) 
and rename it <b>Crypto Investment Tracker</b>. Finally, ensure that your Sheet ID has been given to the <i>GOOGLE_SHEET_ID</i> variable in <i>global_vars</i>.

#### Installation
To install the package, go to location where you want to save project and follow the below commands:
```bash
git clone https://github.com/heskarioth/crypto_investment_tracker.git
cd crypto_investment_tracker
python3 setup.py install
```

### Sample Usage

```python

ab = Abebooks()

list_isbns = ['9784900737396','020161622X']

book_results  = ab.getPricingDataByISBN(list_isbns)

```

### Methods Description:

- *getPricingDataByISBN* Blablabla
```python 
    summary_get_overview_tab(kraken_dca_df,binance_dca_df)
```
- *getBookRecommendationByISBN*
```python 
    summary_get_overview_tab(kraken_dca_df,binance_dca_df)
```
- *getPricingDataForAuthorTitleByBinding*
```python 
    summary_get_overview_tab(kraken_dca_df,binance_dca_df)
```
- *getPricingDataForAuthorTitleBDP*
```python 
    summary_get_overview_tab(kraken_dca_df,binance_dca_df)
```
- *getHighlightInventoryForBookSearch*
```python 
    summary_get_overview_tab(kraken_dca_df,binance_dca_df)
```

### Future Development
Currently there are no other major updates in the pipeline for this project as all abebook's available endpoints have been captured.
For enhancements or additional use case recommendations, please reach out. I love extending my previous projects :).

### License
[MIT](https://choosealicense.com/licenses/mit/)
