# -*- coding: utf-8 -*-

'统计一个项目的commits、added lines及final lines'

__author__ = "Jason Zhao <guojiongzhao@139.com>"

import os
import sys
import logging
# 需要先执行pip install chardet进行安装
import chardet
import config

# 项目类
class Project(object):
	logger = None

	# 本地git代码库的根目录
	__git_root = os.path.join(".", "git")

	# 统计final lines的文件扩展名（即只统计这些扩展名文件的代码行数）
	# 之所以为公共变量，是因为其他文件需要知道这些扩展名，而且通过类就可以拿到这些扩展名，而不需先实例化一个对象才能拿到（所以没有设计set_xxx方法）
	# 每增加一个新的扩展名，就需要修改codestat.FinalLinesStat.__print_oneline方法
	code_file_ext = [
		# Java项目
		".java", 
		# 仓库项目
		".sh", ".sql", ".job", 
		# 前端项目
		".htm", ".html", ".css", ".less", ".js", ".ts", ".vue", 
		# Python项目
		".py", 
		#C/C++项目
		".c", ".cpp", ".h", 
		# Scala项目
		".scala", 
		# 配置及其它文件
		".properties", ".md", ".xml", ".yml", ".bat", ".json"]

	# 分隔符
	# author中name与email之间的分隔符，例如：zhaoguojiong <zhaoguojiong@xueleyun.com>
	__SEP_AUTHOR_NAME_EMAIL = ' '
	# author中email的开始、结束标志字符，例如：zhaoguojiong <zhaoguojiong@xueleyun.com>
	__SEP_AUTHOR_EMAIL_BEGIN = '<'
	__SEP_AUTHOR_EMAIL_END = '>'
	# git log --pretty=tformat: 输出文件中各列之间的分隔符，例如：
	# 04281db86b16393ceb3968219426189b9a30c007||霍伟伟 <huoweiwei@xueleyun.com>||2017-12-29T19:16:09+08:00
	__SEP_GIT_LOG_COLUMN = '||'

	# final_lines_stat{}中的特殊key
	# 之所以为公共变量，是因为其他文件需要使用，而且通过类就可以拿到该变量。
	FINAL_LINES_TOTAL = "total" # 所有扩展名的final lines总和
	FINAL_LINES_OTHERS = "others" # 除了code_file_ext[]的其它扩展名的final lines总和。

	# 构造函数
	# git_host: git服务器的地址，例如："git@git.xuelebj.net:xueleapp/classroom.git"中的git.xuelebj.net
	# group_name: git项目组的名称
	# proj_name: git项目的名称
	def __init__(self, git_host, group_name, proj_name):
		self.__git_host = git_host
		self.__group_name = group_name
		self.__proj_name = proj_name

		# 默认不需要更新本地代码，不需要重新生成git log文件，不保留author原始格式
		self.__update_codes_needed = False
		self.__create_log_needed = False
		self.__original_author = False

		# 如果本地git根目录不存在， 则先创建目录
		if not os.path.exists(self.__git_root):
			os.mkdir(self.__git_root)
		
		# 先检查git项目在本地是否已经存在，如果不存在，则先克隆项目
		if not (self.__proj_name in os.listdir(self.__git_root)):
			self.__git_clone()
			# 如果克隆了新项目，则必须更新代码，生成log文件
			self.__update_codes_needed = True
			self.__create_log_needed = True

		# 获取项目的根目录
		self.__proj_root = os.path.join(self.__git_root, self.__proj_name)
		if not os.path.exists(self.__proj_root):
			self.logger.error("%s is not existed" % self.__proj_root)
			return

		# 整个项目的commits和added lines，数组结构，第1个元素为最后更新的branch，第2个元素为added lines，第3个元素为commits
		self.__proj_stat = []
		# 每个人的commit数和added lines，dict类型，key为author，value为一个数组，第1个元素为最后更新的branch，第2个元素为该人的added lines，第3个元素为该人的commits
		self.__author_stat = {}
		# 整个项目的最终代码行数，dict类型，key为代码文件的扩展名，value为最终代码行数
		self.__final_lines_stat = {}

		# 不规范的author列表，key为不规范的author，value为一个list，0是规范的author，1是最近的commit时间
		self.__abnormal_authors = {}
		# 跳过的文件清单，key为文件名称，value为跳过的原因
		self.__skipped_files = {}
		# 编码不是utf-8的文件清单，key为文件名称，value为实际编码格式
		self.__not_utf8_files = {}
		# 读取错误的文件清单，key为文件名称，value为错误原因
		self.__error_files = {}

	# 获取project名称
	def get_proj_name(self):
		return self.__proj_name

	# 设置是否需要更新代码
	def set_update_codes_need(self, value: False):
		# self.__update_codes_needed默认是False，如果在__init__()时被改为了True（当需要克隆项目时），则本set方法的逻辑不执行。
		if not self.__update_codes_needed:		
			self.__update_codes_needed = value

	# 设置是否生成log文件
	def set_create_log_needed(self, value: False):
		# self.__create_log_needed默认是False，如果在__init__()时被改为了True（当需要克隆项目时），则本set方法的逻辑不执行。
		if not self.__create_log_needed:
			self.__create_log_needed = value

	# 设置是否保留author的原始格式
	def set_original_author(self, value: False):
		self.__original_author = value

	# 返回保存整个项目的commits和added lines统计结果的proj_stat{}
	def get_proj_stat(self):
		return self.__proj_stat

	# 返回保存每个人的commits和added lines统计结果的author_stat{}
	def get_author_stat(self):
		return self.__author_stat

	# 返回保存final lines统计结果的final_lines_stat{}
	def get_final_lines_stat(self):
		return self.__final_lines_stat
	
	# 返回不规范的author清单
	def get_abnormal_authors(self):
		return self.__abnormal_authors

	# 返回跳过的文件清单
	def get_skipped_files(self):
		return self.__skipped_files

	# 返回非utf-8编码的文件清单（但也解析成功了）
	def get_not_utf8_files(self):
		return self.__not_utf8_files

	# 返回读取错误的文件名单
	def get_error_files(self):
		return self.__error_files
	
	# 克隆git项目
	def __git_clone(self):
		self.logger.info("git cloning...")

		# 构建git命令行
		cmd_cd = 'cd %s' % self.__git_root
		cmd_git_clone = 'git clone git@%s:%s/%s.git' % (self.__git_host, self.__group_name, self.__proj_name)
		cmd = '%s && %s' % (cmd_cd, cmd_git_clone) 
		self.logger.debug(cmd)

		# 执行git命令行
		result = os.system(cmd)
		self.logger.debug("command return: %s", result)

	# git pull最新代码
	def __git_pull(self, branch):
		self.logger.info("git pulling...")

		# 构建git命令行
		cmd_cd = "cd %s" % self.__proj_root
		cmd_git_checkout = "git checkout %s" % branch
		cmd_git_pull = "git pull"
		cmd = "%s && %s && %s" % (cmd_cd, cmd_git_checkout, cmd_git_pull) 
		self.logger.debug(cmd)

		# 执行git命令行
		result = os.system(cmd)
		self.logger.debug("command return: %s", result)

	# git checkout分支
	def __git_checkout(self, branch):
		self.logger.info("git checkouting...")

		# 构建git命令行
		cmd_cd = "cd %s" % self.__proj_root
		cmd_git_checkout = "git checkout %s" % branch
		cmd = "%s && %s" % (cmd_cd, cmd_git_checkout) 
		self.logger.debug(cmd)

		# 执行git命令行
		result = os.system(cmd)
		self.logger.debug("command return: %s", result)

	# git fetch最新代码
	def __git_fetch(self):
		self.logger.info("git fetching...")

		# 构建git命令行
		cmd_cd = "cd %s" % self.__proj_root
		cmd_git_fetch = "git fetch origin"
		cmd = "%s && %s" % (cmd_cd, cmd_git_fetch) 
		self.logger.debug(cmd)

		# 执行git命令行
		result = os.system(cmd)
		self.logger.debug("command return: %s", result)

	# 获取git_log_stat_***.txt文件名称（不含路径）
	def __get_git_log_stat_filename_without_path(self):
		# 构建git_log_stat_***.txt文件名称
		return "git_log_stat_%s_%s.txt" % (self.__since, self.__before)

	# 获取git_log_stat_***.txt文件名称（含路径）
	def __get_git_log_stat_filename_with_path(self):
		# 获得git_log_stat_***.txt文件名称（不含路径）
		filename = self.__get_git_log_stat_filename_without_path()
		# 返回文件名称（含路径）
		return os.path.join(self.__proj_root, filename)

	# 执行git log --stat命令，生成commit统计文件，包含每一次commit的author、date、及代码行数变更统计
	def __create_git_log_stat_file(self):
		self.logger.info("git logging...")

		# 构建git_log_stat_***.txt文件名称
		filename = self.__get_git_log_stat_filename_without_path()

		# 构建统计提交代码行数的git log --stat命令行
		cmd_cd = "cd %s" % self.__proj_root
		cmd_git_log = "git log --pretty=tformat:\"%%H%s%%an <%%ae>%s%%aI\" --stat --since=%s --before=%s --all > \"%s\"" % \
		(self.__SEP_GIT_LOG_COLUMN, self.__SEP_GIT_LOG_COLUMN, self.__since, self.__before, filename)
		cmd = "%s && %s" % (cmd_cd, cmd_git_log) 
		self.logger.debug(cmd)

		# 执行git命令行
		result = os.system(cmd)
		self.logger.debug("command return: %s", result)

	# 从author中解析出email，并转换为规范的email
	# author格式为：zhaoguojiong <zhaoguojiong@xueleyun.com>
	def __normalize_author_email(self, author, datetime):
		# 截取出原始的email
		author_email = author.split(self.__SEP_AUTHOR_EMAIL_BEGIN)[1].strip(self.__SEP_AUTHOR_EMAIL_END)
		self.logger.debug("split email: %s.", author_email)

		if author_email in config.author_mapping:
			new_author = config.author_mapping.get(author_email)
			# 添加到abnormal_authors{}中
			if author_email in self.__abnormal_authors:
				# 取出已经添加的commit时间
				last_datetime = self.__abnormal_authors[author_email][1]
				# 如果这次的时间更新，则更新时间
				if datetime > last_datetime:
					self.__abnormal_authors[author_email][1] = datetime
			else:
				self.__abnormal_authors[author_email] = [new_author, datetime]
			self.logger.debug("Notice: %s --> %s, commit date: %s", author_email, new_author, datetime)
		else:
			new_author = author_email

		return new_author

	# 获取最近更新的branch（暂时没有办法，返回"unknown"）
	def __get_latest_branch(self):
		return "unknown"

	# 解析git_log_stat_***.txt文件，统计整个项目的added lines、commits，及每个人的added lines、commits，保存到类的实例变量中（proj_stat[]和author_stat{})。
	def __parse_git_log_stat_file(self):
		# 获取文件名称（含路径）
		filename = self.__get_git_log_stat_filename_with_path()

		self.logger.debug("parsing %s", filename)
		total_lines = 0
		total_commits = 0

		# 读取git_log_stat_***.txt文件，一次commit记录的内容格式为：
		# c3c867c8a146d9c3fe1dfb3284c6fcb237f95467||zhouming <zhouming@xueleyun.com>||2017-12-28T18:22:28+08:00
		#
		#  .../dm_recomm_book_bottom_kp_schedule.sh           |  4 +-
		#  .../dm_recomm_book_bottom_kp_schedule.sql          | 94 +++++++++++++++++++++-
		#  .../dm_recomm_book_bottom_unit_schedule.sql        | 19 ++++-
		#  3 files changed, 108 insertions(+), 9 deletions(-)	
		with open(filename, "r", encoding="utf-8") as f:
			author = ""
			commit = ""

			try:
				for line in f:
					line = line.strip("\n")
					self.logger.debug("reading a line: %s.", line)
					
					# 处理commit行
					if self.__SEP_GIT_LOG_COLUMN in line:
						# 截取出commit id、author和datetime
						commit = line.split(self.__SEP_GIT_LOG_COLUMN)[0]
						author = line.split(self.__SEP_GIT_LOG_COLUMN)[1]
						datetime = line.split(self.__SEP_GIT_LOG_COLUMN)[2]

						# 保留原样的author格式
						if self.__original_author:
							new_author = author
						else:
							# 转换为规范的author email
							new_author = self.__normalize_author_email(author, datetime)

						# 累加该人的commits，更新到author_stat{}中
						if new_author in self.__author_stat:
							# value是一个数组，[2]是commits
							self.__author_stat[new_author][2] += 1
						else:
							branch = self.__get_latest_branch()
							# 0是added lines（此行中只有commit，没有added lines），1是commits
							self.__author_stat[new_author] = [branch, 0, 1]

						# 累加该项目的commits
						total_commits += 1
					# 处理lines行
					elif "changed" in line and ("insertion" in line or "deletion" in line):
						self.logger.debug("parsing: %s.", line)
						# 可能有三种格式：
						# 1： 3 files changed, 39 insertions(+), 106 deletions(-)
						# 2： 1 file changed, 18 deletions(-)
						# 3： 1 file changed, 4 insertions(+)
						insertions = line.split(", ")[1]
						if "insertion" in insertions:
							insertions = insertions.split(" ")[0]
						else:
							insertions = 0
						self.logger.debug("split insertions: %s.", insertions)
						lines = int(insertions)

						# 累加该人的lines，更新到author_stat{}中
						if new_author in self.__author_stat:
							# value是一个数组，[1]是added lines
							self.__author_stat[new_author][1] += lines
						# 该else分支应该不会出现，当拿到added lines时，该author已经存在于author_stat中了（随着第一个commit）
						else:
							self.logger.warn('异常：没有commit，就有了added lines')
							branch = self.__get_latest_branch()							
							self.__author_stat[new_author] = [branch, lines, 1]

						# 累加该项目的lines
						total_lines += lines
			except Exception as e:
				self.logger.error(e)

		# 将该项目的统计结果添加到proj_stat{}中
		if total_commits > 0:
			branch = self.__get_latest_branch()
			self.__proj_stat = [branch, total_lines, total_commits]

		self.logger.info("total added lines: %s, total commits: %s, total authors: %s",
			total_lines, total_commits, len(self.__author_stat))

	# 统计整个项目的commits和added lines，保存到类的实例变量中
	# 统计结果不空时，返回True；否则，返回False
	def stat_commits(self, since, before):
		self.__since = since
		self.__before = before

		# 如果需要更新代码，先执行git fetch操作，用于后续的统计所有分支的commits和added lines
		if self.__update_codes_needed:
			self.__git_fetch()

		# 如果需要重新生成git log文件，则执行git log操作
		if self.__create_log_needed:
			self.__create_git_log_stat_file()

		# 解析文件，统计commits和added lines，输出到2个实例变量中
		self.__parse_git_log_stat_file()

		return not (self.__proj_stat == [])

	# 递归统计给定目录下的文件行数，返回predefined_ext和undefined_ext。
	# predefined_ext为一个dict结构，key为预定义的文件扩展名（即存在于code_file_ext中的扩展名），value为final lines。
	#   但是，所有的未定义的扩展名，也会作为一个统一的“others”扩展名（一个key），也计入到此dict中
	# undefined_ext为一个dict结构，key为未定义的文件扩展名，value为final lines
	# skipped_files为一个数组结构，保存跳过的文件列表
	# error_files为一个数组结构，保存read文件有异常的文件列表
	def __count_lines(self, path, predefined_ext, undefined_ext, level):
		# 最多显示3层目录的提示信息（项目根目录为第1层目录）
		if level <= 2:
			self.logger.info('counting final lines: %s', path)

		for file in os.listdir(path):
			# 获得完整路径
			file_path = os.path.join(path, file)

			# 跳过一些目录或文件
			if file in config.skipped_path:
				# 添加到成员变量skipped_files{}中
				self.__skipped_files[file_path] = 'path is matched'
				self.logger.debug("%s is skipped.", file)
				continue

			# 如果是目录，则继续递归
			if os.path.isdir(file_path):
				level += 1
				self.__count_lines(file_path, predefined_ext, undefined_ext, level)
				level -= 1
				continue

			# 获取文件扩展名（转换为小写）
			ext = os.path.splitext(file)[1].lower()

			# 跳过一些扩展名（精确匹配）
			if ext in config.skipped_file_ext:
				# 添加到成员变量skipped_files{}中
				self.__skipped_files[file_path] = 'ext is matched'
				self.logger.debug("%s is skipped, because ext: %s", file, ext)
				continue

			# 统计文件行数
			# 先尝试以utf-8读取文件，如果有异常再去获取文件编码、再次读取。
			# 因为获取文件编码的耗时较长，而绝大多数文件都是utf-8编码，所以采取此优化策略
			file_lines = 0
			codec = "utf-8"
			read_error = False
			try:
				with open(file_path, "r", encoding = codec) as f:
					for l in f:
						file_lines += 1
				self.logger.debug("%s: %d final lines. [%s]", file_path, file_lines, codec)
			except Exception as e:
				read_error = True
				self.logger.debug(e)

			# 读文件异常时，最大可能是编码问题，此时获取文件编码（耗时较长）
			if read_error:
				# 获得文件编码格式
				codec = ""
				try:
					with open(file_path, "rb") as f:
						data = f.read()
					result = chardet.detect(data)
					codec = result["encoding"]
					# 添加到成员变量not_utf8_files{}中
					self.__not_utf8_files[file_path] = 'codec: ' + codec
					self.logger.debug("file: %s, detected encoding: %s", file_path, codec) 
				except Exception as e:
					self.logger.debug(e)

				# 获取编码失败，记录到error_files[]中，然后跳过
				if codec == "":
					# 添加到成员变量error_files{}中
					self.__error_files[file_path] = 'codec is ""' 
					self.logger.debug("file: %s, error ocurred when detect encoding, just skipped.", file_path)
					continue

				# 未获取到编码（可能是二进制文件），记录到skipped_files[]中，然后跳过
				if codec is None:
					# 添加到成员变量error_files{}中
					self.__error_files[file_path] = 'codec is None(binary?) '
					self.logger.debug("file: %s, encoding is None (binary?), just skipped.", file_path)
					continue

				# chardet似乎有bug，有些js文件检测结果为Windows-1254，但实际为utf-8，所以在此做一个修正
				original_codec = codec
				if codec == "Windows-1254":
					codec = "utf-8"
					# 添加到成员变量not_utf8_files{}中
					self.__not_utf8_files[file_path] = original_codec + ' --> ' + codec
					self.logger.debug("file: %s, encoding %s --> %s.", file_path, original_codec, codec)

				# 再次读取文件
				try:
					with open(file_path, "r", encoding = codec) as f:
						for l in f:
							file_lines += 1
					self.logger.debug("%s: %d final lines. [%s]", file_path, file_lines, codec)
				except Exception as e:
					# 添加到成员变量error_files{}中
					self.__error_files[file_path] = str(e)
					self.logger.debug(e)
					continue

			# 如果扩展名是预定义的，则按原扩展名分类统计；否则，统一计入到“others”类别中
			if not (ext in self.code_file_ext):
				if not (ext in undefined_ext):
					undefined_ext[ext] = file_lines
				else:
					undefined_ext[ext] += file_lines
				self.logger.debug("undefined ext: %s, file: %s", ext, file_path)
				ext = self.FINAL_LINES_OTHERS

			predefined_ext[ext] += file_lines

	# 统计final lines，保存到类的实例变量中
	def stat_final_lines(self):
		# 如果需要更新代码，先执行git pull操作（pull master分支的代码）
		if self.__update_codes_needed:
			self.__git_pull("master")
		# 切换到master分支
		else:
			self.__git_checkout("master")

		# 初始化要返回的predefined_ext{}、undefined_ext{}、skipped_file[]和error_files[]
		predefined_ext = {self.FINAL_LINES_TOTAL: 0, self.FINAL_LINES_OTHERS: 0}
		for e in self.code_file_ext:
			predefined_ext[e] = 0
		undefined_ext = {}

		# 统计该项目下的final lines
		level = 0
		self.__count_lines(self.__proj_root, predefined_ext, undefined_ext, level)

		# 计算所有ext的lines的总和（不包含未定义扩展名的lines）
		for e in predefined_ext:
			if not (e in [self.FINAL_LINES_TOTAL, self.FINAL_LINES_OTHERS]):
				predefined_ext[self.FINAL_LINES_TOTAL] += predefined_ext[e]

		# 保存到类的实例变量中
		self.__final_lines_stat = predefined_ext

		# 打印统计结果（过滤掉行数为0的ext）
		lines_stat = {}
		for e in self.__final_lines_stat:
			lines = self.__final_lines_stat[e]
			if lines > 0:
				lines_stat[e] = lines
		self.logger.info('final_lines_stat{}: %s', lines_stat)

		# 打印undefined_ext{}
		if len(undefined_ext) > 0:
			self.logger.info("%s (undefined ext): %s", self.FINAL_LINES_OTHERS, undefined_ext)
		# 打印跳过的文件数量、读取失败的文件数量
		self.logger.info("skipped files: %d, not utf-8 files: %d, error files: %d", 
		len(self.__skipped_files), len(self.__not_utf8_files), len(self.__error_files))

if __name__ == "__main__":
	# 获得logger实例
	logger = logging.getLogger()
	# 设置日志格式
	formatter = logging.Formatter("%(levelname)s %(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S")
	# 设置控制台日志处理器
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(formatter)
	# 为logger添加日志处理器（同时console输出和文件输出）
	logger.addHandler(console_handler)
	# 设置日志级别
	logger.setLevel(logging.INFO)

	Project.logger = logger
	proj = Project('git.xuelebj.net','xueleapp','classroom')
	proj.stat_commits('2018-01-01', '2018-02-01')
	proj.stat_final_lines()