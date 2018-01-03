#! /usr/bin/env  python

import json
import csv
import sys

json_file = sys.argv[1]
csv_file = json_file.split('/')[-1].split('.')[0]+'.csv'

with open(json_file, 'r') as f:
    h_dict = json.load(f)

# for h in h_dict:
#     h['city'] = h['city'].encode("UTF-8")
#     h['title'] = h['title'].encode("UTF-8")
#     h['focus_num'] = h['focus_num'].encode("UTF-8")
#     h['area'] = h['area'].encode("UTF-8")
#     h['community'] = h['community'].encode("UTF-8")
#     h['watch_num'] = h['watch_num'].encode("UTF-8")
#     h['time'] = h['time'].encode("UTF-8")
#     h['model'] = h['model'].encode("UTF-8")
#     h['average_price'] = h['average_price'].encode("UTF-8")

# encode_dict = json.dumps(h_dict, ensure_ascii=False)
encode_dict = h_dict

with open(csv_file, 'w') as f:
    csv_writer = csv.writer(f)
    for item in encode_dict:
        csv_writer.writerow([item[s].encode('utf-8') for s in item])
           #  item['city'],
           #                   item['community'],
           #                   item['title'],
           #                   item['area'],
           #                   item['time'],
           #                   item['focus_num'],
           #                   item['watch_num'],
           #                   item['model'],
           #                   item['price'],
           #                   item['average_price'],
           #                   item['link']])

# with open('encode_items.json','w') as f:
#     json.dump(h_dict, f, ensure_ascii=False)
