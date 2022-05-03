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

#### API Exchange keys set up
This project utilises Kraken and Binance. Follow [this link](https://www.binance.com/en/support/faq/360002502072) for instructions on how to create API keys for Binance and [this](https://support.kraken.com/hc/en-us/articles/360000919966-How-to-generate-an-API-key-pair-) 
other one for Kraken. Their corresponding values should be given to the variables below in <i>portfolio_keys</i> module. Don't forget to also amend <i>INVESTED_COINS</i> with the list of coins you're holding.
```bash
KRAKEN_API_KEY = '????????????????????????????????????????????????'
KRAKEN_PRIVATE_KEY = '???????????????????????????????????????????????'

BINANCE_API_KEY = '??????????????????????????????????????'
BINANCE_PRIVATE_KEY = '??????????????????????????????????????'

INVESTED_COINS = ['BTC','ADA','AAVE','HBAR','STX','BNB','MATIC'] # This is the list of coins I have.
```

### Usage

```python

ab = Abebooks()

list_isbns = ['9784900737396','020161622X']

book_results  = ab.getPricingDataByISBN(list_isbns)

```

### Methods Description:

- *Summary*
  - Get me an overview of all my crypto holdings. Include total token quantity, dca, profit_loss, price paid, and current asset value.
    ```python 
    summary_get_overview_tab(kraken_dca_df,binance_dca_df)
    ```
  - Get me all my open orders across all the exchanges.
    ```python 
    summary_get_open_orders([kraken_open_orders,binance_open_orders])
    ```  
  - Get me how much I have deposited in all my accounts.
    ```python
    summary_get_deposits_usd_(kraken_deposit_history,kraken_account_size,binance_deposit_history,binance_account_size)
    ```
  - Get me total available spot balance across all exchanges (in BTC and USDT)
    ```python
    summary_get_spot_balance(kraken_spot_balance,binance_spot_balance)
    ```
  - Get me total savings account balance across all exchanges (in BTC and USDT).
    ```python 
    summary_get_savings_balance(binance_savings_overview,kraken_savings_overview)
    ```
  - Get me total account size across all exchanges (in BTC and USDT).
    ```python 
    summary_get_account_size(binance_account_size,kraken_account_size)
    ```  
  - Give my trade history, suggest me selling prices for the crypto I own.
    ```python
    summary_get_selling_recomendations_overview(df_portfolio_overview)
    ```

### Future Development
Currently there are no other major updates in the pipeline for this project as all abebook's available endpoints have been interfaced.
For enhancements or additional use case recommendations, please reach out. I love extending my previous projects :).

### License
[MIT](https://choosealicense.com/licenses/mit/)
