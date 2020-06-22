import atexit
import argparse
import datetime
import logging
import time

import attr
import client
import influxdb
import objects
import yaml

def now():
	zone = datetime.datetime.now(datetime.timezone.utc).astimezone()
	return datetime.datetime.now().replace(tzinfo=zone.tzinfo)

@attr.s
class Submitter(object):
	config = attr.ib()

	def __attrs_post_init__(self):
		self.log = logging.getLogger('submitter')
		self.influx = influxdb.InfluxDBClient(**self.config['influxdb'])
		self.sma = client.SMAClient(**self.config['sma'])
		self.sma.login()
	
	def work(self):
		self.log.info('Polling and submitting')
		t = now()
		data = self.sma.read()
		fields = {field: value for field, value, unit in objects.fields(data) if value is not None}
		self.log.debug(f'Result: {fields}')
		self.influx.write_points(
			tags=config['tags'], 
			points=[{'measurement': 'sma', 'time': t, 'fields': fields}]
		)
	
	def loop(self):
		self.log.info('Looping indefinately')
		while True:
			t0 = time.time()
			s.work()
			nap = t0 + interval - time.time()
			self.log.debug(f'Sleeping {nap:.1f} seconds')
			time.sleep(nap)
	
	def cleanup(self):
		self.log.debug('Clean up in aisle 5')
		self.sma.logout()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Submit SMA Webconnect to InfluxDB")
	parser.add_argument("--config", dest='config', help='Config YAML', default='config.yaml')
	parser.add_argument("--debug", dest='level', action='store_const', help='Enable debug logging', const=logging.DEBUG, default=logging.INFO)
	args = parser.parse_args()

	logging.basicConfig(level=args.level)
	with open(args.config, 'r') as f:
		config = yaml.load(f)
	
	interval = int(config['interval'])
	s = Submitter(config)

	# register exit hook. Needed to not overflow sessions
	@atexit.register
	def cleanup():
		s.cleanup()
	
	s.loop()
