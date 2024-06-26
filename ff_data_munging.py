# -*- coding: utf-8 -*-
"""FF Data Munging.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ecQxe-yvcDHz5DbIaKiCDX9qLeTZXv8y
"""

import pandas as pd
link = 'https://raw.githubusercontent.com/fantasydatapros/LearnPythonWithFantasyFootball/master/2023/06-Data%20Munging/01-FDP%20Projections%20-%20(2023.03.30).csv'
adp = 'https://raw.githubusercontent.com/fantasydatapros/LearnPythonWithFantasyFootball/master/2023/06-Data%20Munging/02-ADP%20Data%20-%20(2023.03.30).csv'

df=pd.read_csv(link)

scoring_weights = {

    'receptions': 0.5, # half-PPR

    'receiving_yds': 0.1,

    'receiving_td': 6,

    'rushing_yds': 0.1,

    'rushing_td': 6,

    'passing_yds': 0.04,

    'passing_td': 4,

    'int': -2

}
df['FantasyPoints'] = (

    df['Receptions']*scoring_weights['receptions'] + df['ReceivingYds']*scoring_weights['receiving_yds'] + \

    df['ReceivingTD']*scoring_weights['receiving_td'] + \

    df['RushingYds']*scoring_weights['rushing_yds'] + df['RushingTD']*scoring_weights['rushing_td'] + \

    df['PassingYds']*scoring_weights['passing_yds'] + df['PassingTD']*scoring_weights['passing_td'] + \

    df['Int']*scoring_weights['int'] )

base_columns=['Player','Pos','Team']
rushing_columns=['FantasyPoints','Receptions','ReceivingYds','ReceivingTD','RushingAtt','RushingYds','RushingTD']

rb_df=df.loc[df['Pos']=='RB',base_columns + rushing_columns]

rb_df.head()

rb_df.sort_values(by='Receptions',ascending=False)

rb_df.describe()

rb_df['RushingAtt']

rb_df['RushingTDRank']=rb_df['RushingTD'].rank(ascending=False)

rb_df

import seaborn as sns

sns.set_style('whitegrid')
sns.displot(rb_df['RushingAtt'])

rb_df['RushingAtt'].plot.hist()

rb_df.values[:5]

adp_df = pd.read_csv(adp)

adp_df.head()

adp_df['ADP RANK']=adp_df['Current ADP'].rank()

adp_df

adp_df_cutoff=adp_df[:75]

adp_df_cutoff

replacement_players={
    'RB':'',
    'QB':'',
    'WR':'',
    'TE':''
}

for _,row in adp_df_cutoff.iterrows():
 position = row['Pos']
 player = row['Player']

 if position in replacement_players:
  replacement_players[position]=player

replacement_players

#Filtering our data to only include the following 5 columns
df=df[['Player','Pos','Team','FantasyPoints']]

df.head()

replacement_values=dict()
#We have our dictionary of replacement players
#Now we are using the data table to find the values of those players

for position,player_name in replacement_players.items():
  #loc filters data frame
  #going through the data table until we find the same player as our replacement player
  player = df.loc[df['Player']==player_name]
  #After we match the player now grab their corresponding points from the 'FantasyPoints' column
  #and set it equal to the replacement_value variable
  replacement_value=player['FantasyPoints'].tolist()[0]
  #then add that value to the dictionary
  replacement_values[position]=replacement_value

replacement_values

#add Value Over Replacement column to dataframe
#df.apply applies a function across every row in our dataframe
df['VOR'] = df.apply(
    #Goes through row by row and accesses the 'FantasyPoints' and 'Pos' columns
    #Starts with Josh Allen, sees QB and 413.44 points
    #Takes that number and subtracts the replacement_value of QB Trevor Lawrence
    #which is 295.36
    #Results in a VOR for Josh Allen equal to 118
    lambda row: row['FantasyPoints'] - replacement_values[row['Pos']], axis=1
)

df.head()

df = df.sort_values(by='VOR',ascending=False)
df.head()

df['VOR Rank']=df['VOR'].rank(ascending=False)

pd.set_option('display.max_rows',None)
df.head(100)

df.groupby('Pos')['VOR'].describe()

#Normalizing the data with min-max scaling
#Common technique in statistics to scale numerical features to a range between 0 and 1
#Formula: x_normalized = (x-x_min) / (x_max - x_min)
#Ensures min value becomes 0 and max value becomes 1
df['VOR'] = df['VOR'].apply(lambda x:(x-df['VOR'].min()) / (df['VOR'].max() - df['VOR'].min()))

df.head()

sns.boxplot(x=df['Pos'], y=df['VOR'])

df = df.rename({
    'VOR':'Value',
    'VOR Rank':'Value Rank'
}, axis=1)

df.head()

adp_df = adp_df.rename({
    'PLAYER': 'Player',
    'POS': 'Pos',
    'AVG':'Average ADP',
    'ADP RANK':'ADP Rank'

}, axis=1)

adp_df.head()

df['Player'] = df['Player'].replace({

    'Kenneth Walker III': 'Kenneth Walker',
    'Travis Etienne Jr.': 'Travis Etienne',
    'Brian Robinson Jr.': 'Brian Robinson',
    'Pierre Strong Jr.': 'Pierre Strong',
    'Michael Pittman Jr.': 'Michael Pittman',
    'A.J. Dillon': 'AJ Dillon',
    'D.J. Moore': 'DJ Moore'

})

df.head()

adp_df = adp_df.drop('Team', axis=1)
final_df=df.merge(adp_df,how='left',on=['Player','Pos'])

final_df.head()

# let's calculate the difference between our value rank and adp rank
final_df['Diff in ADP and Value'] = final_df['ADP Rank'] - final_df['Value Rank']

#removing outliers in ADP

final_df = final_df.loc[final_df['ADP Rank'] <= 212]

final_df.head()

draft_pool = final_df.sort_values(by='ADP Rank')[:196]

rb_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'RB']
qb_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'QB']
wr_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'WR']
te_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'TE']

# top 10 RB sleepers for this year's draft

rb_draft_pool.sort_values(by='Diff in ADP and Value', ascending=False)[:10]

# top 10 RB overvalued for this year's draft

rb_draft_pool.sort_values(by='Diff in ADP and Value', ascending=True)[:10]

# top 10 WR sleeprs for this year's draft

wr_draft_pool.sort_values(by='Diff in ADP and Value', ascending=False)[:10]

# top 10 WR overvalued for this year's draft

wr_draft_pool.sort_values(by='Diff in ADP and Value', ascending=True)[:10]

# top 10 TE sleepers for this year's draft

te_draft_pool.sort_values(by='Diff in ADP and Value', ascending=False)[:10]

# top 10 TE overvalued for this year's draft

te_draft_pool.sort_values(by='Diff in ADP and Value', ascending=True)[:10]

# top 10 QB sleepers for this year's draft

qb_draft_pool.sort_values(by='Diff in ADP and Value', ascending=False)[:10]

# top 10 QB overvalued for this year's draft

qb_draft_pool.sort_values(by='Diff in ADP and Value', ascending=True)[:10]

#Most undervalued players in all positions
final_df.sort_values(by='Diff in ADP and Value', ascending=False)[:10]

#Most overvalued
final_df.sort_values(by='Diff in ADP and Value', ascending=True)[:10]