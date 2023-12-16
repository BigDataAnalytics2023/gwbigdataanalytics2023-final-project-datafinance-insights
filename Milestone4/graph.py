from flask import Flask, request
import os
from flask_cors import CORS
from google.cloud import bigquery
from google.oauth2 import service_account
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import requests
from bs4 import BeautifulSoup
import json
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta
import datetime

cwd = os.getcwd()

credentials = service_account.Credentials.from_service_account_file(
cwd+'\datafinance\src\data-finance-final-92d8049c252f.json')

project_id = 'data-finance-final'
client = bigquery.Client(credentials= credentials,project=project_id)

app = Flask(__name__)
CORS(app)

@app.route('/predict/<stock>', methods=['GET'])
def predict(stock): 
    sql = "SELECT * FROM `data-finance-final.stockMetaData.stock_prices_cleaned`"

    # Re-run the query
    query_job = client.query(sql)
    results = query_job.result()

    # Convert results to a list
    results_list = list(results)

    # Convert the list of tuples to a list of lists
    data_list = [list(row) for row in results_list]

    # Convert the list of lists to a DataFrame with column names
    column_names = ['date', 'open', 'high', 'low', 'close', 'volume', 'stock']
    df = pd.DataFrame(data_list, columns=column_names)

    #specify which stock you want
    #stock = 'AAPL'
    df = df[df['stock'] == stock]
    df = df.sort_values(by='date')

    pred_range = 100
    p = 1
    d = 0
    q = 0
    #Loads the model 
    model = ARIMA(df['close'], order=(p,d,q))
    model_fit = model.fit()

    #Test####
    #print(model_fit.summary())
    
    #Time range 
    current_date = datetime.date.today() #- timedelta(days=1)
    # Format dates as strings in "YYYY-MM-DD" format
    start_index = current_date

    ##Test####
    #print(current_date)
    #print(start_index)
    forecast_index = pd.date_range(start=start_index, periods=pred_range, freq='D')
    # forecast_index = forecast_index.strftime("%Y-%m-%d")
    # df['date'] = pd.to_datetime(df['date'])
    #Forecasting 
    forecast = model_fit.get_forecast(steps = pred_range)
    forecast_df = forecast.summary_frame()

    #Test pritn###
    #print(forecast_df.head())
    
    forecast_df['index'] = forecast_index


    #Print forecast head
    #print(forecast_df.head())
    #print(df.tail())

    
    #### You can mess with the formatting but do not change the names of the DFs. 
    plt.figure(figsize=(15/2, 7/2))  # Modify this as needed for your data
    
    #May need to change 'index' to 'date' for df. NOT FORECAST
    # This takes the last 365 days from the price chart to reduce plot size 
    plt.plot(df['date'].iloc[-365:], df['close'].iloc[-365:], label='Closing Price', color='blue')
    plt.plot(forecast_df['index'], forecast_df['mean'], label='Predicted Price', color='red', linestyle='dashed')
    plt.fill_between(forecast_df['index'], forecast_df['mean_ci_lower'], forecast_df['mean_ci_upper'], color='lightgray', label='95% Prediction Interval')
    # Format the date axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    
    # Rotate date labels
    plt.xticks(rotation=45)
    
    plt.title(f'ARIMA Prediction for \'{stock}\' Over {pred_range} days')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    
    plt.tight_layout()  # Adjust layout to fit the date labels
    plt.legend()
    plt.grid(True)
     
    # Save the plot to a PNG file
    plt.savefig('.\datafinance\src\predicted_graph.png')

    # Optionally, you can return a confirmation message or status
    return os.getcwd()+"\predicted_graph.png"

