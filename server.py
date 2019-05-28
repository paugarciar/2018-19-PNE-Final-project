# Server that provides some services related with genes and chromosomes using the HTTP protocol.
# The user introduces the parameters through the main page HTML, the data is taken from the rest.ensembl.org
# web page and the results can be presented in json format if the user indicates it with the parameter json = 1
# or in an HTML page, otherwise.

# importing the needed resources
import http.server
import http.client
import json
import socketserver
import termcolor

# Server's port
PORT = 8000

# Client
HOSTNAME = "rest.ensembl.org"
ENDPOINT0 = "/info/species?content-type=application/json"
METHOD = "GET"

headers = {'User-Agent': 'http-client'}
conn = http.client.HTTPSConnection(HOSTNAME)


# Function with the endpoint dependent part
def client(endpoint):
    """function of a common client that asks information using json
    and generates a dictionary with it"""

    # -- Sending the request
    conn.request(METHOD, endpoint, None, headers)
    r1 = conn.getresponse()

    # -- Printing the status
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)

    # -- Read the response's body and close connection
    text_json = r1.read().decode("utf-8")
    conn.close()
    return json.loads(text_json)


# Seq class for gene questions
class Seq:
    """A class for representing sequences"""

    def __init__(self, strbases):
        self.strbases = strbases  # self.strbases now represents my species name

    # Obtaining the ID of a species
    def id(self):
        ENDPOINT3 = "/lookup/symbol/homo_sapiens/" + self.strbases + "?content-type=application/json"
        result3 = client(ENDPOINT3)
        return result3["id"]

    # Obtaining the sequence from an ID
    def gene_seq(self):
        ENDPOINT4 = "/sequence/id/" + self.id() + "?content-type=application/json"
        result4 = client(ENDPOINT4)
        return result4["seq"]

    # Length of the string
    def len(self):
        return len(self.gene_seq())  # returns the length of our string(self.gene_seq())

    # Number of a concrete base
    def count(self, base):
        res = self.gene_seq().count(base)  # counting the base that we will introduce
        return res

    # Percentage of a concrete base
    def perc(self, base):
        tl = self.len()
        for e in base:
            n = self.count(e)
            res = round(100.0 * n / tl, 1)  # percentage with one decimal of precision
            return res

    # Results presentation
    def results(self):
        bases = "ACTG"
        s1 = "The total number of bases is: "+str(self.len())
        s2 = ""  # empty string to save the percentage results of the following percentage loop
        for b in bases:
            s2 += "The percentage of " + b + " is: " + str(self.perc(b)) + "%" + "<br>"
        return s1 + "<br><br>" + s2


