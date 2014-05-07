#!/usr/bin/python

import argparse
import os

WGET = '/usr/local/bin/wget'
RETRIES = 5
N = 8300

def download_index(output_dir):
  for i in range(1, N+1):
    url = 'http://seekingalpha.com/analysis/all/all/%d' % i
    output_path = '%s/%d.html' % (output_dir, i)
    print '%d/%d: downloading %s => %s' % (i, N, url, output_path)
    cmd = '%s -q "%s" -O "%s"' % (WGET, url, output_path)
    for j in range(RETRIES):
      if os.system(cmd) == 0:
        assert os.path.isfile(output_path)
        break
      print '(download failed for %s, try %d)' % (url, j+1)
      if os.path.isfile(output_path):
        os.remove(output_path)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  download_index(args.output_dir)

if __name__ == '__main__':
  main()

