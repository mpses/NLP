# NLP
Natural Language Processing.

## Requirements
- MeCab

```shell
$ brew install mecab
$ brew install mecab-ipadic

$ brew install swig
$ pip install mecab-python3
```

- NEologD

```shell
$ brew install git curl xz
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
$ cd mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n
```

- CRF++ <span id="a1">[¹](#1)</span>

```shell
$ brew install wget
$ wget "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7QVR6VXJ5dWExSTQ" -O CRF++-0.58.tar.gz
$ tar zxfv CRF++-0.58.tar.gz
$ cd CRF++-0.58
$ ./configure
$ make
$ sudo make install
```

- CaboCha

```shell
$ FILE_ID=0B4y35FiV1wh7SDd1Q1dUQkZQaUU
$ FILE_NAME=cabocha-0.69.tar.bz2
$ curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID}" > /dev/null
$ CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
$ curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID}" -o ${FILE_NAME}
$ tar jxvf cabocha-0.69.tar.bz2
$ cd cabocha-0.69
$ ./configure --with-charset=utf8
$ make
$ sudo make install

~/cabocha-0.69 $ cd python
$ sudo python3 setup.py build_ext
$ sudo python3 setup.py install
```

- Sentiment Dictionary <span id="a2">[²](#2)</span>

```
/NLP $ mkdir NLP_lib/dict
$ cd NLP_lib/dict
$ wget http://www.cl.ecei.tohoku.ac.jp/resources/sent_lex/wago.121808.pn
$ wget http://www.cl.ecei.tohoku.ac.jp/resources/sent_lex/pn.csv.m3.120408.trim
```

- etc.

```shell
pip install better_exceptions
export BETTER_EXCEPTIONS=1
```


## Environments
```shell
$ sw_vers
ProductName:    macOS
ProductVersion: 11.1
BuildVersion:   20C69

$ python3 -V
Python 3.8.2
```


## References
- <span id="1">¹</span> [curlやwgetで公開済みGoogle Driveデータをダウンロードする - Qiita](https://qiita.com/namakemono/items/c963e75e0af3f7eed732) [⏎](#a1)<br>
- [nlp-jp/jp_parser.py - GitHub](https://github.com/matsu0228/nlp-jp/blob/master/lib/jp_parser.py)
  - [大槻諒, 松吉俊, 福本 文代. 否定の焦点コーパスの構築と自動検出器の試作. 言語処理学会第19回年次大会論文集, pp.936-939, 2013. / Ryo Otsuki, Suguru Matsuyoshi, Fumiyo Fukumoto. Proceedings of the 19th Annual Meeting of the Association for Natural Language Processing, pp.936-939, 2013.](https://www.anlp.jp/proceedings/annual_meeting/2013/pdf_dir/C6-1.pdf)
- <span id="2">²</span> [日本語評価極性辞書 - 東北大乾研究室](http://www.cl.ecei.tohoku.ac.jp/index.php?Open%20Resources%2FJapanese%20Sentiment%20Polarity%20Dictionary) [⏎](#a2)<br>
  - 小林のぞみ, 乾健太郎, 松本裕治, 立石健二, 福島俊一. 意見抽出のための評価表現の収集. 自然言語処理 Vol.12, No.3, pp.203-222, 2005. / Nozomi Kobayashi, Kentaro Inui, Yuji Matsumoto, Kenji Tateishi. Collecting Evaluative Expressions for Opinion Extraction, Journal of Natural Language Processing 12(3), 203-222, 2005.
  - 東山昌彦, 乾健太郎, 松本裕治. 述語の選択選好性に着目した名詞評価極性の獲得. 言語処理学会第14回年次大会論文集, pp.584-587, 2008. / Masahiko Higashiyama, Kentaro Inui, Yuji Matsumoto. Learning Sentiment of Nouns from Selectional Preferences of Verbs and Adjectives, Proceedings of the 14th Annual Meeting of the Association for Natural Language Processing, pp.584-587, 2008.