# Class with our Handler that inheritates all its methods and properties
class TestHandler(http.server.BaseHTTPRequestHandler):  # Objects with the properties of the library

    def do_GET(self):
        """This method is called whenever the client invokes the GET method
        in the HTTP protocol request"""

        # Printing in the server some useful information
        print("GET received")
        print("Request line:" + self.requestline)
        print(" Cmd: " + self.command)
        print(" Path: " + self.path)

        # Separating and selecting the information of the path
        res = self.path.split("?")[0]
        p = (self.path.replace("=", ",")).replace("&", ",")
        ins = p.split(",")  # Making a list of instructions dividing the string in the = and & symbols
        print(" Ins: ", ins)

        # Some important parameters
        text = []  # Empty list that will save the response information
        j_dict = {}  # Dictionary that will save the response information when json_opt == "json1"
        page = "response.html"  # Our page will be response except if the endpoint is "/" or it does not exist
        keyword_j_dict = ""  # Keyword of j_dict to which we will assign specific values of text list
        y = []  # parameter only used in case we want to print a unique string contained in a list
        code = 200  # if everything is OK!

        # Classification of the information requested in function of the resource
        try:
            if self.path == "/":  # Using the resource / to obtain the main page with all the options
                page = "main-page.html"

            elif res == "/listSpecies":  # Using the resource /listSpecies

                result0 = client(ENDPOINT0)
                # The variable limit has been created to avoid the error "referenced before assignment"
                limit = ""
                if "json=1" in self.path:
                    j = 4  # j is the length of instructions with limit parameter
                    k = 2  # k is the length of instructions without limit parameter
                else:
                    j = 2
                    k = 1

                if len(ins) == j:
                    limit = int(ins[1])
                # Using elif instead of else to avoid sending the list of species with excess of parameters
                elif len(ins) == k:
                    limit = len(result0["species"])  # If there is no limit, the loop will iterate over all the species
                for index in range(limit):
                    text.append(result0["species"][index]["name"])

                keyword_j_dict += "species"  # Our keyword "species" will be assigned with all species values

            elif res == "/karyotype":  # Using the resource /karyotype

                ENDPOINT1 = "/info/assembly/"+ins[1]+"?content-type=application/json"
                result1 = client(ENDPOINT1)
                text = result1["karyotype"]  # text will be our list of chromosomes

                keyword_j_dict = "karyotype"  # choosing the word karyotype as a keyword

            elif res == "/chromosomeLength":  # Using the resource /chromosomeLength

                specie = ins[1]
                ch = ins[3]
                ENDPOINT2 = "/info/assembly/"+specie+"/"+ch+"?content-type=application/json"
                result2 = client(ENDPOINT2)
                text.append(str(result2["length"]))  # Selecting the value that corresponds to the length keyword
                keyword_j_dict = "length"  # Name of the keyword of j_dict for this case
                y.append(0)  # this will be used to indicate that we want the string contained in the list

            elif res == "/geneSeq":  # Using the resource /geneSeq

                sp = Seq(ins[1])  # Object of the species name
                text.append(sp.gene_seq())  # calling the method gene_seq to obtain the sequence of the sp object
                keyword_j_dict = "seq"  # Name of the keyword of j_dict for this case
                y.append(0)  # this will be used to indicate that we want the string contained in the list

            elif res == "/geneInfo":

                sp = Seq(ins[1])  # Object of the species name
                id_number = sp.id()  # calling the method id to obtain the identity number of the sp object
                ENDPOINT5 = "/overlap/id/" + id_number + "?feature=gene;content-type=application/json"
                result4 = client(ENDPOINT5)  # Dictionary that contains several lists of information for different genes

                a = ""  # This variable avoids the error "referenced before assignment"
                for i in range(len(result4)):  # loop to search which gene is the one that coincides with our requisites
                    if result4[i]["id"] == id_number:  # the correct information is in the list in which is our id gene
                        a = i

                # Searching the values in the selected list
                text.append("Start: " + str(result4[a]["start"]))
                text.append("End: " + str(result4[a]["end"]))
                text.append("Length: " + str(result4[a]["end"] - result4[a]["start"] + 1))  # sum also first position
                text.append("ID: " + str(result4[a]["id"]))
                text.append("Chromosome: " + str(result4[a]["seq_region_name"]))

                keyword_j_dict = a  # Using the index number of the list element that corresponds to our gene

            elif res == "/geneCalc":  # Using the resource /geneCalc

                sp = Seq(ins[1])  # Object of the species name
                text.append(sp.results())  # calling the results method
                if "json=1" in self.path:
                    text = text[0].replace("<br><br>", "<br>").rstrip("<br>").split("<br>")  # deleting intros if json=1
                keyword_j_dict = "Calculus about the gene sequence"  # Choosing this phrase as our j_dict keyword

            elif res == "/geneList":  # Using the resource /geneList

                start = ins[3]
                end = ins[5]
                ch = ins[1]
                ENDPOINT6 = "/overlap/region/human/"+ch+":"+start+"-"+end+"?content-type=application/json;feature=gene"
                result5 = client(ENDPOINT6)
                # Searching the name of each gene in the dictionary
                for index in range(len(result5)):
                    text.append(result5[index]["external_name"])

                if len(text) == 0:
                    text.append("<b>"+"There is no gene in the selected region"+"</b>")
                keyword_j_dict = "External name of the genes"

            else:
                page = "error.html"  # If it is not one of the previous resources
                keyword_j_dict = "ERROR: this is a non valid endpoint"
                code = 404  # the request is not Ok!

            # improvement in the server to avoid taking as correct an extra valid parameter. Ex: gene=FRAT1&gene=BRAF
            if res in ["/karyotype", "/chromosomeLength", "/geneSeq", "/geneInfo", "/geneCalc", "/geneList"]:
                i = 2  # we have three different instructions lengths i, j, k that will change with json = 1 parameter
                j = 4
                k = 6
                if "json=1" in self.path:
                    i += 2
                    j += 2
                    k += 2

                # checking the length of the instructions and generating a KeyError if they are not correct
                if len(ins) > i and res != "/chromosomeLength" and res != "/geneList":
                    text.append(client(ENDPOINT0)["e"])
                elif (len(ins) > j and res == "/chromosomeLength") or (len(ins) > k and res == "/geneList"):
                    text.append(client(ENDPOINT0)["e"])

        # Dealing with the main errors
        except ValueError:
            text = ["<b>"+"Incorrect value in the parameter 'limit'"+"<br>"+"Please introduce an integer number"+"</b>"]
            code = 404  # the request is not Ok!
        except TypeError:
            text = ["<b>"+"Sorry, '/listSpecies' only admits the parameter limit alone or with one json"+"</b>"]
            code = 404  # the request is not Ok!
        except KeyError:
            text = ["<b>"+"Incorrect parameters"+"<br>"+"Please review their spelling and the amount required"+"</b>"]
            code = 404  # the request is not Ok!

        # -- printing the request line
        termcolor.cprint(self.requestline, 'green')

        # Generating and sending the response message according to the request

        # -- Modification according to the request
        if "json=1" in self.path:
            h = 'application/json'  # headers content type will vary if we choose the json option
            # Fulfilling the j_dict with the assigned keywords and values
            if y == [0]:
                j_dict[keyword_j_dict] = text[0]  # if we have a list with a unique string and we just want the string
            else:
                j_dict[keyword_j_dict] = text
            contents = json.dumps(j_dict)  # Our contents will be the j_dict in a json object format
        else:
            h = 'text/html'  # If we don't choose json, the answers must be in html format
            # Opening the selected page
            f = open(page, 'r')
            contents = f.read()  # reading the contents of the selected page (main-page, error, response)

            # If the html response page is requested change the word text by the information requested
            if page == "response.html":
                information = ""  # changing our list text into a string
                for string in text:
                    information += string + "<br>"
                contents = contents.replace("text", information)

        # -- Sending the response message
        self.send_response(code)
        self.send_header('Content-Type', h)
        self.send_header('Content-Length', len(str.encode(contents)))
        self.end_headers()
        self.wfile.write(str.encode(contents))


# -- MAIN PROGRAM


socketserver.TCPServer.allow_reuse_address = True  # preventing the error: "Port already in use"

# main loop to attend the user
with socketserver.TCPServer(("", PORT), TestHandler) as httpd:

    # "" means that the program must use the IP address of the computer
    print("Serving at PORT: {}".format(PORT))

    try:
        httpd.serve_forever()  # go on working except if the server is stopped
    except KeyboardInterrupt:
        httpd.server_close()

print("The server is stopped")
