import re
import socket

import select


def service_client(new_socket, request):
    """Process the client http request"""

    request_lines = request.splitlines()
    print("")
    print(">" * 20)
    print(request_lines)

    # GET /index.html HTTP/1.1
    # get post put del
    file_name = ""
    # Regular expression to get the file name of request
    ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
    if ret:
        file_name = ret.group(1)
        # print("*"*50, file_name)
        if file_name == "/":
            file_name = "/index.html"

    # Response to the request from brower

    try:
        f = open("./html" + file_name, "rb")
    except:
        response = "HTTP/1.1 404 NOT FOUND\r\n"
        response += "\r\n"
        response += "------file not found-----"
        new_socket.send(response.encode("utf-8"))
    else:
        html_content = f.read()
        f.close()

        response_body = html_content

        response_header = "HTTP/1.1 200 OK\r\n"
        response_header += "Content-Length:%d\r\n" % len(response_body)
        response_header += "\r\n"

        response = response_header.encode("utf-8") + response_body

        new_socket.send(response)


def main():
    """Main process"""

    # 1. Create Socket
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 2. Bind ip and port
    tcp_server_socket.bind(("", 7890))

    # 3. Set to listening mode
    tcp_server_socket.listen(128)
    tcp_server_socket.setblocking(False)  # 将套接字变为非堵塞

    # Create an epoll object 
    epl = select.epoll()

    # Register listening socket to epoll 
    epl.register(tcp_server_socket.fileno(), select.EPOLLIN)
    # Create a dictionary, key: socket.fileno, value: socket object 
    fd_event_dict = dict()

    while True:

        # OS watch the request, once it arrives, OS will notify to application 
        fd_event_list = epl.poll()

        # [(fd, event), (socket file discriptor, event type)]
        for fd, event in fd_event_list:
            # Wait for the new client conncetion
            if fd == tcp_server_socket.fileno():
                new_socket, client_addr = tcp_server_socket.accept()
                epl.register(new_socket.fileno(), select.EPOLLIN)
                fd_event_dict[new_socket.fileno()] = new_socket
            elif event == select.EPOLLIN:
                # Check the request data
                recv_data = fd_event_dict[fd].recv(1024).decode("utf-8")
                if recv_data:
                    service_client(fd_event_dict[fd], recv_data)
                else:
                    fd_event_dict[fd].close()
                    epl.unregister(fd)
                    del fd_event_dict[fd]

    # Close the listening socket
    tcp_server_socket.close()


if __name__ == "__main__":
    main()
