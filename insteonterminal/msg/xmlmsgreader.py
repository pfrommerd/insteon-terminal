from xml.dom import minidom

def read_xml(filename):
    xmldoc = minidom.parse(filename)
    return process_xmltree(xmldoc)

# Returns a map of name to msgdef
def process_xmltree(xmldoc):
    results = {}

    elems = xmldoc.getElementsByTagName('msg')
    for m in elems:
        d = process_msgdef_elem(m)
        results[d[0]] = d[1]

# Returns a message
def process_msgdef_elem(elem):
    headers = elem.getElementsByTagName('header')
    if len(headers) > 1:
        raise ValueError('No header for message!')
    header = headers[0]
    for n in filter(lambda x: isinstance(x,minidom.Element), header.childNodes):
        pass


    for n in filter(
            lambda x: isinstance(x,minidom.Element) and x.tagname != 'header',
            elem.childNodes):
        pass
        
    return (elem,elem)
