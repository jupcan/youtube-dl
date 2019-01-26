# [youtube-dl](/reqs/ytdl.pdf)
[![uclm](https://img.shields.io/badge/uclm-project-red.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAYAAAA71pVKAAAC9UlEQVR42o3S3UtTYRwH8F//QhBE3WT0elGr6CZUCLzoRUQt6ibICrESS1MDi7pJwcSXgsCGlG+1LFFzzpzONqduTp3TqVO36V7OzubZ2TznbDvn7NW5nmlXWdADPzg8/D6c3/N9HohSDPCrDgg53bDJByERj0OEpCCEE8cjXlrJaBbOcys2iHpp1OOBgN4MaG/b/BXHfKxgkwuaNvkQE6X8WNDiTI16qP/AicTlMElPeeXTtdTY7G1Kpa/iLU5dnONvhHDyH9hBJGEGu2RV2t93PWaXrb2xAO/kTJgMb5EUM9MGWZQJ5PrnTH9gMwYx2n865PLOrr5uK+XXcLV/YfUD3t5fFFgwN0Y89JzlTUcxb3PNc2YsjVHrdzAKBX1gh+KhsIXokgtJqbopxvIvEa7y600i38xSnXd4qpwa1zcTvcqGqNdHMBPzpzijHSDGcic2WV4Xj0QTGwptBd4meejTGb+gKcS+acMD1mj7Ro3OfcWE3fddnbJnKMRExMuYglbXWUCjjCTQitEBu2dQU05rFp6gsOrJftXzqI9d8gxpajzDk9XUqK6MVs+Xx9igLtnPmewz4GiRnEFprmxtbSXWO4crUCgVrs7hfDTyeLIpiBG29a6fBTxGlPkX116grQBrwnBHq+QCOD9LwflpQIDSNVAjM8IQSVWQfWN1lgZRQRLjH8WF7h5FJW9brww63I2c2WG0N/WkOUVSAHJADZ6BCXAIu/eiP9ehs79Do97xzxrbk5hdsYo9UlVejAnU0lOGFnvT932ubsW2A01WMUxml8Bo2l3QZD7ai+6wnLc5XyGnSuyslTC5UYOOUTJz/enBifR80GaXgjanDGAoJRMGU67Cj/0ZMJZ+DyzVrYdplT4PocXf2B4wWIrwVslJzcUCkB+4AiNHc1HlAMgFN7dr6EgWqC8VgrVeBI7mPkBPUZuUYfeGlehR7HGhbKYzi0F57BqMn7uVrN3Y9rYD0HMEontE4NMuK7yyyVS3WAmujqFd+Bcdh3NlWlsAggAAAABJRU5ErkJggg==&longCache=true&colorA=b30135&colorB=555555&style=for-the-badge)](https://www.uclm.es)  
distributed systems lab project  
## information  
the project files can be divided into 3 different types:
- **zeroc ice files**: *locator.config* so that the client knows the server address, *node[n]* containing the path to the corresponding node data as well as the .txt icestdout file and the *xml* beeing this one the core of the project with all the information of the nodes running, indirect communication between them and use of icestorm service to communicate.
- **python scripts**: *downloader.ice* given by the teacher and containing the methods to be called, aka the interface we have to use, *synctimer.py* a client invocating methods through a timer to sync downloaderscheduler objects using the synctopic created, *factory.py* which contains the schedulerfactory -a server waiting a request from synctimer and from the client- and *client.py* being a normal client with a proxy and allowing us to make use of the interface methods.  
- **makefile**: to make the whole project execution and all the other stuff an easier task.

*when we use the method *make* we create an downloaderscheduler object through schedulerfactory that allow us to request downloads, transferences, songs lists etc. and when using *kill* we remove the aforemention previously created things.

## installation
[**zeroc ice**](https://doc.zeroc.com/ice/3.7/release-notes/using-the-python-distribution) python client from pip source distribution
```
pip3 install zeroc-ice
```
[**youtube-dl**](https://rg3.github.io/youtube-dl/) command-line program to download videos from websites
```
sudo apt-get install youtube-dl
```
