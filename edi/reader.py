import json
from typing import Union, List
from pathlib import Path

from badx12 import Parser

class Reader:

	def __init__(self) -> None:
		self.document = []
		self.header = []
		self.lines = []
		self.footer = []
		self.filename = ''
		self.reader_document_type = "0"

	def _validate_document(self, document:str) -> Union[List, OSError, TypeError]:
		try:
			is_file = Path(document).is_file()
		except AttributeError and OSError:
			is_file = False

		if not isinstance(document, str) and not is_file:
			raise TypeError(
				f"{document}() expects document to be of type str or x12 file, "
				f"got {type(document)}"
			)

		if is_file:
			self.filename = document.split('/')[-1]
			with open(document, 'r', encoding="ISO-8859-1") as reader:
				lines = reader.readlines()
				if len(lines) == 1:
					lines = [f"{x}~\n" for x in lines[0].split('~')]
				self.document = [x.split('^') for x in lines]
				if len(self.document[0]) == 1:
					self.document = [x.split('*') for x in lines]
				return self.document
		raise OSError(f"{document} is not a file")

	def _get_key_position(self, key:str, array:List=None, first:bool=True) -> Union[int, List]:
		array = self.document if not array else array
		keys=[i for i, e in enumerate(array) if e[0] == key]
		if first and keys:
			return keys[0]
		return keys

	def _get_lines_by_indexes(self, start:int=0, stop:int=None) -> List:
		stop = len(self.document) if not stop else stop
		return self.document[start:stop]

	def _parse_header(self) -> None:
		try:
			self.header = self._get_lines_by_indexes(
				stop=self._get_key_position('PO1')
			)
		except Exception as e:
			raise Exception(f"Erreur parse header: {e}")

	def _parse_lines(self) -> None:
		try:
			self.lines = self._get_lines_by_indexes(
				self._get_key_position('PO1'), 
				self._get_key_position('CTT')
			)
		except Exception as e:
			raise Exception(f"Erreur parse line: {e}")

	def _parse_footer(self) -> None:
		try:
			self.footer = self._get_lines_by_indexes(
				self._get_key_position('CTT')
			)
		except Exception as e:
			raise Exception(f"Erreur parse footer: {e}")


	def _sanitize_val(self, payload:str) -> dict:
		for key, val in payload.items():
			payload[key] = val.replace('~\n','')
		return payload

	def _get_address_lines(self, type:str) -> None:
		if type:
			addresses_pos = self._get_key_position('N1',self.header, False)
			for x in addresses_pos:
				line = self.header[x]
				if line[1] == type:
					index = addresses_pos.index(x)
					if index == len(addresses_pos):
						index = len(self.header)-1

					return self.header[x:addresses_pos[index+1]]
					
	def _parse_address(self, lines:List) -> dict:
		address = {
			'code':'',
			'name':'',
			'address': '',
			'city': '',
			'province':'',
			'zip': '',
		}
		for line in lines:
			if line[0] == 'N1':
				address['code'] = line[4]
				address['name'] = line[2]
			if line[0] == 'N3':
				address['address'] = line[1]
			if line[0] == 'N4':
				address['city'] = line[1]
				address['province'] = line[2]
				address['zip'] = line[3]
		address = self._sanitize_val(address)
		return address
	
	def parse(self, path:str) -> List:
		try:
			self._validate_document(path)
		except Exception as e:
			raise Exception(f"DOCUMENT NOT VALID {e}")

		if self.check_document_type() == 997:
			return self.document
		return self.parse_document()

	def check_document_type(self) -> int:
		line_pos = self._get_key_position('ST')
		self.reader_document_type = self._get_lines_by_indexes(line_pos)[0][1]
		return int(self.reader_document_type)
	
	def parse_document(self) -> List:
		self._parse_header()
		self._parse_lines()
		self._parse_footer()
		return self.document
	
	def get_bill_to(self) -> dict:
		address_lines = self._get_address_lines('BT')
		return self._parse_address(address_lines)

	def get_ship_to(self) -> dict:
		address_lines = self._get_address_lines('ST')
		return self._parse_address(address_lines)

	def get_lines(self) -> List:
		_rtn = []
		_line = {}
		first_run = True
		for line in self.lines:
			if line[0] == 'PO1':
				if not first_run:
					_rtn.append(_line)
				first_run = False
				_line = {}

				_line['code'] = line[7]
				_line['line_num'] = line[1]
				_line['qty'] = line[2]
				_line['uom'] = line[3]
				_line['uprix'] = line[4]
				try:
					_line['buyer_in'] = line[9]
				except:
					pass

			if line[0] == 'PID':
				if 'description' in _line:
					_line['description'] = f"{_line['description']}\n{line[-1]}"
				else:
					_line['description'] = line[-1]
			if line[0] == 'DTM':
				_line['dtm'] = line[-1]
		if not first_run:
			_rtn.append(_line)
		
		return [self._sanitize_val(x) for x in _rtn]

	def get_messages(self) -> str:
		return '\n'.join(
			[
				self._sanitize_val({'msg':self.document[x][-1]})['msg'] 
				for x in self._get_key_position(key='MSG', first=False)
			]
		)

	def get_document(self) -> str:
		try:
			beg = self.header[self._get_key_position('BEG', self.header)]
			ref_pos = self._get_key_position('REF', self.header)
			ref = ['','','']
			if ref_pos:
				ref = self.header[ref_pos]
			code = self.get_bill_to()['code']
			if "-" in code:
				code = code.split('-')[0]
			return {
				'customer': code,
				'reference': beg[3],
				'comments': self.get_messages(),
				'date': beg[5][:-2],
				'po_ref': ref[2],
			}
		except Exception as e:
			raise Exception(f"Error parse Document {e}")
