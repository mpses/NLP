#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://github.com/matsu0228/nlp-jp/blob/master/lib/jp_parser.py

import MeCab
import CaboCha
import os, sys, csv, subprocess, better_exceptions
from collections import namedtuple, defaultdict
from preprocessing import preprocessing

def read_file_into_lines(file_name):
    with open(file_name, "r") as f:
        return f.readlines()

def import_inui_dict():
    polar_dict = defaultdict(lambda: 0)

    into_value = {"ポジ": 1, "ネガ": -1}
    for l in read_file_into_lines("dict/wago.121808.pn"):
        line_list = l.split("\t")
        polar_dict[line_list[1].split(" ")[0].strip()] = into_value[line_list[0][:2]]

    into_value = defaultdict(lambda: 0)
    into_value["p"], into_value["n"], into_value["e"] = 1, -1, 0
    for l in read_file_into_lines("dict/pn.csv.m3.120408.trim"):
        line_list = l.split("\t")
        polar_dict[line_list[0]] = into_value[line_list[1]]
    
    del polar_dict[""]
    del polar_dict["だ"]

    return polar_dict

NEologD_pass = f"{subprocess.run(['mecab-config', '--dicdir'], encoding = 'utf-8', stdout = subprocess.PIPE).stdout.strip()}/mecab-ipadic-neologd"
# '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'

