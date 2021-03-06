# -*- coding: utf-8 -*-
"""DATA_CONTEST.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10DVjTGs21aeVlP7yNWzBNjWwzZITt_q8
"""

import numpy as np
from sklearn.datasets import load_digits
import matplotlib.pyplot as plt
import pandas as pd
import csv

import pandas as pd

df = pd.read_csv('train.csv')
table = df.pivot_table(index='customer_id', columns='song_id', values='score')

Songs_df = pd.read_csv('songs.csv')
Song_labels_df = pd.read_csv('song_labels.csv')
xx = pd.unique(Song_labels_df['label_id'])
yy = pd.unique(Song_labels_df['platform_id'])

Songs_df = Songs_df.sort_values(by = ['song_id']).reset_index(drop = True)

Songs_full_df = pd.merge(Songs_df,Song_labels_df,on = "platform_id",how = 'outer')

customers = pd.unique(df.sort_values(by=['customer_id'])['customer_id']).reshape(14053,1)
customer_index = {}
index = 0
for i in customers:
  customer_index[i[0]] = index
  index+=1


release_year = Songs_df['released_year'].to_numpy()
release_year[np.isnan(release_year)] = 0
Num_com = Songs_df['number_of_comments'].to_numpy()
song_ids = Songs_df['song_id'].to_numpy()

updated_release_year = np.full(10000,0)
updated_Num_com = np.full(10000,0)

for i in range(len(song_ids)):
  id = song_ids[i]
  updated_release_year[id-1] = release_year[i]
  updated_Num_com[id-1] = Num_com[i]

updated_release_year[updated_release_year < 0] = 0

ry_max = np.max(updated_release_year)
nc_max = np.max(updated_Num_com)

ry_min = np.min(updated_release_year)
nc_min = np.min(updated_Num_com)

updated_release_year *= 4
updated_release_year = updated_release_year/ry_max
updated_release_year += 1 

updated_Num_com *= 4
updated_Num_com = updated_Num_com/nc_max
updated_Num_com+= 1

# print(table[1]>0)

Song_Rating = table.to_numpy().copy()
Song_Rating[np.isnan(Song_Rating)] = 0
Song_Rating = np.append(Song_Rating, np.array([updated_release_year]), axis=0)
Song_Rating = np.append(Song_Rating, np.array([updated_Num_com]), axis=0)

customer_rating_sum = np.sum(Song_Rating,axis = 1)
customer_rating_count = np.sum(Song_Rating>0,axis = 1)
customer_rating_avg = customer_rating_sum/customer_rating_count

SS  = np.zeros((len(customer_rating_avg),10000))

for j in range(len(customer_rating_avg)):
  for i in range(10000):
   if Song_Rating[j][i] > 0:
     SS[j][i] = Song_Rating[j][i] - customer_rating_avg[j]

SS1 = np.transpose(SS)

from sklearn.metrics.pairwise import cosine_similarity
cosine_sim = cosine_similarity(SS1,SS1)

cosine_sim3 = cosine_sim.copy()
cosine_sim3[cosine_sim3 < 0] = 0

df1 = pd.read_csv('test.csv')

score = np.zeros(len(df1))
for index,row in df1.iterrows():
  i = customer_index[row['customer_id']]
  j = row['song_id'] - 1
  x = np.sum(cosine_sim3[j][Song_Rating[i] > 0])
  if x != 0:
    score[index] = np.dot(Song_Rating[i],cosine_sim3[j])/x
  else:
    score[index] = customer_rating_avg[i]

data = {'test_row_id':range(0,len(df1)),'score':score}
df2 = pd.DataFrame(data)

df2.to_csv('test22.csv',index = False)

