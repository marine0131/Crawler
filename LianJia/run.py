from scrapy import cmdline
cmdline.execute("scrapy crawl lianjiaspider -o items.json -t json".split())
