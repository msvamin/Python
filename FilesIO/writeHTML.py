__author__ = 'amin'

import webbrowser
# Create a Hello World html file
f = open('helloworld.html','w')

message = """<html>
<head></head>
<body><p>Hello World!</p></body>
</html>"""

f.write(message)
f.close()

# Opening the file
filename = 'C:/Amin/Python/FilesIO/' + 'helloworld.html'
webbrowser.open_new_tab(filename)