class JpParser:
    POS_DIC = {
        'BOS/EOS': 'EOS', # end of sentense
        '形容詞' : 'ADJ',
        '連体詞' : 'JADJ', # Japanese-specific POS like a adjective
        '副詞'   : 'ADV',
        '名詞'   : 'NOUN',
        '動詞'   : 'VERB',
        '助動詞' : 'AUX',
        '助詞'   : 'PART',
        '感動詞' : 'INTJ',
        '接続詞' : 'CONJ',
        '記号'   : 'SYM', # symbol
        '*'      : 'X',
        'その他' : 'X',
        'フィラー': 'X',
        '接頭詞' : 'X',
    }
    POS_2ND_DIC = {
        '代名詞':'PRON',
    }

    def __init__(self, sys_dic_path = NEologD_pass):
        opt_m = "-Ochasen"
        opt_c = '-f4'
        if sys_dic_path:
            opt_m += ' -d {0}'.format(sys_dic_path)
            opt_c += ' -d {0}'.format(sys_dic_path)
        tagger = MeCab.Tagger(opt_m)
        tagger.parse('') # for UnicodeDecodeError
        self._tagger = tagger
        self._parser = CaboCha.Parser(opt_c)
        self.pol_dic = import_inui_dict()

    def search_politely_dict(self, words):
        return {word: self.pol_dic[word] for word in words}

    def get_sentences(self, text):
        """ 
        input: text have many sentences
        output: ary of sentences ['sent1', 'sent2', ...]
        """
        EOS_DIC = ['。', '．', '！', '？', '!?', '!', '?']
        sentences = []
        sent = ''
        # split in first when text include '\n'
        temp = text.split('\\n')
        for each_text in temp:
            if each_text == '':
                continue
            for token in self.tokenize(preprocessing(each_text)):
                # print(token.pos_jp, token.pos, token.surface, sent)
                # TODO: this is simple way. ex)「今日は雨ね。」と母がいった
                sent += token.surface
                if token.surface in EOS_DIC and sent:
                    sentences.append(sent)
                    sent = ''
            if sent:
                sentences.append(sent)
        return sentences

    def tokenize(self, sent):
        node = self._tagger.parseToNode(sent)
        tokens = []
        idx = 0
        while node:
            feature = node.feature.split(',')
            token = namedtuple('Token', 'idx, surface, pos, pos_detail1, pos_detail2, pos_detail3,\
                                infl_type, infl_form, base_form, reading, phonetic')
            token.idx         = idx
            token.surface     = node.surface  # 表層形
            token.pos_jp      = feature[0]    # 品詞
            token.pos_detail1 = feature[1]    # 品詞細分類1
            token.pos_detail2 = feature[2]    # 品詞細分類2
            token.pos_detail3 = feature[3]    # 品詞細分類3
            token.infl_type   = feature[4]    # 活用型
            token.infl_form   = feature[5]    # 活用形
            token.base_form   = feature[6] if feature[6] != '*' else node.surface # 原型 ex) MacMini's base_form == '*'
            token.pos         = self.POS_DIC.get( feature[0], 'X')     # 品詞
            token.reading     = feature[7] if len(feature) > 7 else ''  # 読み
            token.phonetic    = feature[8] if len(feature) > 8 else ''  # 発音
            # for BOS/EOS
            if token.pos != 'EOS':
                tokens.append(token)
                idx += 1
            node = node.next
        return tokens

    def tokenize_filtered_by_pos(self, sent, pos = ['NOUN']):
        tokens = [token for token in self.tokenize(sent) if token.pos in pos]
        return tokens

    def extract_words(self, text, filter_pos = []):
        if filter_pos:
            return [w.surface for w in self.tokenize(text) if not w.pos in filter_pos]
        else:
            return [w.surface for w in self.tokenize(text)]

    def get_chunk_data(self, sentence):
        tree = self._parser.parse(sentence)
        chunk_data = []
        for i in range(tree.chunk_size()):
            chunk = namedtuple('Chunk', 'tokens, head_token, chunk_idx, depend_idx, src_idx, head_idx, func_idx,\
                                token_size, token_idx, feature_size, score, additional_info')
            c = tree.chunk(i)
            c_tokens = []
            for j in range(c.token_pos, c.token_pos + c.token_size):
                c_tokens.append(tree.token(j))
            chunk.tokens       = c_tokens
            chunk.head_token   = c_tokens[c.head_pos] # 主辞のtoken
            chunk.chunk_idx    = i                    # chunk_index
            chunk.depend_idx   = c.link               # dependecy chunk index
            chunk.src_idx      = []                   # source chunk (recieve chunk) index
            chunk.head_idx     = c.head_pos           # 主辞のindex
            chunk.func_idx     = c.func_pos           # 機能語のindex
            chunk.token_size   = c.token_size
            chunk.token_idx    = c.token_pos          # chunk先頭tokenのindex
            chunk.feature_size = c.feature_list_size
            chunk.score        = c.score
            chunk.additional_info = c.additional_info
            chunk_data.append(chunk)
        for i in range(tree.chunk_size()):
            c = tree.chunk(i).link
            if c != -1:
                chunk_data[c].src_idx.append(i)
        return chunk_data

    def get_child_tokens(self, chunks, chunk, token):
        child_tokens = []
        # a non head_token have no child (return empty list)
        if token.idx == chunk.head_token.idx:
            child_tokens.extend([t for t in chunk.tokens if t.idx != token.idx])
            if chunk.src_idx:
                child_tokens.extend([chunks[si].head_token for si in chunk.src_idx])
        return child_tokens


    def debug(self, sentence):
        tree = self._parser.parse(sentence)
        # 0: tree format
        print(tree.toString(0))
        # 4: CONLL format
        print(tree.toString(4))

    # return senti_word_list
    def senti_tokenize(self, sentence):
        senti_tokens = {'pos': [], 'nue': [], 'neg': []}
        words = [s.base_form.lower()
                    for s in self.tokenize(sentence)
                    if s.base_form != '*' and s.pos != 'SYM']
        politely_dict = self.search_politely_dict(words)
        for w, score in politely_dict.items():
            key = 'pos' if int(score) > 0 else 'nue' if int(score) == 0 else 'neg'
            senti_tokens[key].append(w)
        return senti_tokens

    def senti_analisys(self, sentence):
        """
        output: sentiment score (1: positive < score < -1: negative)
        """
        score = num_all_words = 0
        tokens = self.tokenize(sentence)
        words = []
        words.extend([s.base_form.lower() for s in tokens])
        politely_dict = self.search_politely_dict(words)
        # politely_dict = bulk_search_for_politely_dict(words, suffix = '_JP')
        scores = []
        scores.extend([politely_dict[w] for w in words])
        for i in range(len(tokens)):
            scores = self.apply_muliwords_rule_for_senti_analisys(i, tokens, scores)
            scores = self.apply_politely_reverse_rule_for_senti_analisys(i, tokens, scores, sentence)
        # evaluate score
        # -------------------------------------------------------------------
        for sc in scores:
            score += sc
            num_all_words += 1
        return round(score / num_all_words, 2)

    def apply_politely_reverse_rule_for_senti_analisys(self, i, tokens, scores, sentence):
        # ref) https://www.anlp.jp/proceedings/annual_meeting/2013/pdf_dir/C6-1.pdf
        reverse_multiwords = [
            # headword, N-gram, apply_type
            ['の で は ない', 3, 'own'],
            ['わけ で は ない', 3, 'own'],
            ['わけ に は いく ない', 4, 'src'],
        ]
        reverse_words = [
            # headword, pos, apply_type
            ['ない', 'AUX', 'own'],
            ['ぬ', 'AUX', 'own'],
            ['ない', 'ADJ', 'own'],
        ]
        apply_type = ''
        # detect politely-reverse word ( like a 'not' )
        # -------------------------------------------------------------------
        for r in reverse_words:
            if tokens[i].base_form ==r[0] and tokens[i].pos == r[1]: 
                apply_type = r[2]
        for r in reverse_multiwords:
            if i >= r[1]:
                multi_words = [x.base_form.lower() for x in tokens if i - r[1] <= x.idx <= i]
                if ' '.join(multi_words) == r[0]:
                    apply_type = r[2]
        # apply for score
        # -------------------------------------------------------------------
        if apply_type:
            chunk = self.get_chunk_data(sentence)
            for c in chunk:
                if c.token_idx <= i <= c.token_idx + c.token_size - 1:
                    if apply_type == 'own':
                        start_idx, end_idx = c.token_idx, (c.token_idx + c.token_size)
                    elif apply_type == 'src':
                        sc = chunk[c.src_idx[-1]]
                        start_idx, end_idx = sc.token_idx, (sc.token_idx + sc.token_size)
                    # elif apply_type == 'depend':
                    max_score_of_reverse = max(scores[start_idx : end_idx])
                    # print('max:', max_score_of_reverse, scores[start_idx : end_idx])
                    del scores[start_idx : end_idx]
                    scores.append(-int(max_score_of_reverse))
                    scores.extend([0] * (end_idx - start_idx - 1))
                    break
        return scores

    def apply_muliwords_rule_for_senti_analisys(self, i, tokens, scores):
        bigram_score = trigram_score = 0
        if i >= 1:  # bigram
            headword = ' '.join([tokens[i - 1].base_form.lower(), tokens[i].base_form.lower()])
            res = self.search_politely_dict([headword])
            bigram_score = res[headword]
        if i >= 2:  # triram
            headword = ' '.join([tokens[i - 2].base_form.lower(), tokens[i - 1].base_form.lower(), tokens[i].base_form.lower()])
            res = self.search_politely_dict([headword])
            trigram_score = res[headword]
        # apply for scores
        if trigram_score:
            del scores[i - 3 : i]
            scores.extend([trigram_score, 0, 0])
        elif bigram_score:
            del scores[i - 2 : i]
            scores.extend([bigram_score, 0])
        return scores
    
    def __call__(self, sentences):
        sentences = self.get_sentences(sentences)
        return [(sentence, self.senti_analisys(sentence)) for sentence in sentences]
    
    def point(self, sentences):
        sentences = self.get_sentences(sentences)
        return round(sum(map(self.senti_analisys, sentences)) / len(sentences), 2)

if __name__ == '__main__':
    default_txt = """
    親譲りの無鉄砲で小供の時から損ばかりしている。
    小学校に居る時分学校の二階から飛び降りて一週間ほど腰を抜かした事がある。
    なぜそんな無闇をしたと聞く人があるかも知れぬ。別段深い理由でもない。
    新築の二階から首を出していたら、同級生の一人が冗談に、いくら威張っても、そこから飛び降りる事は出来まい。
    弱虫やーい。と囃したからである。
    小使に負ぶさって帰って来た時、おやじが大きな眼をして二階ぐらいから飛び降りて腰を抜かす奴があるかと云ったから、この次は抜かさずに飛んで見せますと答えた。"""
    print(JpParser().point(default_txt))