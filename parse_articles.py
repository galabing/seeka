#!/usr/bin/python

from bs4 import BeautifulSoup
import argparse
import datetime
import os
import re

symbol_prog = re.compile(
    '/symbol/(?P<ticker>[A-Za-z]{1,4}(\.[A-Z][a-z]{1,2})?)')

class ContentStatus:
  VALID = 0
  INVALID_HEADER = 1
  INVALID_ENDING = 2
  SOUND_MONEY_TIPS = 3
  UNDATED = 4
  INVALID_TITLE = 5
  INVALID_BODY = 6

status_str_map = {
    ContentStatus.VALID: 'valid',
    ContentStatus.INVALID_HEADER: 'invalid header',
    ContentStatus.INVALID_ENDING: 'invalid ending',
    ContentStatus.SOUND_MONEY_TIPS: "sound money tips",
    ContentStatus.UNDATED: 'undated',
    ContentStatus.INVALID_TITLE: 'invalid title',
    ContentStatus.INVALID_BODY: 'invalid body',
}

def is_sound_money_tips(content):
  return content.find(
      '<title>Make Money, Save Money -- Sound Money Tips</title>') >= 0

first_value_error = True
def get_date(content):
  global first_value_error
  p = content.find('<div class="article_info_pos">')
  if p < 0:
    return None
  p = content.find('<span>', p)
  if p < 0:
    return None
  # Get rid of timezone as it's not python standard and is always the same.
  q = content.find(' ET</span>', p)
  if q < 0:
    return None
  date_str = content[p+len('<span>'):q]
  try:
    date = datetime.datetime.strptime(
        date_str, '%b. %d, %Y  %I:%M %p')
  except ValueError:
    if first_value_error:
      print 'first value error: %s' % date_str
      first_value_error = False
    return None
  return date

def validate(content):
  date = None
  if not content.startswith('<!DOCTYPE html>'):
    return ContentStatus.INVALID_HEADER, date
  if not content.endswith('</html>\n'):
    return ContentStatus.INVALID_ENDING, date
  if is_sound_money_tips(content):
    return ContentStatus.SOUND_MONEY_TIPS, date
  status = ContentStatus.UNDATED
  date = get_date(content)
  if date is not None:
    status = ContentStatus.VALID
  return status, date

def extract_tickers(content):
  tickers = symbol_prog.findall(content)
  # Why?
  assert all([len(ticker) == 2 and ticker[1] == '' for ticker in tickers])
  return set([ticker[0].upper() for ticker in tickers])

TITLE_PREFIX = '<span itemprop="name"'
def extract_content(content):
  soup = BeautifulSoup(content)
  title_soup = soup.find_all('span', itemprop='name')
  if len(title_soup) == 0 or len(title_soup) > 1:
    return None, None, ContentStatus.INVALID_TITLE
  title = title_soup[0].text.encode('ascii', errors='ignore')
  body_soup = soup.find_all('div', id='article_body')
  if len(body_soup) == 0 or len(body_soup) > 1:
    return title, None, ContentStatus.INVALID_BODY
  body = body_soup[0].text.encode('ascii', errors='ignore')
  return title, body, ContentStatus.VALID

def parse_article(content):
  status, date = validate(content)
  if status != ContentStatus.VALID:
    assert date is None
    return None, None, None, status
  assert date is not None
  tickers = extract_tickers(content)
  title, body, status = extract_content(content)
  return date, tickers, title, body, status

def parse_articles(article_dir, debug_count, overwrite, parsed_dir):
  folders = sorted(os.listdir(article_dir))
  debug_count_str = 'all'
  if debug_count > 0:
    debug_count_str = 'at most %d' % debug_count
  print 'processing %s files from %d folders' % (debug_count_str, len(folders))
  processed, skipped = 0, 0
  status_map = dict()
  for i in range(len(folders)):
    print '%d/%d: %s' % (i+1, len(folders), folders[i])
    output_dir = '%s/%s' % (parsed_dir, folders[i])
    if not os.path.isdir(output_dir):
      os.mkdir(output_dir)
    folder_dir = '%s/%s' % (article_dir, folders[i])
    articles = os.listdir(folder_dir)
    for article in articles:
      assert article.endswith('.html')
      base = article[:-5]
      meta_path = '%s/%s.meta' % (output_dir, base)
      data_path = '%s/%s.data' % (output_dir, base)
      if (os.path.isfile(meta_path) and
          os.path.isfile(data_path) and
          not overwrite):
        skipped += 1
        continue
      article_path = '%s/%s' % (folder_dir, article)
      with open(article_path, 'r')  as fp:
        content = fp.read()
      date, tickers, title, body, status = parse_article(content)
      if status == ContentStatus.VALID:
        with open(meta_path, 'w') as fp:
          print >> fp, date
          print >> fp, ' '.join(sorted(tickers))
        with open(data_path, 'w') as fp:
          print >> fp, title
          print >> fp, body
      #else:
      #  print article_path
      #  assert False
      if status not in status_map:
        status_map[status] = 1
      else:
        status_map[status] += 1
      processed += 1
      if debug_count > 0 and processed >= debug_count:
        print 'reached debug limit (%d)' % debug_count
        return processed, skipped, status_map
  return processed, skipped, status_map

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--article_dir', required=True)
  parser.add_argument('--debug_count', default=0)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--parsed_dir', required=True)
  args = parser.parse_args()
  processed, skipped, status_map = parse_articles(
      args.article_dir, int(args.debug_count), args.overwrite, args.parsed_dir)
  print 'processed %d files, skipped %d files' % (processed, skipped)
  print 'processed status map:'
  for status in sorted(status_map.keys()):
    print '%s: %d' % (status_str_map[status], status_map[status])

if __name__ == '__main__':
  main()

