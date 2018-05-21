# web-monitor
To run, either use the run_script.py python file or run a bash script run.sh, which prepares a docker environment.
The logs will be written wherever it's specified in config.ini file.
To view the http server interface go to : http://127.0.0.1:5000/
Websites.txt specifies websites to check and string to be present in the response.

Currently implemented:
-Asynchronous, periodic requests to websites specified in websites.txt file
-Checking responses content
-Error handling (connection problems)
-logging to file
-starting a local Flask server
-dockerfile, requirements, config file

What is left to be implemented:
-more advanced content checking
-database under the flask server
-sending request time and result to the flask server
-displaying the results