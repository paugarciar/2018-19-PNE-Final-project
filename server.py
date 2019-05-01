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
    """function of a common client that asks information using json"""

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


# Seq classes for gene questions
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
        s2 = ""  # empty string to save the percentage results of the following loop

        for b in bases:
            s2 += "The percentage of " + b + " is: " + str(self.perc(b)) + "%" + "<br>"
        return s1 + "<br><br>" + s2


# Class with our Handler that inheritates all his methods and properties
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
        calling_response = self.path.split("?")[0]
        p = (self.path.replace("=", ",")).replace("&", ",")
        ins = p.split(",")  # Making a list of instructions dividing the string in the = and & symbols

        # Some important parameters
        text = ""  # Empty string that will save the response information
        sp = Seq(ins[-1])  # Object used in the genes calculations
        page = "response.html"  # The page will be response except if the endpoint is "/" or it does not exist

        try:
            if self.path == "/":
                page = "main-page.html"

            elif calling_response == "/listSpecies":  # Using the resource /listSpecies

                result0 = client(ENDPOINT0)
                # The variable limit has been created to avoid the error "referenced before assignment"
                limit = ""
                if len(ins) == 2:
                    limit = int(ins[1])
                # Using elif instead of else to avoid sending the list of species with 3 or more parameters
                elif len(ins) == 1:
                    limit = len(result0["species"])
                for index in range(limit):
                    text += result0["species"][index]["name"] + "<br>"

            elif calling_response == "/karyotype":  # Using the resource /karyotype

                ENDPOINT1 = "/info/assembly/"+ins[-1]+"?content-type=application/json"
                result1 = client(ENDPOINT1)
                for chrom in result1["karyotype"]:
                    text += chrom+"<br>"

            elif calling_response == "/chromosomeLength":  # Using the resource /chromosomeLength

                specie = ins[1]
                ch = ins[-1]
                ENDPOINT2 = "/info/assembly/"+specie+"/"+ch+"?content-type=application/json"
                result2 = client(ENDPOINT2)
                text += str(result2["length"])

            elif calling_response == "/geneSeq":  # Using the resource /geneSeq
                text += sp.gene_seq()

            elif calling_response == "/geneInfo":
                id_number = sp.id()
                ENDPOINT5 = "/overlap/id/" + id_number + "?feature=gene;content-type=application/json"
                result4 = client(ENDPOINT5)

                a = ""
                for i in range(len(result4)):
                    if result4[i]["id"] == id_number:
                        a = i
                text += "Start: " + str(result4[a]["start"]) + "<br>"
                text += "End: " + str(result4[a]["end"]) + "<br>"
                text += "Length: " + str(result4[a]["end"] - result4[a]["start"] + 1) + "<br>"
                text += "ID: " + str(result4[a]["id"]) + "<br>"
                text += "Chromosome: " + str(result4[a]["seq_region_name"]) + "<br>"

            elif calling_response == "/geneCalc":  # Using the resource /geneCalc
                text += sp.results()

            elif calling_response == "/geneList":  # Using the resource /geneList

                start = ins[3]
                end = ins[-1]
                ch = ins[1]
                ENDPOINT6 = "/overlap/region/human/"+ch+":"+start+"-"+end+"?content-type=application/json;feature=gene"

                result5 = client(ENDPOINT6)

                for index in range(len(result5)):
                    text += result5[index]["external_name"]+"<br>"

            else:
                page = "error.html"

        # Dealing with some errors
        except ValueError:
            text += "<b>"+"Incorrect value in the parameter 'limit'"+"<br>"+"Please introduce an integer number"+"</b>"
        except TypeError:
            text += "<b>"+"Sorry, the endpoint '/listSpecies' does not admit three or more parameters"+"</b>"
        except KeyError:
            text += "<b>"+"Incorrect parameters"+"<br>"+"Please review their spelling and the amount required"+"</b>"
        except Exception:  # In case there is an error that I haven't detected
            text += "<b>"+"Sorry, an error has been produced"+"<br>"+"Please review the performed actions"+"</b>"

        # -- printing the request line
        termcolor.cprint(self.requestline, 'green')

        f = open(page, 'r')
        contents = f.read()  # reading the contents of the selected page

        # If the html response page is requested change the word text by the text of the user
        if page == "response.html":
            contents = contents.replace("text", text)

        # Generating and sending the response message according to the request
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(contents)))
        self.end_headers()

        # -- sending the body of the response message
        self.wfile.write(str.encode(contents))


# -- MAIN PROGRAM


socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), TestHandler) as httpd:

    # "" means that the program must use the IP address of the computer
    print("Serving at PORT: {}".format(PORT))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

print("The server is stopped")
