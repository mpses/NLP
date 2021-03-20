#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from unicodedata import normalize

def preprocessing(text):
    text = normalize("NFKC", text)
    text = clean_text(text)
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[【】（）()［］\[\]]', ' ', text)
    text = re.sub(r'[@＠]\w+', '', text)
    text = re.sub(r'https?:\/\/.*?[\r\n ]', '', text)
    text = re.sub(r'　', ' ', text)
    return text