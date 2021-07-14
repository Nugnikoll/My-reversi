import time
import os
import sys
import argparse
import numpy as np
import signal

import data

sys.path.append("../python")
import reversi as rv

parser = argparse.ArgumentParser(description = "generate training samples for reversi program")
parser.add_argument("--num-simulate", type = int, default = 10000, help = "number of random self-play games (default: 10000)")
parser.add_argument("--path-train", type = str, default = "./train.dat", help = "path to save training data (default: ./train.dat)")
parser.add_argument("--path-pattern", type = str, default = "", help = "generate target with old pattern and specify the path to find it")
parser.add_argument("--search-depth", type = int, default = 4, help = "the depth to search to evaluate each sample (default: 4)")
parser.add_argument("--play-depth", type = int, default = 0, help = "evaluate sample by costly play-out instead of a single search (default: 0)")
args = parser.parse_args()

mthd = rv.mthd_ab | rv.mthd_kill | rv.mthd_pvs | rv.mthd_mtdf

rv.board.config()
rv.pattern.config()

name = args.path_train

if not os.path.exists(name):
	sample, target, play_cnt, play_score = None, None, None, None
else:
	with open(name, "rb") as fobj:
		sample, target, play_cnt, play_score = data.load_npy_list(
			fobj,
			("sample", "target", "play_cnt", "play_score")
		)

if not sample is None:
	print("sample exists")
else:
	print("generate sample")
	time_begin = time.time()
	sample = rv.sample_gen_select(args.num_simulate)
	time_end = time.time()
	print("time: ", time_end - time_begin)
	with open(name, "wb") as fobj:
		data.dump_npy_list(fobj, ("sample"), sample)

print("sample shape", sample.shape)

if os.path.exists(args.path_pattern):
	rv.pattern.config(args.path_pattern)
	mthd = mthd | rv.mthd_ptn

if not target is None:
	print("target exists")
else:
	print("generate target")
	time_begin = time.time()
	rv.board.clear_hash()
	target = rv.evaluate(sample, mthd, args.search_depth, True)
	time_end = time.time()
	print("time: ", time_end - time_begin)

	def modify(head):
		head["append"][1]["search_depth"] = args.search_depth
		head["append"][1]["search_mthd"] = mthd

	with open(name, "wb") as fobj:
		data.dump_npy_list(
			fobj, ("sample", "target"),
			sample, target,
			modify_head = modify,
		)

print("target shape", target.shape)

flag_int = False
def on_interrupt(signum, frame):
	global flag_int
	flag_int = True

if args.play_depth:
	size = sample.shape[0]
	if not play_cnt is None and not play_score is None:
		print("play_cnt and play_score exists")
	else:
		play_cnt = np.zeros((size,), dtype = np.int32)
		play_score = np.zeros((size,), dtype = np.float32)

	max_cnt = play_cnt.max()
	min_cnt = play_cnt.min()
	if max_cnt == min_cnt:
		max_cnt += 1

	time_begin = time.time()
	rv.board.clear_hash()
	handler_save = signal.signal(signal.SIGINT, on_interrupt)
	for i in range(size):
		if flag_int:
			break
		cnt = play_cnt[i]
		for j in range(cnt, max_cnt):
			if flag_int:
				break
			print("i:", i)
			brd = rv.board(int(sample[i, 0]), int(sample[i, 1]))
			brd._print()
			brd.play_out(mthd, True, args.play_depth)
			brd._print()
			score = brd.score_end(True)
			print("score:", score)
			print()
			play_score[i] = (play_score[i] * cnt + score) / (cnt + 1)
			cnt = cnt + 1
		play_cnt[i] = cnt
	time_end = time.time()
	print("time: ", time_end - time_begin)

	def modify(head):
		head["append"][1]["search_depth"] = args.search_depth
		head["append"][1]["search_mthd"] = mthd
		head["append"][3]["search_depth"] = args.play_depth
		head["append"][3]["search_mthd"] = mthd

	with open(name, "wb") as fobj:
		data.dump_npy_list(
			fobj,
			("sample", "target", "play_cnt", "play_score"),
			sample, target, play_cnt, play_score,
			modify_head = modify,
		)

	signal.signal(signal.SIGINT, handler_save)
