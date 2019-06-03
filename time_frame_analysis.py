# -*- coding: utf-8 -*-
"""
Created on Thu May 30 14:40:47 2019

@author: matth
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os

#filepath used to load the csv price data - NOTE [ASSET] will be replaced
#with the variable asset to load in the data for that particular asset
template_source_filepath = "D:\\ForexData\\BaseData\\[ASSET]_m1.csv"

def load_asset_data(asset):
    """ Loads the asset data from csv 
    
    Args:
        asset (string): name of the asset to subtitute in the filepath
        
    Returns:
        Pandas.DataFrame: the asset data in a dataframe
    
    """
    
    #set the filepath by substitution the asset name
    source_filepath = template_source_filepath.replace("[ASSET]", asset)

    #read the csv file
    df = pd.read_csv(source_filepath, sep=",", index_col=0, parse_dates=True)
    
    return df

def plot_volume_by_minute(asset_data, save_file = None):        
    """ Plots the tick volume grouped by minute of the hour 
    
    Args:
        asset_data (Pandas.DataFrame): the dataframe with the tickqty volume data
        save_file (string): filepath to save the figure to if desired       
    
    
    """
    
    #group tick volume by minute to see which minute of the hours has the highest activity
    whole_set_minute_vol = asset_data.groupby(asset_data.index.minute)['tickqty'].median()
    
    #transform these to relative values to make the graph clearer
    relative_values = (whole_set_minute_vol / whole_set_minute_vol.mean()) * 100 - 100
    
    #plot a bar graph of the EUR USD over the whole period
    plt.figure(figsize=(16.0, 10.0))
    plt.bar(range(60), relative_values)
    plt.title("Relative Trade Volumes by Minute")
    plt.xlabel("Volume at Minute")
    plt.ylabel("% Higher than Average") 
    
    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')
        
    plt.show()
    
    
def plot_volume_by_year(asset_data, start_year=2007, end_year=2018, save_file = None):
    """ Plots the tick volume grouped by minute of the hour separated over 
    different years to look at the consistency of the relationship over time
    
    Args:
        asset_data (Pandas.DataFrame): the dataframe with the tickqty volume data
        start_year (int): filter data to start from this year (inclusive)
        end_year (int): filter data to finish at this year (inclusive)
        save_file (string): filepath to save the figure to if desired       
    
    Returns:
        Pandas.DataFrame: the results on the 0,15,30,45 and 59 min periods for
            each year
    
    """
    
    #restrict to full years from 2006 to 2018
    asset_data = asset_data[(asset_data.index.year >= start_year) & (asset_data.index.year <= end_year)]
    
    #just calculate the % more than mean for 0,15,30,40 and 59 minutes
    cols = ["0 min", "15 min", "30 min", "45 min", "59 min"]
    res_table = pd.DataFrame(columns = cols)
    
    for year in range(start_year, end_year+1):
        
        df_year = asset_data[asset_data.index.year == year]
        year_grouped_by_min = df_year.groupby(df_year.index.minute)['tickqty'].median()
    
        relative_values = (year_grouped_by_min / year_grouped_by_min.mean()) * 100 - 100
        summary_data = pd.Series([relative_values[0],
                                  relative_values[15],
                                  relative_values[30],
                                  relative_values[45],
                                  relative_values[59]], name=year, index=cols)
    
        res_table = res_table.append(summary_data)

    #plot a bar graph of the EUR USD over the whole period        
    plt.figure(figsize=(16.0, 10.0))
    ax = res_table.plot.bar(title="Relative Trade Volumes by Year", width=0.9, figsize=(16,10))
    ax.set_xlabel("Year")
    ax.set_ylabel("% Higher than Average")    
    
    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')
        
    plt.show()

    return res_table

def plot_volume_by_asset(assets, save_file = None):
    """ Plots the tick volume grouped by minute of the hour across several assets
    to confirm relationship exists in multiple assets
    
    Args:
        assets (string[]): list of strings of asset names
        save_file (string): filepath to save the figure to if desired       
    
    Returns:
        Pandas.DataFrame: the results on the 0,15,30,45 and 59 min periods for
            each asset
    
    """
    
    #just calculate the % more than mean for 0,15,30,40 and 59 minutes      
    cols = ["0 min", "15 min", "30 min", "45 min", "59 min"]    
    res_table = pd.DataFrame(columns = cols)
    
    #loop through the assets and the results to the table
    for asset in assets:
        
        df = load_asset_data(asset)
             
        #group tick volume by minute to see which minute of the hours has the highest activity
        whole_set_minute_vol = df.groupby(df.index.minute)['tickqty'].median()
        
        #convert this to a relative value to make it clearer in the graph
        relative_values = (whole_set_minute_vol / whole_set_minute_vol.mean()) * 100 - 100
        
        #add the summary values to the results table
        summary_data = pd.Series([relative_values[0],
                                  relative_values[15],
                                  relative_values[30],
                                  relative_values[45],
                                  relative_values[59]], name=asset, index=cols)        
        res_table = res_table.append(summary_data)
    
    #plot a bar graph of the EUR USD over the whole period   
    plt.figure(figsize=(16.0, 10.0))     
    ax = res_table.plot.bar(title="Relative Trade Volumes by Asset", width=0.9, figsize=(16,10))
    ax.set_xlabel("Year")
    ax.set_ylabel("% Higher than Average")    
    
    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')
        
    plt.show()
 
    return res_table
   
    
def tick_analysis_59_0_minute_volume(tick_file_directory, save_file=None):
    """ Looks at the distribution of tick volume in seconds across the 59th 
    and 0min. Tick data is saved in a seperate file for each day
    
    Args:
        tick_file_directory (string): the directory that contains all the 
            individual tick data for a single asset
        save_file (string): filepath to save the figure to if desired       
    
    Returns:
        Pandas.DataFrame: the results on the 0,15,30,45 and 59 min periods for
            each asset
    
    """  
    
    #function to convert timestamp into datetime
    def dateparse (time_in_secs):
        return datetime.datetime.fromtimestamp(float(time_in_secs) / 1000)
      
    #create a list to hold the dataframe of each tick file
    df_list = []
    
    #need to read all the tickfiles from the directiory - each day is stored
    #in a seperate file      
    file_list = os.listdir(tick_file_directory)
    i = 1
    #loop through the file list but due to memory constraints only use every
    #10th file
    for filename in file_list:    
        if i % 10 == 0: #not enough memory to read all files
            
            #show percentage completed
            per_complete = i / len(file_list) * 100
            print("\t\rReading files {:.1f}% complete".format(per_complete), end="")
            
            #load the csv data and append it to the list of dataframes
            df_list.append(pd.read_csv(tick_file_directory + "\\" + filename, header=None, date_parser=dateparse, parse_dates=True, index_col=0))
        i += 1
            
    #compile the list of dataframes into 1
    tick_data = pd.concat(df_list, sort=True, axis=0)    
    
    #gruop the ticks into seconds for the 59th and 0 minute
    df_0 = tick_data[tick_data.index.minute == 0]
    grouped_0 = df_0.groupby(df_0.index.second)[1].count()    
       
    df_59 = tick_data[tick_data.index.minute == 59]
    grouped_59 = df_59.groupby(df_59.index.second)[1].count()
    
    #distrubition across the seconds
    #The zero is at the exact change of hour, -60 is 1 minute before change of hour
    #and +60 is 1 minute after change of hour
    plt.figure(figsize=(16.0, 10.0))
    plt.bar(range(-60, 60), np.concatenate([grouped_59, grouped_0]))
    
    plt.title("Tick volume grouped by second for 59 and 0 minutes")
    plt.xlabel("Volume at Second")
    plt.ylabel("Volume of Ticks") 
    
    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')
        
    plt.show()
    

def back_test_simulation(asset_details, save_file_pips = None, 
                         save_file_profit = None, commission = 0.07):
    """ Runs a back test simulation to test the trading idea. 
    The simulation is run testing the trading idea on every minute in the hour
    If the theory is correct then the most profitable backtests would be the 
    back test simulation run on the 59th minute.
    Calculates the median values for number of pips movement and also a more 
    realistic median trade profit which takes into account spread and commission
    
    Args:
        asset_details ((string, double, double)): list of the assets to test
            string is the assetname, then pip value then pip cost
        save_file_pips (string): filepath to save the figure for pips movement      
        save_file_profit (string): filepath to save the figure for profit
        commission (double): round trip commission paid on each trade
        
    Returns:
        (Pandas.DataFrame, Pandas.DataFrame): Results by asset of median profit,
            results by asset of the median pip movement
    
    """ 
    
    #results for the trade profit median for strategy run on each minute
    results = pd.DataFrame()
    #results for the pips movement median for strategy run on each minute
    results_pips_median = pd.DataFrame()
    
    #loop through everyone of the passed assets and apply the trading idea
    for asset_detail in asset_details:
        
        #get the data needed from the passed asset tuple
        asset = asset_detail[0]
        pip = asset_detail[1]
        pip_cost = asset_detail[2]
        
        #load in the price data
        df = load_asset_data(asset)
        
        #the price level that the trade will be opened will be the open price
        #of the next available bar
        df["open_trade"] = df["askopen"].shift(-1)
        
        #the close leve will be 5 minutes after the open time ie. trade is held
        #for 5 minutes before closing.
        df["close_trade"] = df["askopen"].shift(-1).shift(-5)
        
        #calculate the spread in pips for each bar
        df["spread"] = (df["askopen"].shift(-1) - df["bidopen"].shift(-1)) / pip
        
        #calculate what the profit (pips) would be in terms of a long trade
        df["profit_pips"] = (df["close_trade"] - df["open_trade"]) / pip
    
        #declare a list for the median pip movement and the median trade profit
        median = []
        median_profit = []
        
        #cycle through every minute in the hour and apply the trading idea
        #if the theory is correct the 59th minute will produce superior results
        #to applying the trading idea to other minutes. If the theory is wrong
        #ther performance will be relatively similar no matter what minute is
        #used to apply the strategy
        for minute in range(60):
            
            #filter the bars to take only those that match the current minute
            df_min = df[df.index.minute == minute]
            #add another filter that make sure the movement in this bar is reasonable
            df_min = df_min[np.abs(df_min["profit_pips"]) > 15]
            #make sure we only take trades that are less than 3 pips otherwise
            #trading costs become to high
            df_min = df_min[df_min["spread"] < 3]
            
            #work out the direction of this bar, bull bar is a 1 and bear bar is a -1
            direction = np.where(df_min["askclose"] - df_min["askopen"] > 0, 1, -1)
        
            #calculte the median pip movement in the strategies favour by tradeing
            #in the opposite direction to the current bars movement
            median.append(-df_min["profit_pips"][direction == 1].median() + 
                        df_min["profit_pips"][direction == -1].median())
            
            #calcaulte a realistic profit by subtracting spread and commission
            short_trades = df_min[direction == 1] #take the inverse trade of the direction
            long_trades = df_min[direction == -1] #take the inverse trade of the direction
            short_trades_profit = (-short_trades["profit_pips"] - short_trades["spread"]) * pip_cost  - commission
            long_trades_profit = (long_trades["profit_pips"] - long_trades["spread"]) * pip_cost  - commission
            
            #use the profit calcaulations to work out the median profit of each
            #trade
            median_profit.append((short_trades_profit.median() + 
                                long_trades_profit.median()) / 2)
        
        #show some charts for each asset of the median pip movement performance
        #if the strategy was run on that minute - would expect the 59 min bar
        #to outperform the others if theory is proved correct.
        print(asset + " - median pips    |       median profit  (total trades: " + 
                                    str(len(short_trades_profit) + len(long_trades_profit)) + ")")
        a = plt.subplot(121)
        b = plt.subplot(122)
        a.bar(range(60), median)
        b.bar(range(60), median_profit)
        plt.show()
        
        #build a table of the results for each asset
        results = results.append(pd.Series(median_profit, name=asset))
        results_pips_median = results.append(pd.Series(median, name=asset))
        
    #final chart summary for all assets showing median profit across all assets    
    av = results.median(axis=0)
    plt.figure(figsize=(16.0, 10.0))
    plt.bar(range(60), av)
    plt.title("Median Profit (if the Strategy was run on that minute bar)")
    plt.xlabel("Strategy run on Minute")
    plt.ylabel("Median Profit across all assets") 
    
    if save_file_pips is not None:
        plt.savefig(save_file_pips, bbox_inches='tight')
    plt.show()
    
    #show median pip movement across all assets
    av = results_pips_median.median(axis=0)
    plt.figure(figsize=(16.0, 10.0))
    plt.bar(range(60), av)
    plt.title("Median Pip Movement (if the Strategy was run on that minute bar)")
    plt.xlabel("Strategy run on Minute")
    plt.ylabel("Median Pip movement across all assets") 
    
    if save_file_profit is not None:
        plt.savefig(save_file_profit, bbox_inches='tight')
    plt.show()
    
    return results, results_pips_median
        

    
if __name__ == "__main__":
    #load the EURUSD data
    eurusd = load_asset_data("EURUSD")
    
    #plot the EURUSD by minute
    plot_volume_by_minute(eurusd, save_file="eurusd_volume_by_minute.png")
    
    #plot the EURUSD by year
    res_table = plot_volume_by_year(eurusd, save_file="eurusd_volume_by_year.png")
    res_table.to_csv("D:\\Temp\\tick_volume_by_year.csv", header=True, index=True)    

    #look at all the assets to see if the same relationship exists
    res_table = plot_volume_by_asset(["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD", "NZDUSD", "USDCHF",
                                      "EURGBP", "EURJPY", "EURCAD", "EURAUD", "EURNZD", "EURCHF",
                                      "GBPJPY", "GBPCAD", "GBPAUD", "GBPNZD", "GBPCHF",
                                      "CADJPY", "AUDJPY", "NZDJPY", "CHFJPY",
                                      "AUDCAD", "NZDCAD", "CADCHF",
                                      "AUDNZD", "AUDCHF",
                                      "NZDCHF"],
                                      save_file="volume_by_asset.png")
    res_table.to_csv("D:\\Temp\\tick_volume_by_asset.csv", header=True, index=True)   
    
    #look at the tick data for the 59th minute and 0th minute to see where
    #the distribution of the volume is over the minute.
    tick_analysis_59_0_minute_volume("D:\\Websites\\TickFBDownload\\data\\EURUSD", 
                                     save_file = "tick_data_59_0_min.png")
    
    
    #Identified relationship that whatever direction the 59th minute bar goes in
    #there is a reversal of that direction in the few minutes afterwards
        
    #Run a backtest simulation to test this idea ie. trade in opposite direction
    #of the 59th candlestick move, if the move is large enough and if the spread is
    #small enough
    results = back_test_simulation([("EURUSD", 0.0001, 0.1403), 
                                     ("GBPUSD", 0.0001, 0.1403), 
                                     ("USDJPY", 0.01, 0.1258),  
                                     ("USDCAD", 0.0001, 0.1048), 
                                     ("AUDUSD", 0.0001, 0.1403), 
                                     ("NZDUSD", 0.0001, 0.1403), 
                                     ("USDCHF", 0.0001, 0.1403),
                                     ("EURGBP", 0.0001, 0.1826), 
                                     ("EURJPY", 0.01, 0.1258), 
                                     ("EURCAD", 0.0001, 0.1048), 
                                     ("EURAUD", 0.0001, 0.1), 
                                     ("EURNZD", 0.0001, 0.0942), 
                                     ("EURCHF", 0.0001, 0.1403), 
                                     ("GBPJPY", 0.01, 0.1258), 
                                     ("GBPCAD", 0.0001, 0.1048), 
                                     ("GBPAUD", 0.0001, 0.1), 
                                     ("GBPNZD", 0.0001, 0.0942), 
                                     ("GBPCHF", 0.0001, 0.1403), 
                                     ("CADJPY", 0.01, 0.1258), 
                                     ("AUDJPY", 0.01, 0.1258), 
                                     ("NZDJPY", 0.01, 0.1258), 
                                     ("CHFJPY", 0.01, 0.1258), 
                                     ("AUDCAD", 0.0001, 0.1048), 
                                     ("NZDCAD", 0.0001, 0.1048), 
                                     ("CADCHF", 0.0001, 0.1403), 
                                     ("AUDNZD", 0.0001, 0.0942), 
                                     ("AUDCHF", 0.0001, 0.1403), 
                                     ("NZDCHF", 0.0001, 0.1403)],
                                    save_file_pips="simulation_pips.png",
                                    save_file_profit="simulation_profit.png")




