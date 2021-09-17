import codecs
import sys


class Encoding:

    @staticmethod
    def init_stderr():
        if sys.stderr.encoding != 'UTF-8':
            if sys.version_info[:2] >= (3, 7):
                sys.stderr.reconfigure(encoding='utf-8')
            elif sys.version_info[:2] >= (3, 1):
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
            else:
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
