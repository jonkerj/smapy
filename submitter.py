import atexit
import argparse
import datetime
import logging
import os
import os.path
import sys
import time

import attr
import environ
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import yaml

import objects
import client

def now():
	zone = datetime.datetime.now(datetime.timezone.utc).astimezone()
	return datetime.datetime.now().replace(tzinfo=zone.tzinfo)

def convLoglevel(s):
	levels = ['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG']
	if not s in levels:
		raise ValueError(f'{s} is not a valid log level. Valid are {"".join(choices)}')
	return s

@environ.config(prefix="SMAPY")
class Config:
	url = environ.var()
	group = environ.var('usr')
	password = environ.var('sun1sgr3at')
	interval = environ.var(30, converter=int)
	loglevel = environ.var("INFO", converter=convLoglevel)
	influxdb_bucket = environ.var('solar', name='INFLUXDB_V2_BUCKET')

@attr.s
class Submitter(object):
	config = attr.ib()
	log = attr.ib(converter=lambda l: l.getChild('submitter'))
	sma = attr.ib()

	def __attrs_post_init__(self):
		self.log = logging.getLogger('smapy.submitter')

		self.influx_client = InfluxDBClient.from_env_properties()
		self.influx_write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
		self.sma.login()
	
	def work(self):
		self.log.info('Polling and submitting')
		t = now()
		data = self.sma.read()
		p = Point('sma').time(t)
		for field, value, unit in objects.fields(data):
			if value is not None:
				p.field(field, value)
		self.log.debug(f'Result: {p.to_line_protocol()}')

		self.influx_write_api.write(
			bucket = self.config.influxdb_bucket,
			record = p,
		)
	
	def loop(self):
		self.log.info('Looping indefinately')
		while True:
			t0 = time.time()
			s.work()
			nap = t0 + self.config.interval - time.time()
			self.log.debug(f'Sleeping {nap:.1f} seconds')
			time.sleep(nap)
	
	def cleanup(self):
		self.log.debug('Clean up in aisle 5')
		self.sma.logout()

if __name__ == '__main__':
	config = Config.from_environ()
	ch = logging.StreamHandler(sys.stderr)
	ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s:%(name)s: %(message)s"))
	log = logging.getLogger('smapy')
	log.addHandler(ch)
	log.setLevel(config.loglevel)

	sma = client.SMAClient(config, log)
	s = Submitter(config, log, sma)

	# register exit hook. Needed to not overflow sessions
	@atexit.register
	def cleanup():
		s.cleanup()
	
	s.loop()
