import csv

with open('comments/sound_comments.csv', 'rb') as f:
    reader = csv.reader(f)
    your_list = list(reader)

value_arr =  your_list[1:]
print type(your_list[3])
print your_list[3]