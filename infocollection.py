

def build_report(uniqueURLs, subdomainDict, words_dict, longest_page):
    f = open("report.txt", "w")
    f.write("Q1: Number of unique pages: %d\n\n" % len(uniqueURLs))
    f.write("Q2: Longest page: %s (%d words)\n\n" % (longest_page[0], longest_page[1]))
    words_dict = sorted(words_dict.items(), key = lambda x: x[1], reverse = True)
    f.write("Q3: ")
    for i in range(0,50):
        f.write("%s, " % (words_dict[i][0]))
    f.write("%s\n\n" % (words_dict[50][0]))
    sortedsubs = sorted(subdomainDict.keys(), key = lambda x:x)
    for sub in sortedsubs:
        f.write("%s, %d\n" % (sub, subdomainDict[sub]))