@app.route('/generate_graph/<stock>', methods=['GET'])
def generate_graph(stock):
    # get data
    sql = "SELECT * FROM `data-finance-final.stockMetaData.stock_prices_cleaned`"

    # Re-run the query
    query_job = client.query(sql)
    results = query_job.result()

    # Convert results to a list
    results_list = list(results)

    # Convert the list of tuples to a list of lists
    data_list = [list(row) for row in results_list]

    # Convert the list of lists to a DataFrame with column names
    column_names = ['date', 'open', 'high', 'low', 'close', 'volume', 'stock']
    df = pd.DataFrame(data_list, columns=column_names)

    #specify which stock you want
    #stock = 'AAPL'
    df = df[df['stock'] == stock]
    print('dataframe')
    print(df)
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    # Check for and handle any possible duplicates in the 'date' column
    df = df.drop_duplicates(subset='date')

    # Sort the DataFrame by 'date'
    df = df.sort_values(by='date')    

    #add predictions
    pdf = pd.DataFrame(columns = ['date', 'stock', 'close', 'open', 'high', 'low', 'volume'])
    today = datetime.date.today()
    for i in range(100):
        price = 200+i
        d = today + datetime.timedelta(days=i-1)
        row = {'date':d, 'close':price, 'stock':stock, 'open':200, 'high':200, 'low':200, 'volume':40000000}
        pdf.loc[len(pdf)] = row
            

    # Plotting
    plt.figure(figsize=(15/2, 7/2))  # Modify this as needed for your data
    plt.plot(df['date'], df['close'], label='Closing Price', color='blue')
    plt.plot(pdf['date'], pdf['close'], label='Predicted Price', color='red', linestyle='dashed')
    # Format the date axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

    # Rotate date labels
    plt.xticks(rotation=45)

    plt.title(f'Closing Price of Stock \'{stock}\' Over Time')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')

    plt.tight_layout()  # Adjust layout to fit the date labels
    plt.legend()
    plt.grid(True)

    # Generate a plot based on received data
    
    
    
    # Save the plot to a PNG file
    plt.savefig('.\datafinance\src\generated_graph.png')

    # Optionally, you can return a confirmation message or status
    return os.getcwd()+"\generated_graph.png"

#get moving averages
@app.route('/tech/<stock>', methods=['GET'])
def tech(stock):
    body = requests.get('https://stockanalysis.com/stocks/'+stock.lower()+'/statistics/')
    soup = BeautifulSoup(body.text, 'html.parser')
    all_data = soup.find_all('td')
    ret = {}
    for i in range(len(all_data)):
        if '52-Week Price Change' in all_data[i].get_text():
            ret['52 Week Price Change'] = all_data[i+1].contents[0]
        if '200-Day Moving Average' in all_data[i].get_text():
            ret['200 Day Moving Average'] = all_data[i+1].contents[0]
        if 'Relative Strength Index (RSI)' in all_data[i].get_text():
            ret['Relative Strength Index'] = all_data[i+1].contents[0]
        if 'Average Volume (30 Days)' in all_data[i].get_text():
            ret['30 Day Average Volume'] = all_data[i+1].contents[0]
        if 'Beta (1Y)' in all_data[i].get_text():
            ret['Beta (1Y)'] = all_data[i+1].contents[0]
        if 'Market Cap' in all_data[i].get_text():
            ret['Market Cap'] = all_data[i+1].contents[0]
        if 'Dividend Yield' in all_data[i].get_text():
            ret['Dividend Yield'] = all_data[i+1].contents[0]
        if 'PE Ratio' in all_data[i].get_text():
            ret['PE Ratio'] = all_data[i+1].contents[0]

        json_object = json.dumps(ret)
        
        with open("./datafinance/src/tech.json", "w") as outfile:
            outfile.write(json_object)
    return ret

#sentiment
@app.route('/sen/<stock>', methods=['GET'])
def sen(stock):
    sql = "SELECT * FROM `data-finance-final.stockMetaData.stock_sentiments_cleaned`"
    # Re-run the query
    query_job = client.query(sql)
    results = query_job.result()

    # Convert results to a list
    results_list = list(results)

    # Convert the list of tuples to a list of lists
    data_list = [list(row) for row in results_list]

    # Convert the list of lists to a DataFrame with column names
    column_names = ['date', 'stock', 'sentiment']
    df = pd.DataFrame(data_list, columns=column_names)

    #specify which stock you want
    #stock = 'AAPL'
    #df = df[df['stock'] == 'AAPL']
    df['date'] = pd.to_datetime(df['date'])

    # Sort the DataFrame by 'date'
    df = df.sort_values(by='date')
    print(df)
    sen_val = df[df['stock']==stock]['sentiment'][0]
    
    print(str(sen_val))
    
    return str(sen_val)
    
    


if __name__ == '__main__':
    app.run(debug=True)

