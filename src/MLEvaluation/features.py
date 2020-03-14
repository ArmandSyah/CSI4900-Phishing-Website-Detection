from urllib.parse import urlparse, parse_qs
from collections import Counter
from math import log, e
from src.MLEvaluation.new_features import NewFeatures

import numpy as np

well_known_ports = [1, 5, 7, 18, 20, 21, 22, 23, 25, 29, 37, 42, 43, 49, 53, 69, 70, 79, 80, 103, 108, 109, 110, 115,
118, 119, 137, 193, 143, 150, 156, 161, 179, 190, 194, 197, 389, 396, 443, 444, 445, 458, 546, 547, 563, 569, 1080]
url_delimiters = ['.', ',', '/', '=', '-', '_']

# MAIN Feature Set

class WebsiteInfo:
    def __init__(self, target_url: str, unknown_url: str, keyword: str, is_legit: int = -1):
        parsed_url = urlparse(unknown_url.lower())
        self.target_url = target_url
        self.unknown_url = unknown_url
        self.keyword = keyword
        self.url = URLpart(parsed_url)
        self.domain = DomainPart(parsed_url.netloc)
        self.path = PathPart(parsed_url.path)
        self.query = QueryPart(parse_qs(parsed_url.query), parsed_url.query)
        self.fragment = FragmentPart(parsed_url.fragment, len(unknown_url))
        self.new_features = NewFeatures(target_url, unknown_url, keyword)
        self.is_legit = is_legit
    
    def to_json(self):
        url_features = {}
        for k, v in vars(self).items():
            if isinstance(v, int):
                url_features[k] = v
            else:
                for key, value in vars(v).items():
                    url_features[key] = value
        return url_features

# Calculating each feature

class URLpart:
    def __init__(self, url):
        self.url = url.geturl()
        self.protocol = url.scheme
        self.port_number = url.port if url.port else (80 if url.scheme == 'http' else 443)
        self.is_default_port_number = check_default_port(url.port)
        self.url_letter_count = check_letter_count(url.geturl())
        self.url_delimeter_count = check_url_delimeter_count(url.geturl())
        self.url_digit_rate = check_url_digit_rate(url.geturl())
        self.is_url_encoded = check_url_encoded(url.geturl())
        self.url_symbol_count = check_url_symbol_count(url.geturl())

class DomainPart:
    def __init__(self, domain):
        self.domain_deli_count = check_domain_delimeter_count(domain)
        self.domain_letter_count = check_letter_count(domain)
        self.domain_digit_rate = check_domain_digit_rate(domain)
        self.is_port_in_domain = check_port_in_domain(domain)
        self.domain_symbol_count = check_domain_symbol_count(domain)

class PathPart:
    def __init__(self, path):
        self.path = path
        self.path_letter_count = check_letter_count(path)
        self.path_digit_rate = check_path_digit_rate(path)
        self.path_symbol_count = check_domain_symbol_count(path)

class QueryPart:
    def __init__(self, queryDict: dict, q: str,  *args, **kwargs):
        self.query = q
        queryDict = {key:value[0] for key,value in queryDict.items()}
        if not queryDict:
            self.query_symbol_count = 0
            self.query_deli_count = 0
            self.avg_value_letter_count = 0
            self.avg_value_symbol_count = 0
            self.avg_var_symbol_count = 0
            self.avg_var_letter_count = 0
            self.avg_var_len = 0
            self.query_value_max_token = 0
            self.query_var_max_token = 0
            self.sum_var_len = 0
            self.query_letter_count = 0
            self.query_digit_rate = 0
            self.query_value_digit_count = 0
            self.query_var_digit_count = 0
        else:
            self.query_symbol_count = check_query_symbol_count(queryDict)
            self.query_deli_count = check_query_delimeter_count(queryDict)
            self.avg_value_letter_count = average_letter_count(queryDict.values())
            self.avg_value_symbol_count = average_symbol_count(queryDict.values())
            self.avg_var_symbol_count = average_symbol_count(queryDict.keys())
            self.avg_var_letter_count = average_letter_count(queryDict.keys())
            self.avg_var_len = average_variable_length(queryDict.keys())
            self.query_value_max_token = longest_token(queryDict.values())
            self.query_var_max_token = longest_token(queryDict.keys())
            self.sum_var_len = sum( [len(q) for q in queryDict.keys()] )
            self.query_letter_count = check_query_letter_count(queryDict)
            self.query_digit_rate = check_query_digit_rate(queryDict) 
            self.query_value_digit_count = sum([1 if c in string.digits else 0 for c in queryDict.values()])
            self.query_var_digit_count = sum([1 if c in string.digits else 0 for c in queryDict.keys()])

class FragmentPart:
    def __init__(self, fragment: str, url_len, *args, **kwargs):
        self.fragment = fragment

        if not fragment:
            self.frag_digit_count = 0
            self.frag_letter_count = 0
            self.frag_digit_rate = 0
            self.frag_symbol_count = 0
            self.frag_len_ratio = 0
            self.frag_unigram_ent = 0
            self.frag_brigram_ent = 0
            self.frag_trigram_ent = 0
        else:
            self.frag_digit_count = check_digit_count(fragment)
            self.frag_letter_count = check_letter_count(fragment)
            self.frag_digit_rate = check_digit_count(fragment) / (check_letter_count(fragment) if check_letter_count(fragment) != 0 else 1)
            self.frag_symbol_count = check_fragment_symbol_count(fragment)
            self.frag_len_ratio = len(fragment) / url_len
            self.frag_unigram_ent = check_unigram_entropy(fragment)
            self.frag_brigram_ent = check_bigram_entropy(fragment)
            self.frag_trigram_ent = check_trigram_entropy(fragment)


