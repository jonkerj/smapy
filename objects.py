#!/usr/bin/env python3

import json
import logging
import sys

def first_value(tag):
	def fn(results):
		if tag in results:
			return results[tag]['1'][0]['val']
		raise KeyError(f'Tag {tag} not present')
	return fn

def second_value(tag):
	def fn(results):
		if tag in results:
			return results[tag]['1'][1]['val']
		raise KeyError(f'Tag {tag} not present')
	return fn

def scale(factor):
	return lambda x: x * factor

sensors = [
	('ac_power',				first_value('6100_40263F00'),	scale(1.0), 'W'),
	('ac_active_power_l1',			first_value('6100_40464000'),	scale(1.0), 'W'),
	('ac_phase_voltage_l1',			first_value('6100_00464800'),	scale(0.01), 'V'),
	('ac_phase_current_l1',			first_value('6100_40465300'),	scale(0.001), 'A'),
	('ac_grid_frequency',			first_value('6100_00465700'),	scale(0.01), 'Hz'),
	('ac_pv_generated_power',		first_value('6100_0046C200'),	scale(1.0), 'W'),
	('ac_phase_total_current',		first_value('6100_00664F00'),	scale(0.001), 'A'),
	('ac_displacement_power_factor',	first_value('6100_00665900'),	scale(0.001), ''), # heb ik die?
	('ac_eei_displacement_power_factor',	first_value('6100_40665B00'),	scale(0.001), ''), # heb ik die?
	('ac_reactive_power',			first_value('6100_40665F00'),	scale(1.0), 'VAR'), # heb ik die?
	('ac_reactive_power_l1',		first_value('6100_40666000'),	scale(1.0), 'VAR'), # heb ik die?
	('ac_apparent_power',			first_value('6100_40666700'),	scale(1.0), 'VA'), # heb ik die?
	('ac_apparent_power_l1',		first_value('6100_40666800'),	scale(1.0), 'VA'), # heb ik die?
	('dc_power_a',				first_value('6380_40251E00'),	scale(1.0), 'W'),
	('dc_power_b',				second_value('6380_40251E00'),	scale(1.0), 'W'),
	('dc_voltage_a',			first_value('6380_40451F00'),	scale(0.01), 'V'),
	('dc_voltage_b',			second_value('6380_40451F00'),	scale(0.01), 'V'),
	('dc_current_a',			first_value('6380_40452100'),	scale(0.001), 'A'),
	('dc_current_b',			second_value('6380_40452100'),	scale(0.001), 'A'),
	('ac_total_yield',			first_value('6400_00260100'),	scale(3600.0), 'J'),
	('ac_daily_yield',			first_value('6400_00262200'),	scale(3600.0), 'J'),
]

def fields(data):
	serial, results = next(iter(data['result'].items()), ('', {}))
	for field, extract, transform, unit in sensors:
		try:
			r = extract(results)
		except KeyError:
			continue
		if r is not None:
			v = transform(r)
			yield (field, v, unit)
