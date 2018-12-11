import re
import ssl
import time
from urllib import request


class Streamer:
	video_view_info_pattern = "([\d\.]*)([\w\W]*)"
	unit_map = {
		'千':  1000,
		'万':  10000,
		'十万': 100000,
		'百万': 1000000,
		'千万': 10000000,
		'亿':  100000000,
		'十亿': 1000000000,
		'百亿': 10000000000,
		'千亿': 100000000000
	}
	
	def __init__(self, video_title, video_nickname, video_view):
		self.video_title = video_title
		self.video_nickname = video_nickname
		self.video_view_org = video_view
		self.video_view = self.__process_view(video_view)
	
	def __process_view(self, video_view_info):
		buffer = re.search(Streamer.video_view_info_pattern, video_view_info)
		video_view_number = buffer.group(1)
		video_view_unit = self.__process_unit(buffer.group(2))
		final = float(video_view_number) * video_view_unit
		return final
	
	def __process_unit(self, video_view_unit):
		if not video_view_unit:
			return 1
		return Streamer.unit_map[video_view_unit]

class Clawer:
	url = "https://www.panda.tv/cate/lol"
	root_pattern = '<div class="video-info">[\s\S]*?</div>'
	video_title_pattern = '<span class="video-title" title="([\s\S]*?)">[\s\S]*?</span>'
	video_nickname_pattern = '<span class="video-nickname" title="([\s\S]*?)">[\s\S]*?</span>'
	video_view_number_pattern = '<span class="video-number">([\s\S]*?)</span>'
	
	def __fetch_content(self):
		context = ssl._create_unverified_context()
		print("connecting to server...", end=" ")
		print(Clawer.url)
		r = request.urlopen(Clawer.url, context=context)
		html = str(r.read(), encoding="UTF-8")
		return html
	
	def __analysis(self, html):
		root_result = re.findall(Clawer.root_pattern, html)
		
		def map_func(html_sub):
			video_title = re.search(Clawer.video_title_pattern, html_sub).group(1)
			video_nickname = re.search(Clawer.video_nickname_pattern, html_sub).group(1)
			video_view_number = re.search(Clawer.video_view_number_pattern, html_sub).group(1)
			return Streamer(video_title, video_nickname, video_view_number)
		
		print("Analysing Data...")
		result = map(map_func, root_result)
		return list(result)
	
	def __sort(self, result_table):
		return sorted(result_table, key=lambda each: each.video_view, reverse=True)
	
	rank_No_title = "Rank"
	video_title_title = "Title"
	video_nickname_title = "Nickname"
	video_views_title = "Views"
	
	def __print_rank_table(self, result_table):
		# get the longest from rank number
		rank_no_longest = int(len(str(len(result_table))))
		rank_no_longest = max(rank_no_longest, int(len(Clawer.rank_No_title)))
		# get the longest from title
		video_title_longest = Clawer.grab_longest_length(result_table, lambda item: int(len(item.video_title)))
		video_title_longest = max(video_title_longest, int(len(Clawer.video_title_title)))
		# get the longest from nickname
		video_nickname_longest = Clawer.grab_longest_length(result_table, lambda item: int(len(item.video_nickname)))
		video_nickname_longest = max(video_nickname_longest, int(len(Clawer.video_nickname_title)))
		# get the longest from video views
		video_views_longest = Clawer.grab_longest_length(result_table, lambda item: int(len(item.video_view_org)))
		video_views_longest = max(video_views_longest, int(len(Clawer.video_views_title)))
		# print time stamp
		print("Update time : " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		# print table header
		print(Clawer.pad_str(Clawer.rank_No_title, rank_no_longest, padder=' ', from_start=True), end=' | ')
		print(Clawer.pad_str(Clawer.video_views_title, video_views_longest, padder=' ', from_start=False), end=' |')
		print(Clawer.pad_str(Clawer.video_title_title, video_title_longest, padder=' ', from_start=False), end=' |')
		print(Clawer.pad_str(Clawer.video_nickname_title, video_nickname_longest, padder=' ', from_start=False))
		adder = 0
		for streamer in result_table:
			adder += 1
			print(Clawer.pad_str(str(adder), rank_no_longest, padder=' ', from_start=True), end=" | ")
			print(Clawer.pad_str(streamer.video_view_org, video_views_longest, padder=' ', from_start=False), end=' |')
			print(Clawer.pad_str(streamer.video_title, video_title_longest, padder=' ', from_start=False), end=' |')
			print(Clawer.pad_str(streamer.video_nickname, video_nickname_longest, padder=' ', from_start=False))
	
	@staticmethod
	def grab_longest_length(iterable, callback):
		table = map(callback, iterable)
		table = sorted(table, reverse=True)
		return table[0]
	
	@staticmethod
	def pad_str(str, desired, padder=' ', from_start=False):
		if len(str) >= desired:
			return str
		padding = ''
		for adder in range(int((desired - len(str)) / len(padder))):
			padding += padder
		if from_start:
			return padding + str
		else:
			return str + padding
	
	def start(self):
		html = self.__fetch_content()
		result = self.__sort(self.__analysis(html))
		self.__print_rank_table(result)

clawer = Clawer()
clawer.start()
