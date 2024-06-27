# coding=utf-8
"""
    Extract and elaborate MATLAB data from emoBody project by Nummenmaa et al.
    WARNING: Execute this script before simulation!

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from scipy.io import loadmat
from numpy import isnan, average
from pandas import read_csv, DataFrame, Index

if __name__ == "__main__":
    emo_body_data = loadmat('./resources/data/emotions_data.mat')  # Load MATLAB Workspace
    emotions = ['anger', 'fear', 'happiness', 'sadness', 'disgust', 'neutral']  # Select emotion for the simulation
    colours = ['cyan', 'blue', 'black', 'dark red', 'red', 'yellow']  # emBody color map
    color_range = [[-15, -9], [-9, -4], [-4, -0], [0, 4], [4, 9], [9, 15]]  # emBody ranges color map
    emo_subset = {key: emo_body_data[key] for key in emotions}  # Extract selected emotion from starting data
    ranges = read_csv('./resources/data/ranges.csv')  # Read selected pixel range
    ranges = ranges.sort_values('Body Part')
    ranges = ranges.set_index('Body Part')

    emo_df = DataFrame(columns=list(ranges.index))
    emo_df_color = DataFrame(columns=list(ranges.index))

    # For each emotion provided by Nummenmaa evaluate average value from every selected body part
    for label in emotions:
        data = emo_subset[label]
        new_row = {}
        new_row_color = {}
        for body_part in ranges.index:
            emo_data = data[ranges.at[body_part, 'x_min']:ranges.at[body_part, 'x_max'],
                            ranges.at[body_part, 'y_min']:ranges.at[body_part, 'y_max']]
            emo_data = emo_data[~(isnan(emo_data))]
            avg_value = average(emo_data)
            for c_range, color in zip(color_range, colours):
                start = c_range[0]
                end = c_range[1]
                if int(avg_value) in range(start, end):
                    new_row_color[body_part] = color
                    new_row[body_part] = c_range
                    break
        emo_df = emo_df.append(new_row, ignore_index=True)
        emo_df_color = emo_df_color.append(new_row_color, ignore_index=True)
    emo_df.set_index(Index(emotions, name='Emotions'), inplace=True)
    emo_df_color.set_index(Index(emotions, name='Emotions'), inplace=True)

    # Save extracted information in CSV file
    emo_df.to_csv('./resources/data/emBody_value.csv')
    emo_df_color.to_csv('./resources/data/emBody_color.csv')
