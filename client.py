import logging
import urllib.parse
import urllib3
import attr
import requests

class SMAError(Exception):
	pass

class TooManySessions(SMAError):
	pass

class UnexpectedResponse(SMAError):
	pass

@attr.s
class SMAClient(object):
	config = attr.ib()
	log = attr.ib(converter=lambda l: l.getChild('client'))
	session = attr.ib(default=None)

	def __attrs_post_init__(self):
		urllib3.disable_warnings() # SMA uses self-signed certs, no point in warning
	
	def rest(self, uri, params, data):
		url = urllib.parse.urljoin(self.config.url, uri)
		p = data.copy()
		if self.session:
			p['sid'] = self.session
		r = requests.post(url, json=data, params=p, verify=False)
		j = r.json()
		error = j.get('err', None)

		if error:
			if error == 503:
				raise TooManySessions('Too many sessions, inverter returned 503')
			else:
				raise SMAError(f'Unknown error, inverter returned {error}')
		return j

	def login(self):
		self.log.debug('Logging in')
		data = {
			'right': self.config.group,
			'pass': self.config.password,
		}
		r = self.rest('/dyn/login.json', params={}, data=data)
		if not 'result' in r:
			raise UnexpectedResponse('Inverter did not return "result" after login')
			return None
		if not 'sid' in r['result']:
			raise UnexpectedResponse('Inverter did not return session ID')
			return None
		if not r['result']['sid']:
			raise UnexpectedResponse('Inverter returned null session ID. This happens with incorrect credentials')
			return None
		self.session = r['result']['sid']
		return True
	
	def logout(self):
		self.log.debug('Logging out')
		if self.session:
			self.rest('/dyn/logout.json', params={}, data={})
		self.session = None
	
	def read(self):
		self.log.debug('Fetching data')
		if not self.session:
			self.login()
		return self.rest('/dyn/getAllOnlValues.json', params={}, data={'destDev': []})
