#!/usr/bin/python

import argparse
import os

HOST = 'http://seekingalpha.com'
WGET = '/usr/local/bin/wget'
RETRIES = 5

URL_PREFIX = '/article/'

def download_article(url, cookie_file, output_path):
  cmd = '%s -q -x --load-cookies "%s" "%s" -O "%s"' % (
      WGET, cookie_file, url, output_path)
  for i in range(RETRIES):
    if os.system(cmd) == 0:
      assert os.path.isfile(output_path)
      return True
    print '(download failed for %s, try %d)' % (url, i+1)
    if os.path.isfile(output_path):
      os.remove(output_path)
  return False

def download_articles(url_file, cookie_file, article_dir, overwrite):
  with open(url_file, 'r') as fp:
    urls = fp.read().splitlines()
  print 'processing %d urls' % len(urls)

  downloaded, failed, skipped = 0, 0, 0
  for i in range(len(urls)):
    output_dir = '%s/%04d' % (article_dir, i/1000)
    if not os.path.isdir(output_dir):
      os.mkdir(output_dir)
    assert urls[i].startswith(URL_PREFIX)
    p = urls[i].find('-')
    assert p > len(URL_PREFIX)
    article_id = int(urls[i][len(URL_PREFIX):p])
    output_path = '%s/%d.html' % (output_dir, article_id)

    if os.path.isfile(output_path):
      if not overwrite:
        skipped += 1
        continue
      os.remove(output_path)

    url = '%s%s' % (HOST, urls[i])
    print '%d/%d: %s => %s' % (i+1, len(urls), url, output_path)
    ok = download_article(url, cookie_file, output_path)
    if ok:
      downloaded += 1
    else:
      skipped += 1
  print 'downloaded: %d, failed: %d, skipped: %d' % (
      downloaded, failed, skipped)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--url_file', required=True)
  parser.add_argument('--cookie_file', required=True)
  parser.add_argument('--article_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  args = parser.parse_args()
  download_articles(args.url_file, args.cookie_file, args.article_dir,
                    args.overwrite)

if __name__ == '__main__':
  main()

