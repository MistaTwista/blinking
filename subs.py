import pysrt

subs = pysrt.open('subs.srt')

len(subs)
for sub in subs:
    print(sub)
