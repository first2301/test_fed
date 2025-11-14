Step 1: Set Up
Clone the Flower repository and change to the distributed directory:

$ git clone --depth=1 --branch v1.23.0 https://github.com/adap/flower.git
$ cd flower/framework/docker/distributed

First, set the environment variable SUPERLINK_IP with the IP address from the remote machine. For example, if the IP is 192.168.2.33, execute:

$ export SUPERLINK_IP=192.168.2.33
Next, generate the self-signed certificates:

$ docker compose -f certs.yml -f ../complete/certs.yml run --rm --build gen-certs


Step 2: Copy the Server Compose Files
Use the method that works best for you to copy the server directory, the certificates, and the pyproject.toml file of your Flower project to the remote machine.

For example, you can use scp to copy the directories:

$ scp -r ./server \
       ./superlink-certificates \
       ../../../examples/quickstart-sklearn-tabular/pyproject.toml remote:~/distributed


Step 3: Start the Flower Server Components
Log into the remote machine using ssh and run the following command to start the SuperLink and ServerApp services:

 $ ssh <your-remote-machine>
 # In your remote machine
 $ cd <path-to-``distributed``-directory>
 $ export PROJECT_DIR=../
 $ docker compose -f server/compose.yml up --build -d