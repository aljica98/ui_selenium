# This project consists in running a python file consistenly each week to extract open data of Unemployment Insurance Weekly Claim Data from https://oui.doleta.gov/unemploy/claims.asp
The Workflow consists in creating in GCP a Cloud Scheduler job for activating Cloud Pub/Sub messages, one for start and other to stop a VM triggered by Cloud Functions, the code will upload a CSV file to a bucket in Cloud Storage. 

It is very important to change the output directory to your environment and create the folders indicated in the code, remember to adapt also the name of the bucket you are using in the end of the code.

The start and stop python files are for the Cloud Functions, the parameters need to be changed according to your environment.

Requirement.txt are the dependencies and libraries for the cloud function code.

The bash code is the startup script to insert it in the VM where you have the python code, remember to adapt the directory route to your environment.

