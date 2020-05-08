#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-05-07 08:19:57
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import requests
import re
import random

books = {'Book_name':[], 'Author':[], 'Rating':[], 'Rating_nums':[]}

# Define a function to get all the valid pages

headers = [
{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'},
{'User-Agent': "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"},
{'User-Agent': "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3; MS-RTC LM 8; Zune 4.7)"},
{'User-Agent': "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.1.4322)"},
{'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b9pre) Gecko/20101228 Firefox/4.0b9pre"},
{'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:2.0b11pre) Gecko/20110126 Firefox/4.0b11pre"},
{'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.2.9) Gecko/20100824 Firefox/3.6.9 ( .NET CLR 3.5.30729; .NET CLR 4.0.20506)"}]


# Define a function to transform html to bs object
def Url_to_bs(URL, proxies=None):

	try:
		response = requests.get(URL, headers=random.choice(headers), proxies=proxies)
	except  (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
		print(e)
	bs_obj = bs(response.text, 'html.parser')
	return bs_obj

# bookname filter
def Isbookornot(tag):
	return tag.has_attr('title') and tag.has_attr('href')


def Get_pages(tag):
	pages = []
	# Loop to get all pages
	for i in range(1000):
		html = ('https://book.douban.com/tag/{}?start={}&type=T').format(tag, i*20)
		bs_obj = Url_to_bs(html)
		if bs_obj.find_all('li', 'subject-item'):
			pages.append(html)
		else:
			break
	return pages

def Scraping_pages(pages):
	# Create a dict to store data
	# loop to get all pages
	for page in pages:
		books_list = Url_to_bs(page)
		bknames_raw = books_list.find_all(Isbookornot)

		# loop to get all book names
		for bkname in bknames_raw:
			bk = bkname.get_text(strip=True)
			books['Book_name'].append(bk)

		# loop to get all pub_info
		for bkinfo in books_list.find_all('div', 'pub'):
		 	book_info = list(bkinfo.get_text(strip=True).split('/'))
		 	books['Author'].append(book_info[0])

		for bkinfo in books_list.find_all('div', 'star clearfix'):
			# add zero value for missing tag
			if bkinfo.find('span', 'rating_nums'):
				bkrating = bkinfo.find('span', 'rating_nums')
				books['Rating'].append(bkrating.get_text())
			else:
				books['Rating'].append(0)

		for bkrating_nums in books_list.find_all('span', class_='pl'):
			rating_nums = bkrating_nums.get_text(strip=True)
			books['Rating_nums'].append(rating_nums)
	return books

# Transform dict to excel
def books_to_datafram(books):
	df = pd.DataFrame(data=books)
	# Get object to number
	df.iloc[:,2] = pd.to_numeric(df.iloc[:,2], errors='coerce')
	# Get number from strings
	for index in range(len(df)):
		df.iloc[index,3] = re.sub('\D', '', df.iloc[index,3])
	df.iloc[:,3] = pd.to_numeric(df.iloc[:,3], errors='coerce')
	return df

# Transform df to excel
def df_excel(df_data, data_tag, out_path='/Users/finnlee/Data_anlysis_projects/datasets/douban_books/books.xlsx'):
	writer = pd.ExcelWriter(out_path, engine='xlsxwriter')
	df_data.to_excel(writer, sheet_name=data_tag, index=False)
	writer.save()


if __name__ == '__main__':
	tag = '心理学'
	pages = Get_pages(tag)
	books = Scraping_pages(pages)
	# print(len(books['Book_name']), len(books['Author']), len(books['Rating']), len(books['Rating_nums']))
	# print(books['Rating'])
	df = books_to_datafram(books)
	df_excel(df, tag)


