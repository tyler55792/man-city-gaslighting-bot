# Man City Gaslighting Bot
As a Liverpool fan, I am very tired of Man City winning. 
So, I decided to build a twitter bot that posts daily celebrations of their greatest losses in history. 
The goal is to slowly gaslight myself into thinking they are bad, and then maybe I will be able to happily watch the premier league again.

[View the twitter account here](link) 👈

## Overview
I uploaded a CSV file with results from every Premier League game in history to an AWS-hosted MySQL database. 
Using AWS Lambda, I created a function that queries this database to find Man City's greatest loss on a given day in history. 
A summary of this loss is then automatically posted to Twitter. 
AWS EventBridge (formerly CloudWatch), triggers this lambda function daily at 8 am MT.

## Note
Currently, my keys and db access information are stored in AWS parameters. 
The more secure choice would be to store this information in AWS Secrets.
Unfortunately, my personal account cannot do this without associated costs.
