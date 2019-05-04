import http.server
import http.client
import json
import socketserver
import termcolor

# Server's port
PORT = 8000


# Client

HOSTNAME = "rest.ensembl.org"
ENDPOINT3 = "/lookup/symbol/homo_sapiens/BRCA2?content-type=application/json"
ENDPOINT5 = "/overlap/id/ENSG00000157764?feature=gene;content-type=application/json"

METHOD = "GET"

headers = {'User-Agent': 'http-client'}
conn = http.client.HTTPSConnection(HOSTNAME)


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

        # Assigning to the variable page different html pages names in function of the request
        text = ""
        if self.path == "/":
            page = "main-page.html"

        elif calling_response == "/geneInfo":

            p = (self.path.replace("=", ",")).replace("&", ",")
            ins = p.split(",")  # Making a list of instructions dividing the string in the = and & symbols
            print(ins)

            ENDPOINT3B = ENDPOINT3.replace("BRCA2", ins[-1])
            result3 = client(ENDPOINT3B)

            print(result3["id"])

            ENDPOINT5b = ENDPOINT5.replace("ENSG00000157764", result3["id"])
            result5 = client(ENDPOINT5b)
            for i in range(len(result5)):
                if result5[i]["id"] == result3["id"]:
                    a = i
            print(result5)
            print(a)
            text += "Start: "+str(result5[a]["start"])+"<br>"
            text += "End: "+str(result5[a]["end"])+"<br>"
            text += "Length: " + str(result5[a]["end"]-result5[a]["start"])+"<br>"
            text += "ID: "+str(result5[a]["id"])+"<br>"
            text += "Chromosome: "+str(result5[a]["seq_region_name"])+"<br>"
            page = "response.html"

        else:
            page = "error.html"

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
