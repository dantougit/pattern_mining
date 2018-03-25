#!/usr/bin/env python
# -*- coding:UTF-8 -*-
"""author : haozhuolin
   date : 20171116
"""

import sys
import re
import copy
from collections import defaultdict

import numpy as np

reload(sys)
sys.setdefaultencoding("utf-8")


class RegularMining(object):
    def __init__(self, reg):
        self.reg_handle(reg)

    def reg_handle(self, reg):
        """regular pattern handle
        """
        self.reg_old = re.compile(reg)
        reg_pattern = "(.*)".join(["(%s)" % i.strip("()")
                                   for i in re.split(r"\.\*|\.\{[\d,]+\}", reg)])
        reg_new = re.compile("(.*)%s(.*)" % reg_pattern)
        self.reg_new = reg_new

    def load_data(self):
        """load mining data
        """
        self.mining_data = []
        with open("../data/frequent_mining_data") as fi:
            for line in fi:
                words = line.strip().split(" ")
                self.mining_data.append(words)

    def entropy(self, cnt1, cnt2):
        """compute entropy
        """
        p = 1.0 * cnt1 / (cnt1 + cnt2)
        return -(p * np.log(p) + (1 - p) * np.log(1 - p))

    def gen_information_gain(self):
        """generate word information_gain
        """
        word_cnt = defaultdict(int)
        other_word_cnt = defaultdict(int)
        count = [0, 0]
        for words in self.mining_data:
            line = "".join(words)
            words = set(words)
            if not line:
                continue
            if self.reg_old.search(line):
                for word in words:
                    word_cnt[word] += 1
                count[0] += 1
            else:
                for word in words:
                    other_word_cnt[word] += 1
                count[1] += 1

        self.diff = {}
        for word, cnt in word_cnt.iteritems():
            other_cnt = other_word_cnt[word]
            prop = 1.0 * (cnt + other_cnt) / (count[0] + count[1])
            if other_cnt != 0 and count[0] != cnt:
                # 信息增益
                # self.diff[word] = self.entropy(count[0], count[1]) - (prop * self.entropy(cnt, other_cnt) + (1 - prop) * self.entropy(count[0] - cnt, count[1] - other_cnt))
                # 信息增益比
                # self.diff[word] = (self.entropy(count[0], count[1]) - (prop * self.entropy(cnt, other_cnt) + (1 - prop) * self.entropy(
                #    count[0] - cnt, count[1] - other_cnt))) / self.entropy(cnt + other_cnt, count[0] + count[1] - cnt - other_cnt)
                # idf比值
                # self.diff[word] = np.log(1.0 * count[1] / other_cnt) / np.log(1.0 * count[0] / cnt)
                # 点互信息
                self.diff[word] = np.log((1.0 * cnt / (count[0] + count[1])) / \
                                   (1.0 * count[0] / (count[0] + count[1])) /
                                   (1.0 * (cnt + other_cnt) / (count[0] + count[1])))

    def pattern_minning(self):
        self.res = {}
        for words in self.mining_data:
            line = "".join(words)
            match = self.reg_old.search(line)
            if not match:
                continue
            match = self.reg_new.match(line)
            blocks = list(match.groups())
            self.add_one(words, blocks)
            self.same_num(words, blocks)
        self.sort_res = sorted(
            self.res.items(), key=lambda d: d[1][0], reverse=True)

    def add_one(self, words, blocks):
        for word in words:
            range0 = range(0, len(blocks), 2)
            for j in range0:
                blocks_copy = copy.copy(blocks)
                for k in range0:
                    blocks_copy[k] = ""
                if word in blocks[j]:
                    blocks_copy[j] = word
                    new_reg = ".*".join([r for r in blocks_copy if r])
                    if new_reg not in self.res:
                        self.res[new_reg] = [self.diff.get(word, 0), 0, word]
                    self.res[new_reg][1] += 1

    def same_num(self, words, blocks):
        for word in words:
            range0 = range(0, len(blocks), 2)
            range1 = range(1, len(blocks), 2)
            for i in range1:
                for j in range0:
                    blocks_copy = copy.copy(blocks)
                    blocks_copy[i] = ""
                    for k in range0:
                        blocks_copy[k] = ""
                    if word in blocks[j]:
                        blocks_copy[j] = word
                        new_reg = ".*".join([r for r in blocks_copy if r])
                        if new_reg not in self.res:
                            self.res[new_reg] = [
                                self.diff.get(word, 0), 0, word]
                        self.res[new_reg][1] += 1

    def main(self):
        self.load_data()
        self.gen_information_gain()
        self.pattern_minning()


if __name__ == "__main__":
    """输入一个正则，拓展更多的正则
    """
    reg = '带来.*客户'
    rm = RegularMining(reg)
    rm.main()

    for new_reg_count in rm.sort_res:
        new_reg, count = new_reg_count
        if count[1] > 10:
            print "%s\t%s\t%s\t%s\t%s" % (
                reg, count[2], count[0], new_reg, count[1])
