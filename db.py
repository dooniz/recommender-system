﻿# !/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
#
# (c) Copyright University of Southampton, 2021
#
# Copyright in this software belongs to University of Southampton,
# Highfield, University Road, Southampton SO17 1BJ
#
# Created By : Stuart E. Middleton
# Created Date : 2021/02/11
# Project : Teaching
#
######################################################################

from __future__ import absolute_import, division, print_function, unicode_literals

import sys, codecs, json, math, time, warnings, logging, os, shutil, subprocess, sqlite3, traceback, random

LOG_FORMAT = ('%(levelname) -s %(asctime)s %(message)s')
logger = logging.getLogger( __name__ )
logging.basicConfig( level=logging.INFO, format=LOG_FORMAT )
logger.info('logging started')

'''

# Setup a ECS VM (which will run RedHat Enterprise 7 and therefore need Python 3.6)
# Copy comp3208-train-small.csv file to the same folder as db_example.py

sudo yum install java-1.8.0-openjdk-devel
sudo yum install python36 python36-pip
sudo python3.6 -m pip install --upgrade pip
sqlite3 comp3208.db
	.quit
python3.6 db_example.py

'''

if __name__ == '__main__':

	logger.info( 'loading training set and creating sqlite3 database' )

	# connect to database (using sqlite3 lib built into python)
	conn = sqlite3.connect('example_table.db')

	#
	# comp3208-test-small.csv
	#
	readHandle = codecs.open( 'comp3208-train-small.csv', 'r', 'utf-8', errors = 'replace' )
	listLines = readHandle.readlines()
	readHandle.close()

	c = conn.cursor()
	c.execute( 'CREATE TABLE IF NOT EXISTS example_table (UserID INT, ItemID INT, Rating FLOAT, PredRating FLOAT)' )
	conn.commit()

	c.execute( 'DELETE FROM example_table' )
	conn.commit()

	for strLine in listLines :
		if len(strLine.strip()) > 0 :
			# userid, itemid, rating, timestamp
			listParts = strLine.strip().split(',')
			if len(listParts) == 4 :
				# insert training set into table with a completely random predicted rating
				c.execute( 'INSERT INTO example_table VALUES (?,?,?,?)', (listParts[0], listParts[1], listParts[2], random.random() * 5.0) )
			else :
				raise Exception( 'failed to parse csv : ' + repr(listParts) )
	conn.commit()

	c.execute( 'CREATE INDEX IF NOT EXISTS example_table_index on example_table (UserID, ItemID)' )
	conn.commit()

	# run SQL to compute MSE
	c.execute('SELECT AVG(ABS(Rating-PredRating)) FROM example_table WHERE PredRating IS NOT NULL')
	row = c.fetchone()
	nMSE = float( row[0] )

	logger.info( 'example MSE for random prediction = ' + str(nMSE) )

	# run SQL to compute MSE against a fixed average rating
	c.execute('SELECT AVG(ABS(Rating-3.53)) FROM example_table WHERE PredRating IS NOT NULL')
	row = c.fetchone()
	nMSE = float( row[0] )

	logger.info( 'example MSE for user average of 3.53 prediction = ' + str(nMSE) )

	# close database connection
	c.close()
	conn.close()

