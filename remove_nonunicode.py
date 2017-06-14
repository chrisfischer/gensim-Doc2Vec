with open("result_utf-8.txt", "wb") as outfile:
    with open("result.txt") as infile:
        txt = infile.read()
        txt = txt.decode('utf-8','ignore').encode("utf-8")
        outfile.write(txt)