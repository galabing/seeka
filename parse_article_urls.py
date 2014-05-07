#!/usr/bin/python

import argparse
import os

URL_PATTERN_START = "'/article/"
URL_PATTERN_END = "'"
MIN_COUNT = 45
MAX_COUNT = 55

def parse_index_file(index_file, url_list, url_set):
  with open(index_file, 'r') as fp:
    content = fp.read()
  count = 0
  start = 0
  while True:
    p = content.find(URL_PATTERN_START, start)
    if p < 0:
      break
    q = content.find(URL_PATTERN_END, p+1)
    assert q > p
    url = content[p+1:q]  # Get rid of surrouding 's.
    start = q + 1
    if url in url_set:
      continue
    url_list.append(url)
    url_set.add(url)
    count += 1
  assert count >= MIN_COUNT
  assert count <= MAX_COUNT

def parse_article_urls(index_dir, url_file):
  index_files = [f for f in os.listdir(index_dir) if f.endswith('.html')]
  print 'processing %d index files' % len(index_files)
  url_list = []  # Output order.
  url_set = set()  # For deduping urls across pages.
  for i in range(len(index_files)):
    print 'processing %d/%d: %s' % (i+1, len(index_files), index_files[i])
    parse_index_file('%s/%s' % (index_dir, index_files[i]), url_list, url_set)
    assert len(url_list) == len(url_set)  # Sanity check.
  with open(url_file, 'w') as fp:
    for url in url_list:
      print >> fp, url

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--index_dir', required=True)
  parser.add_argument('--url_file', required=True)
  args = parser.parse_args()
  parse_article_urls(args.index_dir, args.url_file)

if __name__ == '__main__':
  main()

