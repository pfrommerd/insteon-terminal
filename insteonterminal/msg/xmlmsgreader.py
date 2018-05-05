from xml.dom import minidom

from .msg import MsgDef, Direction


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

    return results

# Returns a message
def process_msgdef_elem(elem):
    msg_name = elem.attributes['name'].value
    msg_length = elem.attributes['length'].value
    msg_direction = Direction.FROM_MODEM if elem.attributes['direction'].value == 'FROM_MODEM' else Direction.TO_MODEM

    msg_def = MsgDef(msg_name)

    headers = elem.getElementsByTagName('header')
    if len(headers) > 1:
        raise ValueError('No header for message!')
    header = headers[0]
    for n in filter(lambda x: isinstance(x,minidom.Element), header.childNodes):
        process_field_elem(n, msg_def)

    # Set the header length
    msg_def.header_length = msg_def.length

    for n in filter(
            lambda x: isinstance(x,minidom.Element) and x.tagName != 'header',
            elem.childNodes):
        process_field_elem(n, msg_def)
        
    return (elem.attributes['name'].value, msg_def)

def process_field_elem(field_elem, msgdef):
    pass

