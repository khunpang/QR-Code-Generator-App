# run this project

First, install docker and run this command.

> docker build -t qr-code-generator-image .

Then

> docker run -p 80:80 -e MODULE_NAME="backend.main" qr-code-gen-app
