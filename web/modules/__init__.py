import re
import itertools

from enum import Enum

class Element:
    def __init__(self, tag, attrib={}, **extra):
        if len(attrib) == 0:
            attrib = {}
        self.tag = tag
        self.attrib = attrib
        self._children = []
        self.text = extra.get('text',None)
        self.tail = extra.get('tail',None)

    def clear():
        self.attrib = {}
        self._children = []

    # children related things
    def __iter__(self):
        for c in self._children:
            yield c

    def remove(self, child):
        self._children.remove(child)

    def append(self, child):
        self._children.append(child)


    # attribute related things

    def get(self, attr, default=None):
        if attr in self.attrib:
            return self.attrib[attr]
        else:
            return default

    def set(self, attr, value):
        self.attrib[attr] = value

    # searching tree things

    def find(self, match):
        for c in self._children:
            if c.tag == match:
                return c
            return c.find(match)
        return None

    def findall(self, match):
        return itertools.chain.from_iterable(([c] if c.tag == match else []) + c.findall(match) \
                                                for c in self._children)

    # printing things

    def __str__(self):
        import textwrap
        attr_str = ' '.join('{}="{}"'.format(a,v) for a, v in self.attrib.items())
        if len(attr_str) > 0:
            attr_str = ' ' + attr_str

        children_str = '\n'.join(str(x) for x in self._children)

        text_str = self.text if self.text else ''
        if len(children_str) > 0 and len(text_str) > 0:
            text_str = text_str + '\n'

        tail_str = '\n' + self.tail if self.tail else ''

        if len(children_str) > 0 or self.text is not None:
            content_str = text_str + children_str
            content_str = textwrap.indent(content_str, 4*' ')
            return '<{}{}>\n{}\n</{}>{}'.format(self.tag, attr_str,
                                                  content_str,
                                                  self.tag, tail_str)
        else:
            return '<{}{}/>{}'.format(self.tag, attr_str, tail_str)


class ElementTree:
    def __init__(self, root=None):
        self._root = root

    def getroot(self):
        return self._root

    def find(self, match):
        return self._root.find(match) if root else None

    def findall(self, match):
        return self._root.findall(match) if root else []

class Tokenizer:
    end_tag_ex = re.compile(r'^<\s*\/\s*([^>\s]*)[^>]*>')
    start_tag_ex = re.compile(r'^<\s*([^>\s]*)([^>]*)>')
    autoclose_ex = re.compile(r'^<\s*([^>\s]*)([^>]*)\/\s*>')

    comment_ex = re.compile(r'^<!--([\s\S]*?)-->')
    space_ex = re.compile(r'^\s*$')
    text_ex = re.compile(r'^[^<]+')

    attribute_ex = re.compile(r'\s*([^\s<>]+)\s*=\s*"([^"]+)"\s*')

    def __init__(self, source):
        self._source = source

    def _discard(self, length):
        self._source = self._source[length:]

    def __iter__(self):
        while self.has_next():
            for t in self.next_group():
                yield t

    def has_next(self):
        return len(self._source) > 0

    def parse_attributes(self, tag_attr):
        attribs = []
        for attr_match in Tokenizer.attribute_ex.finditer(tag_attr):
            attr = attr_match.group(1)
            val = attr_match.group(2)
            attribs.append(('attrib', attr, val)) 
        return attribs

    def next_group(self):
        end_tag_match = Tokenizer.end_tag_ex.search(self._source)
        start_tag_match = Tokenizer.start_tag_ex.search(self._source)
        autoclose_match = Tokenizer.autoclose_ex.search(self._source)

        comment_match = Tokenizer.comment_ex.search(self._source)
        space_match = Tokenizer.space_ex.search(self._source)
        text_match = Tokenizer.text_ex.search(self._source)

        if comment_match:
            self._discard(len(comment_match.group(0)))
            text = comment_match.group(1)
            return [('comment', text)]
        elif end_tag_match:
            end_tag = end_tag_match.group(0)
            self._discard(len(end_tag))

            tag_name = end_tag_match.group(1)
            return [('end', tag_name)]
        elif start_tag_match:
            start_tag = start_tag_match.group(0)
            self._discard(len(start_tag))

            tag_name = start_tag_match.group(1)
            tag_attr = start_tag_match.group(2)

            tokens = [('start', tag_name)]
            tokens.extend(self.parse_attributes(tag_attr))
            if autoclose_match:
                tokens.append(('end', tag_name))
            else:
                tokens.append(('text',''))
            return tokens
        elif space_match:
            self._discard(len(space_match.group(0)))
            return []
        else:
            text = text_match.group(0)
            self._discard(len(text))
            return [('text', text)]
        return []


def fromstring(xmlstr):
    tokens = Tokenizer(xmlstr)
    root = None
    elem_stack = []
    last_elem = None
    for t in tokens:
        ttype = t[0]
        if ttype == 'start':
            elem = Element(t[1])
            if len(elem_stack) > 0: # Add to parent
                elem_stack[-1].append(elem)
            elem_stack.append(elem)
            last_elem = elem
        elif ttype == 'end':
            if len(elem_stack) == 1:
                root = elem_stack[0]
            elif len(elem_stack) == 0:
                break
            #print(' '.join(x.tag for x in elem_stack))
            last_elem = elem_stack[-1]
            elem_stack.pop()
        elif ttype == 'attrib':
            if len(elem_stack) > 0:
                elem = elem_stack[-1]
                elem.set(t[1], t[2])
        elif ttype == 'text':
            text = t[1].strip()
            if len(elem_stack) > 0 and last_elem is elem_stack[-1]:
                elem = elem_stack[-1]
                elem.text = (elem.text if elem.text else '') + text
            elif last_elem:
                last_elem.tail = (last_elem.tail if last_elem.tail else '') + text
    return ElementTree(root)

def parse(xmlfile):
    with open(xmlfile, 'r') as f:
        xmlstr = f.read()
        return fromstring(xmlstr)
