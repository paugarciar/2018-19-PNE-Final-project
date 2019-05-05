# Client to verify that the server works properly

import http.client
import json

# Defining the number of port and the IP
PORT = 8000
SERVER = 'localhost'

print("\nConnecting to server: {}:{}\n".format(SERVER, PORT))
while True:
    # The client write data and then it connects to the server and send it
    url_request = input("Please introduce a request in url format: ")

    # Connect with the server
    conn = http.client.HTTPConnection(SERVER, PORT)

    # -- Send the request message, using the GET method.
    conn.request("GET", url_request)

    # -- Read the response message from the server
    r1 = conn.getresponse()

    # -- Print the status line
    print("Response received!: {} {}\n".format(r1.status, r1.reason))

    # -- Reading and decoding the response
    data1 = r1.read().decode("utf-8")

    # -- Create a variable with the data. In case of the json we have to get the information of the object
    if "json=1" in url_request:
        response = json.loads(data1)
    else:
        response = data1

    # -- Printing the response
    print("REQUEST: ", url_request)
    print("CONTENT: ")
    print(response)
    print()
