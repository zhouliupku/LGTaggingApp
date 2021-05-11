# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:55:30 2019

@author: Zhou
"""

import lg_utils
import config


class Page(object):
    def __init__(self, pid, txt, eos_idx):
        self.pid = pid   #page id
        self.txt = txt   #original text
        self.eos_idx = eos_idx     #end-of-sentence indices
        
    def separate_sentence(self, parsed_sent_len):    
        """
        Separate page to sentences according to parsed_sent_len, list of int
        Return a list of Record
        """
        assert len(self.txt) == sum(parsed_sent_len)
        head_char_idx = 0
        records = []
        for sent_len in parsed_sent_len:
            text = self.txt[head_char_idx : (head_char_idx + sent_len)]
            records.append(Record(text, None))
            head_char_idx += sent_len
        return records
        
    def get_x(self):
        """
        get x sequence as list of str
        """
        return [config.BEG_CHAR] + list(self.txt) + [config.END_CHAR]
        
    def get_y(self):
        """
        get y sequence as list of tag char
        """
        tags = [config.INS_TAG for i in range(len(self.txt))]
        for i in self.eos_idx:
            tags[i] = config.EOS_TAG
        return [config.BEG_TAG] + tags + [config.END_TAG]
    
    def get_sep_len(self):
        """
        get the list of each sentence's length by end-of-sentence indices
        """
        if self.eos_idx == []:
            return []
        else:
            return [self.eos_idx[0] + 1] \
                    + [x-y for x,y in zip(self.eos_idx[1:], self.eos_idx[:-1])]

            

class Record(object):
    def __init__(self, txt, tags):
        """
        idx: record id indicating the index of record in the page it belongs to
        data: tuple of (text, tags)
        """
        self.orig_text = txt        # as a string without <S>, </S>
        self.orig_tags = [None for i in txt] if tags is None else tags
        self.chars = [CharSample(c, t) for c, t in zip(self.orig_text, self.orig_tags)]
        self.chars = [CharSample(config.BEG_CHAR, config.BEG_TAG)] + self.chars
        self.chars = self.chars + [CharSample(config.END_CHAR, config.END_TAG)]

    def set_tag(self, tag_seq):
        """
        tag_seq: list of tags, begin with BEG_TAG, ending with END_TAG
        """
        assert len(tag_seq) == len(self.chars)
        for i in range(1, len(tag_seq) - 1):
            self.chars[i].set_tag(tag_seq[i])
        
    def get_tag_res_dict(self, interested_tags):
        """
        For a tagged record, return a dictionary {col_name: [content1, ...]}
        """
        tag_res_dict = {}
        for col_name in interested_tags:
            keywords = lg_utils.get_keywords_from_tagged_record(self.chars[1:-1], col_name)
            tag_res_dict[col_name] = keywords
        return tag_res_dict
        
    def get_x(self):
        """
        get x sequence as list of char
        """
        return [cs.get_char() for cs in self.chars]
        
    def get_y(self):
        """
        get y sequence as list of tag char
        """
        return [cs.get_tag() for cs in self.chars]
    
    def __str__(self):
        return ''.join([c.get_char() for c in self.chars[1:-1]])
        
    
class CharSample(object):
    def __init__(self, char, tag):
        self.char = char    # both string
        self.tag = tag
        
    def get_char(self):
        return self.char
    
    def get_tag(self):
        return self.tag
    
    def set_tag(self, tag):
        self.tag = tag
