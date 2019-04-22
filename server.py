# Starting from practice 7

# ------MY NOTES of api rest-------
# GET info/genomes/:genome_name 	"base_count"->number of bases
# EXAMPLE
# /info/genomes/nanoarchaeum_equitans_kin4_m?content-type=application/json

# GET sequence/id/:id
# EXAMPLES
# /sequence/id/GENSCAN00000000001?object_type=predictiontranscript;type=protein;content-type=..
# ..application/json;db_type=core;species=homo_sapiens
# /sequence/id/ENSP00000288602?content-type=application/json-> sequence


# First we obtain the FRAT1 gene sequence
import http.client
import json

HOSTNAME = "rest.ensembl.org"
ENDPOINT = "/sequence/id/ENSG00000165879?content-type=application/json"
METHOD = "GET"

headers = {'User-Agent': 'http-client'}
conn = http.client.HTTPSConnection(HOSTNAME)

# -- Sending the request
conn.request(METHOD, ENDPOINT, None, headers)
r1 = conn.getresponse()

# -- Printing the status
print()
print("Response received: ", end='')
print(r1.status, r1.reason)

# -- Read the response's body and close connection
text_json = r1.read().decode("utf-8")
conn.close()

result = json.loads(text_json)


# We create the Seq class
class Seq:
    """A class for representing sequences"""

    def __init__(self, strbases):
        self.strbases = strbases  # self.strbases now represents my initial string

    # Length of the string
    def len(self):
        return len(self.strbases)  # returns the length of our string(self.strbases)

    # Number of a concrete base
    def count(self, base):
        res = self.strbases.count(base)  # counting the base that we will introduce
        return res

    # Percentage of a concrete base
    def perc(self, base):
        tl = self.len()
        for e in base:
            n = self.count(e)
            res = round(100.0 * n / tl, 1)  # percentage with one decimal of precision
            return res

    # The percentage of the most popular  base
    def results(self, dict_p):
        s1 = "The total number of bases in FRAT1 gene is: "+str(self.len())
        s2 = "The number of T bases is: "+str(self.count("T"))
        s3 = ""
        s4 = ""
        for key, value in dict_p.items():
            if value == max(dict_p.values()):
                s3 = "The most popular base is " + str(key) + " and its percentage is " + str(value)
            s4 += "The percentage of " + str(key) + " is " + str(value) + "\n"

        s = s1 + "\n" + s2 + "\n" + s3 + "\n" + s4
        return s


# --Main program
# Creating an object and printing the results
sequence = Seq(result["seq"])

bases = "ACTG"  # string to iterate over the bases
percentage = {}  # dictionary for percentages

# adding information to the dictionary
for i in bases:
    percentage[i] = str(sequence.perc(i))+"%"  # percentage symbol string need another string to be added

print(sequence.results(percentage))  # printing finally the results
