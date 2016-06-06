import zlib
import bz2
import gzip
import StringIO
import json


def LZW_compress(uncompressed):
    """Compress a string to a list of output symbols."""

    # Build the dictionary.
    dict_size = 256
    dictionary = dict((chr(i), chr(i)) for i in xrange(dict_size))
    # in Python 3: dictionary = {chr(i): chr(i) for i in range(dict_size)}

    w = ""
    result = []
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Add wc to the dictionary.
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    # Output the code for w.
    if w:
        result.append(dictionary[w])
    return result


def compress(s):
    print 'Original Length: {}'.format(len(s))
    print 'zlib compressed length: {}'.format(len(zlib.compress(s)))
    print 'bz2 compressed length: {}'.format(len(bz2.compress(s)))
    print 'LZW compressed length: {}'.format(len(LZW_compress(s)))



print 'Compression test'

str = '{  "events": [    [      "Super 80",      2,      "Sat, 12 Mar 2016 00:00:00 GMT",      "Russ Lalla",      "https://lh5.googleusercontent.com/-S_7U3TWBVUQ/AAAAAAAAAAI/AAAAAAAABGQ/8YDirKU6UZg/photo.jpg"    ],    [      "Super 80",      2,      "Sat, 12 Mar 2016 00:00:00 GMT",      "Chaad Dhanoolal",      "https://lh6.googleusercontent.com/-NZVmZtFRWIA/AAAAAAAAAAI/AAAAAAAAAoM/C97EorOsAIg/photo.jpg"    ],    [      "Smooth Rider",      4,      "Sat, 12 Mar 2016 00:00:00 GMT",      "Chaad Dhanoolal",      "https://lh6.googleusercontent.com/-NZVmZtFRWIA/AAAAAAAAAAI/AAAAAAAAAoM/C97EorOsAIg/photo.jpg"    ],    [      "Super 80",      2,      "Fri, 11 Mar 2016 00:00:00 GMT",      "Chaad Dhanoolal",      "https://lh6.googleusercontent.com/-NZVmZtFRWIA/AAAAAAAAAAI/AAAAAAAAAoM/C97EorOsAIg/photo.jpg"    ],    [      "Super 80",      2,      "Thu, 10 Mar 2016 00:00:00 GMT",      "Russ Lalla",      "https://lh5.googleusercontent.com/-S_7U3TWBVUQ/AAAAAAAAAAI/AAAAAAAABGQ/8YDirKU6UZg/photo.jpg"    ],    [      "Super 80",      2,      "Wed, 09 Mar 2016 00:00:00 GMT",      "Keshav Bahadoor",      "https://lh4.googleusercontent.com/-RnzkCq1r6oY/AAAAAAAAAAI/AAAAAAAADV0/8V8r60tAB2s/photo.jpg"    ],    [      "Super 80",      2,      "Tue, 08 Mar 2016 00:00:00 GMT",      "Russ Lalla",      "https://lh5.googleusercontent.com/-S_7U3TWBVUQ/AAAAAAAAAAI/AAAAAAAABGQ/8YDirKU6UZg/photo.jpg"    ],    [      "Smooth Rider",      4,      "Tue, 08 Mar 2016 00:00:00 GMT",      "Russ Lalla",      "https://lh5.googleusercontent.com/-S_7U3TWBVUQ/AAAAAAAAAAI/AAAAAAAABGQ/8YDirKU6UZg/photo.jpg"    ],    [      "Super 80",      2,      "Mon, 07 Mar 2016 00:00:00 GMT",      "Russ Lalla",      "https://lh5.googleusercontent.com/-S_7U3TWBVUQ/AAAAAAAAAAI/AAAAAAAABGQ/8YDirKU6UZg/photo.jpg"    ],    [      "Shining Star",      1,      "Sun, 06 Mar 2016 00:00:00 GMT",      "Russ Lalla",      "https://lh5.googleusercontent.com/-S_7U3TWBVUQ/AAAAAAAAAAI/AAAAAAAABGQ/8YDirKU6UZg/photo.jpg"    ],    [      "Super 80",      2,      "Sat, 05 Mar 2016 00:00:00 GMT",      "Chaad Dhanoolal",      "https://lh6.googleusercontent.com/-NZVmZtFRWIA/AAAAAAAAAAI/AAAAAAAAAoM/C97EorOsAIg/photo.jpg"    ],    [      "Shining Star",      1,      "Sat, 05 Mar 2016 00:00:00 GMT",      "Chaad Dhanoolal",      "https://lh6.googleusercontent.com/-NZVmZtFRWIA/AAAAAAAAAAI/AAAAAAAAAoM/C97EorOsAIg/photo.jpg"    ]  ]}'
gzip_str = 'H4sIAAAAAAAA/9XVQW+CMBgG4L/ScGZSmCJ6A53GOLcMBaPLsjTSUDbkY23xsGX/fdVFTqDJsgM0DWm+krRP3rT9QkijB5pJoQ3RM1Lt9FHVZZFTjhys6b8FSz9PEKkj00ILwpGFTRthPDx1NF2szn9rfiEEuidpSsoSkzIXQ8NIWa8TA8QpLQTlO8ikWr+zg71xs3ztB7ertRcGT4Zbtlk59qZPhrMZJ3we2ME2NnIGEjpveawdV3jR/xEwYoREaMxIBpCStEJh1yketuF+Kyf+euZWKlxYGKNB/w74o3BnVxR7AMmQn0SUn/fQbaekLo8JT5TCbLlixQqlwO09Fmsa6QgPrgDmVDByQB5hJALgFYpuncLPPt9HHya3YVOpGIfYcEKH21i6niX+GENBlcJpfgyXznVrEHUpLCBTgH7zASzJkixGS0nKFMzydi2OCLv5iIsPHe615GK9GEXDJap//wA5ETlvSwkAAA=='



compress(str)

c_str = zlib.compress(str)

emulated_file = StringIO.StringIO(gzip_str)
emulated_file.seek(0)
decompressed_file = gzip.GzipFile(fileobj=emulated_file, mode='rb')

# json_data = json.load(decompressed_file)

# trying to test compression 


# print c_str

