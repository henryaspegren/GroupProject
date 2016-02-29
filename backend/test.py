try:
    import http.client as httplib
    from urllib.parse import urlencode
except ImportError:
    import httplib
    from urllib import urlencode

import socket


def tcpip4_socket(host, port):
    """Open a TCP/IP4 socket to designated host/port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        yield s
    finally:
        try:
            s.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        except OSError:
            pass
        finally:
            s.close()
			
class SocketNER():
    """Stanford NER over simple TCP/IP socket."""

    def __init__(self, host='localhost', port=1234, output_format='inlineXML'):
        if output_format not in ('slashTags', 'xml', 'inlineXML'):
            raise ValueError('Output format %s is invalid.' % output_format)
        self.host = host
        self.port = port
        self.oformat = output_format

    def tag_text(self, text):
        """Tag the text with proper named entities token-by-token.
        :param text: raw text string to tag
        :returns: tagged text in given output format
        """
        for s in ('\f', '\n', '\r', '\t', '\v'): #strip whitespaces
            text = text.replace(s, '')
        text += '\n' #ensure end-of-line
        with tcpip4_socket(self.host, self.port) as s:
            if not isinstance(text, bytes):
                text = text.encode('utf-8')
            s.sendall(text)
            tagged_text = s.recv(10*len(text))
        return tagged_text.decode('utf-8')