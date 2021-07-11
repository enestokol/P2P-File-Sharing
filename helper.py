import os
import math
import os.path

ar = []

def split(file):
    # This'll be the parameter you provide for this code. The name of the content that the user wants to download.
    for i in range(len(file)):
        content_name = os.path.splitext(os.path.basename(file[i]))[0]
        filename = content_name + os.path.splitext(os.path.basename(file[i]))[1]  # file extension like .exe
        c = os.path.getsize("uploads/" + filename)
        CHUNK_SIZE = math.ceil(math.ceil(c) / 5)

        index = 1
        with open("uploads/" + filename, 'rb') as infile:
            chunk = infile.read(int(CHUNK_SIZE))
            while chunk:
                chunkname = content_name + '_' + str(index) + os.path.splitext(os.path.basename(file[i]))[1]
                ar.append(chunkname)
                with open("uploads/temp/" + chunkname, 'wb+') as chunk_file:
                    chunk_file.write(chunk)
                index += 1
                chunk = infile.read(int(CHUNK_SIZE))
        chunk_file.close()


####################################################################################
# STITCH FILE BACK TOGETHER

def combine(file):
    content_name = os.path.splitext(os.path.basename(file))[0]
    ext = os.path.splitext(os.path.basename(file))[1]
    chunknames = [content_name + '_1' + ext, content_name + '_2' + ext, content_name + '_3' + ext,
                  content_name + '_4' + ext,
                  content_name + '_5' + ext]

    # with open(content_name+'.png', 'w') as outfile:
    with open("downloads/{0}{1}".format(content_name, ext), 'wb') as outfile:
        for chunk in chunknames:
            with open('downloads/temp/' + chunk, 'rb') as infile:
                outfile.write(infile.read())


def size_format(b):
    if b < 1000:
        return '%i' % b + 'B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b / 1000) + 'KB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b / 1000000) + 'MB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b / 1000000000) + 'GB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b / 1000000000000) + 'TB'
