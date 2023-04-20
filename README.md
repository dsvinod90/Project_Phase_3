---
Author: Vinod Dalavai, Samson Zhang, Ramparsad Kokkula
Date: 20th April 2023
---
# CSCI-620: Project Phase 3

## Pre-requisites
In order to run the main file, you need to have the following in your machine:
* Python (> version 3)
* PostgreSQL (> version 15 preferable)
* Tables from the previous assignments related to Spotify dataset
___

## Syntax
```shell
python main.py -H <hostname> -D <database_name> [-S <minimum_support>]
```
Default value for minimum support is 5. This can be changed by providing a custom minimum support using the optional `-S` flag.