def check_default_port(port: int):
    return port in well_known_ports

def check_letter_count(input: str):
    return sum([1 if c in string.ascii_letters else 0 for c in input])

def check_url_delimeter_count(url: str):
    return sum([1 if c in url_delimiters else 0 for c in url])

def check_url_digit_rate(url: str):
    return sum([1 if c in string.digits else 0 for c in url]) / (check_letter_count(url) if check_letter_count(url) != 0 else 1)

def check_url_encoded(url: str):
    return '%' in url

def check_url_symbol_count(url: str):
    percent_encoded = r'%[0-9a-fA-F]{2}'
    return len(re.findall(percent_encoded, url))

def check_domain_delimeter_count(domain: str):
    return sum([1 if c in url_delimiters else 0 for c in domain])

def check_letter_count(domain: str):
    return sum([1 if c in string.ascii_letters else 0 for c in domain])

def check_digit_count(fragment: str):
    return sum([1 if c in string.digits else 0 for c in fragment])

def check_fragment_symbol_count(fragment: str):
    percent_encoded = r'%[0-9a-fA-F]{2}'
    return len(re.findall(percent_encoded, fragment))

def check_domain_digit_rate(domain: str):
    return sum([1 if c in string.digits else 0 for c in domain]) / (check_letter_count(domain) if check_letter_count(domain) != 0 else 1)

def check_port_in_domain(domain: str):
    return 1 if re.search(':\d+', domain) else 0

def check_domain_symbol_count(domain: str):
    percent_encoded = r'%[0-9a-fA-F]{2}'
    return len(re.findall(percent_encoded, domain))

def check_path_digit_rate(path: str):
    return  sum([1 if c in string.digits else 0 for c in path]) / (check_letter_count(path) if check_letter_count(path) != 0 else 1)

def check_query_digit_rate(query: dict):
    var_digit_count, val_digit_count, var_letter_count, val_letter_count = 0,0,0,0
    for var, val in query.items():
        var_digit_count += sum([1 if c in string.digits else 0 for c in var])
        val_digit_count += sum([1 if c in string.digits else 0 for c in val])
        var_letter_count += check_letter_count(var)
        val_letter_count += check_letter_count(val)
    return (var_digit_count + val_digit_count) / (var_letter_count + val_letter_count)

def check_query_delimeter_count(query: dict):
    var_count, val_count = 0,0
    for var, val in query.items():
        var_count += check_domain_delimeter_count(var)
        val_count += check_domain_delimeter_count(val)
    return var_count + val_count
    
def average_letter_count(input: list):
    return sum([check_letter_count(word) for word in input]) / len(input)

def average_variable_length(input: list):
    return sum([len(word) for word in input]) / len(input)

def longest_token(input: list):
    return max([len(word) for word in input])

def check_query_letter_count(query: dict):
    var, val = query.keys(), query.values()
    return sum(check_letter_count(v) for v in var) + sum(check_letter_count(v) for v in val)

def check_query_symbol_count(query: dict):
    percent_encoded = r'%[0-9a-fA-F]{2}'
    symbol_count = 0
    for var, val in query.items():
        symbol_count += len(re.findall(percent_encoded, var))
        symbol_count += len(re.findall(percent_encoded, val))
    return symbol_count

def average_symbol_count(input: list):
    percent_encoded = r'%[0-9a-fA-F]{2}'
    return sum([len(re.findall(percent_encoded, word)) for word in input]) / len(input)

def check_unigram_entropy(fragment: str):
    unigrams = [c for c in fragment]
    unigram_counts = Counter(unigrams)
    labels = [count for _, count in unigram_counts.most_common()]
    return entropy(labels)

def check_trigram_entropy(fragment: str):
    bigrams = [fragment[i:i+2] for i, _ in enumerate(fragment[0:len(fragment)-2])]
    bigram_counts = Counter(bigrams)
    labels = [count for _, count in bigram_counts.most_common()]
    return entropy(labels)

def check_bigram_entropy(fragment: str):
    trigrams = [fragment[i:i+3] for i, _ in enumerate(fragment[0:len(fragment)-3])]
    trigram_counts = Counter(trigrams)
    labels = [count for _, count in trigram_counts.most_common()]
    return entropy(labels)

def entropy(labels, base=None):
  """ Computes entropy of label distribution. """

  n_labels = len(labels)

  if n_labels <= 1:
    return 0

  value,counts = np.unique(labels, return_counts=True)
  probs = counts / n_labels
  n_classes = np.count_nonzero(probs)

  if n_classes <= 1:
    return 0

  ent = 0.

  # Compute entropy
  base = e if base is None else base
  for i in probs:
    ent -= i * log(i, base)

  return ent