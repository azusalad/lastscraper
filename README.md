# Last Scraper
Scrape profile data from last.fm.  Scrapes all the songs that a user has listened to and outputs to a csv file.  From there, you can now do library search for free or just analyze the data and make graphs/insights.
Example csv output:

```
title	artist	year	month	day	dow	time
Independence	神崎エルザ	2022	03	10	Thursday	18:58
Truth.	TrySail	2022	03	10	Thursday	18:54
ゆめみてたのあたし	DAOKO	2022	03	10	Thursday	18:49
infinite synthesis	fripSide	2022	03	10	Thursday	18:40
eternal pain	fripSide	2022	03	10	Thursday	18:00
trusty snow	fripSide	2022	03	09	Wednesday	22:43
meditations	fripSide	2022	03	09	Wednesday	22:36
closest love	fripSide	2022	03	09	Wednesday	22:32
crossing over	fripSide	2022	03	09	Wednesday	22:28
```
I used `\t` as my delimiter but you can change that in `config.py`.

## Requirements
Python, selenium with geckodriver, tqdm

`pip install -r requirements.txt`

You can get the geckodriver here: https://firefox-source-docs.mozilla.org/testing/geckodriver/index.html

## Usage
Edit `config.py` with your username and password.  A login is needed to scrape the data.  Library pages after page 1 do not load unless you are logged in.  You also need to point to the geckodriver (and optionally a ublock origin xpi file).  You can also change other things in the config like what delimiter you want to use.  Once you have finished editing the config, run the main program.

`python main.py`

The program will scrape all your songs from present to where you last scraped songs (or until the beginning of your scrobbles if you never ran the program before).  You should run the program until it finishes or else the data will be incomplete.  The next time you run the program there will be time gaps in the csv.  Make sure the program completes without errors to avoid that from happening.

Daylight savings time messes up the program a little bit.  Time will always be recorded in the current timezone.  When scraping, the program will add/subtract 1 hour to the timestamp when checking for duplicates (minutes stay the same).  Recording scrobbles will stay normal though.
