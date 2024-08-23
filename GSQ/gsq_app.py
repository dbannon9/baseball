# import pybaseball as pb
import pandas as pd
from datetime import datetime
from os import path
import streamlit as st

#
# Load game log data for starters into table
# 

gl = pd.read_csv('GSQ/data/pgamelog24.csv')

gl['GS'] = pd.to_numeric(gl['GS'], errors='coerce')
gl['PitcherID'] = gl['PitcherID'].astype(str)

spgl24 = pd.DataFrame(gl[gl['GS'] == 1])

# Convert IP to Outs

spgl24['Outs'] = 10*spgl24['IP'] - 7*round(spgl24['IP'],0)

# Calculate GS2

spgl24['GS2'] = (40 + 2*spgl24['Outs'] + spgl24['K'] - 2*spgl24['BB'] - 2*spgl24['H'] - 3*spgl24['R'] - 6*spgl24['HR'])

#
# Create aggregated GSQ dataset and calculate GSQ
# 

gsq = pd.DataFrame(spgl24.groupby('PitcherID',as_index=False).agg(
    Pitcher = ('Pitcher','max'),
    GS = ('GS','sum'),
    # IP = ('IP', 'sum'),
    K = ('K', 'sum'),
    BB = ('BB', 'sum'),
    GS2 = ('GS2', 'mean'),
    GSD = ('GS2', 'std')
))

gsq['GSD'] = gsq['GSD'].fillna(value=1).replace(0,1)

gsq['GSQ'] = gsq['GS2'] / gsq['GSD']

# 
# Streamlit App!
# 

st.title('MLB Pitching Consistency Leaderboard')
st.header('Game Score Quotient')
st.subheader('Quantifying Pitcher Risk by Inconsistency')
st.write('Game Score Quotient (GSQ) provides a risk-adjusted sense of game-by-game performance. '+
        'Similar to the financial measure "Sharpe Ratio", it divides a quality measure - in this case, Game Score 2 (GSD) '+
        'by a measure of variation - in this case, standard deviation of GS2 (GSD)')
num = st.number_input('Minimum Number of Games Started (GS)',0,30)
df1 = gsq[['Pitcher','GSQ','GS2','GSD','GS','K']].query(f'GS >= {num}').sort_values('GSQ',ascending=False)

st.dataframe(df1)