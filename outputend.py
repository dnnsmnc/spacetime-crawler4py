def printreport(uniqueURLs, longestPage, longestWords, fifty_words, subDomains):
    # write uniqueURLs to txt file
    with open("Endreport.txt", "w") as file:
        file.write("Q1)\n" + str(len(uniqueURLs)) + " unique URLs found.\n\n")

        file.write("Q2)\n")
        file.write("Longest page: " + longestPage + "  " + str(
            longestWords) + " words\n\n")
        file.write("Q3)\n")
        file.write("50 most common words:\n")
        c = 0
        for token, count in sorted(fifty_words.items(), key=lambda x: x[1],
                                   reverse=True):
            if c >= 50:
                break
            file.write(token + " : " + str(count) + "\n")
            c += 1
        file.write("Number of unique words: " + str(len(fifty_words)) + "\n\n")

        file.write("Q4)\n")
        file.write("Subdomain , number of unique pages\n\n")
        for url, num in sorted(subDomains.items()):
            file.write(url + ", " + str(num) + "\n")
