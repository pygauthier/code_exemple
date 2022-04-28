import os
import datetime
import json
import glob
import numpy as np
from pandas.tseries.offsets import BDay

import settings

from .sftp import SFTP
from .reader import Reader

from libraries.teamsBot import Bot
from libraries.utilities import Utilities as Util

from models.Mongo.edimsss import EDIMSSSLogs, EDIMSSSDocuments, EDIMSSSMultiple
from models.Mongo.indexer import IndexAddresses

from models.Mongo.api import Webhooks

from models.BusinessPartners.BusinessPartners import BusinessPartners
from models.Documents.Orders import Orders
from models.Documents.DeliveryNotes import DeliveryNotes
from models.Documents.Invoices import Invoices

from controllers.edi.purchase_order_acknowledgment import PurchaseOrderAcknowledgment
from controllers.edi.ship_notice import ShipNotice
from controllers.edi.invoice import Invoice


class MSSS(SFTP, Reader):

	def __init__(self) -> None:
		super().__init__()
		self.webhook = Webhooks.objects(code="edi").first()
		self.bot = Bot()

	def mv_file(self, file="*"):
		directory = f"{self.local_process_path}/import"
		xmls = glob.glob(f"{self.local_download_path}/{file}")
		for xml_to_process in xmls:
			Util.check_directory(directory)
			Util.move(xml_to_process, f"{directory}/{file}")

		return True

	def get_ten_percent(self, uprix, add=True):
		percent = (10 * uprix) / 100.0
		if add:
			percent_plus = round(percent + uprix, 2)
			return percent_plus
		else:
			percent_minus = round(percent - uprix, 2)
			return percent_minus

	def check_for_multiple_orders(self, path=None):
		line_codes = [x[0] for x in self.document]
		is_splitted = False
		if line_codes.count('ST') > 1:
			new_docs = []
			splitted_doc = []
			common_header = [x for x in self.document if x[0] in ('ISA', 'GS')]
			common_footer = [x for x in self.document if x[0] in ('GE', 'IEA')]

			splitted_doc = [*common_header]
			for line in self.document:
				if line[0] not in ('ISA', 'GS'):
					splitted_doc.append(line)
				if line[0] == 'SE':
					# last line of an order
					splitted_doc = splitted_doc + common_footer
					new_docs.append([*splitted_doc])
					splitted_doc.clear()
					splitted_doc = [*common_header]

			file_number = 2
			for new_doc in new_docs[1:]:
				file_path = f"{path}-{file_number}"
				filename = file_path.split('/')[-1]
				log = EDIMSSSLogs.objects.filter(filename=filename)
				if not os.path.isfile(file_path) and not log:
					is_splitted = True
					_rtn = []
					for val in new_doc:
						_rtn.append("*".join(val))
					str_return = "".join(_rtn)
			
					file = open(file_path, 'a', encoding="ISO-8859-1")
					file.write(str_return)
					file.close()
					log = EDIMSSSLogs()
					log.filename = filename
					log.download = datetime.datetime.now()
					log.save()


					doc = EDIMSSSDocuments()
					doc.filename = filename
					doc.download = datetime.datetime.now()
					doc.save()

				file_number += 1
		return is_splitted

	def process_files(self, path, force_add=False):
		filename = path.split('/')[-1]
		log = EDIMSSSLogs.objects.filter(filename=filename).first()
		if log:
			if log.payload:
				return self.return_error(filename, f"Document a ete traite {log.date}")
		del log
		try:
			self.parse(path)
		except Exception as e:
			return self.return_error(filename, f"{e}")

		if self.check_for_multiple_orders(path):
			return self.return_error(path, "Document a ete divise en plusieurs fichiers")
		if self.check_document_type() == 997:
			self.mv_file(filename)
			directory = f"{self.local_process_path}/import"
			return self.return_error(path, "Document 997 transfere automatiquement")

		funcdata = {
 			'document': "get_document",
 			'bill_to':"get_bill_to",
 			'ship_to':"get_ship_to",
 			'lines':"get_lines",
 		}
		parsed_data = {
			'filename': filename,
		}
		for key, func_name in funcdata.items():
			try:
				parsed_data[key] = getattr(self, func_name)()
			except Exception as e:
				return self.return_error(filename, f"{func_name} : {e}")

		document = parsed_data['document']
		customer = BusinessPartners(document['customer'])
		sapDocument = Orders()
		row = []
		for document_line in parsed_data['lines']:
			price = sapDocument.get_price(
				document['customer'], document_line['code']
			)
			if not price:
				return self.return_error(path, f"ITEM NOT FOUND: {document_line['code']}")

			lowest_price = price['PrixCible']
			if price['MinQuote'] and price['MinQuote'] < lowest_price:
				lowest_price = float(price['MinQuote'])
			
			multiple = EDIMSSSMultiple.objects.filter(cardcode=document['customer'], itemcode=document_line['code'])
			if multiple:
				if len(multiple) > 1:
					filter_uom = multiple.filter(uom=document_line['uom'])
					filter_blank = multiple.filter(uom='')
					filtered_multiple = filter_uom if filter_uom else filter_blank
					if filtered_multiple:
						qty = filtered_multiple.first().multiple  * int(document_line['qty'])
					else:
						return self.return_error(
							path,
							f"PRICE ERROR IN ITEM: {document_line['code']}, UoM {document_line['uom']} OR UoM '' NOT FOUND",
						)
				else:
					filtered_multiple = multiple.first()
					qty = filtered_multiple.multiple * int(document_line['qty'])
			else:
				# Si différence <10%
				# on met direct la qté EDI comme qté de commande SAP
				qty = document_line['qty']
				uprix = float(document_line['uprix'])
				percent_plus = self.get_ten_percent(uprix)

				# Si leur prix est + grand de 10% ou plus que notre prix cible unitaire:
				if percent_plus > price['PrixCible']:

					# Divise le prix EDI par le NumInBuy
					num_in_by_uprix = round(uprix / int(price['NumInBuy']), 2)
					num_in_by_uprix_percent = num_in_by_uprix- price['PrixCible']
					# Si différence absolue <10%
					# on va multiplié la qté EDI par le NumInBuy comme qté de commande SAP
					différence = num_in_by_uprix_percent / price['PrixCible']
					if différence <= 0.25:
						qty = int(document_line['qty']) * int(price['NumInBuy'])
					else:
						# Sinon on divise le prix EDI par le OrdrMulti
						order_multi_uprix = uprix / int(price['OrdrMulti'])
						order_multi_uprix_percent = self.get_ten_percent(order_multi_uprix)

						# Si différence absolue <10%
						# on va multiplié la qté EDI par le OrderMulti comme qté de commande SAP
						if order_multi_uprix_percent >= price['PrixCible']: 
							qty = int(document_line['qty']) * int(price['OrdrMulti'])
						else:
							return self.return_error(
								path, 
								f"PRICE ERROR IN ITEM: {document_line['code']}, QTY:{document_line['qty']}, Uprix:{document_line['uprix']}"
							)

			line_to_sap = {
				"ItemCode": document_line['code'],
				"Quantity": qty,
				"UnitPrice": lowest_price,
				'WarehouseCode': '100',
				'LineNum': int(document_line['line_num'])-1,
				'LineStatus': 'O',
				'U_WebOrderItemId': document_line['line_num']
			}
			document_line['price'] = price
			row.append(line_to_sap)

		mongo_addresses = IndexAddresses.objects(sap=str(document['customer'])).all()
		addr_pk = parsed_data['ship_to']['code'].replace(str(document['customer']), '').replace('-','')
		if not addr_pk:
			return self.return_error(path, f"SHIP TO ADDRESS NOT FOUND {parsed_data['ship_to']}")
		mongo_address = mongo_addresses.filter(addr_pk=addr_pk).first()

		today = datetime.datetime.today()
		date = today + BDay(2)

		Document = {
			"row": [
				{
					"CardCode": document['customer'],
					"NumAtCard": document['reference'],
					"Comments": document['comments'] or '',
					"DocDueDate": date.strftime('%Y-%m-%d'),
					"ShipToCode": mongo_address.reference['Address'] or '' if mongo_address else '',
					"TransportationCode": 126,
					"U_nwr_Tag": f"EDI_{filename}",
				}
			]
		}
		transport_code = customer.get_password()
		if transport_code:
			Document['row'][0]['U_NWR_COMPTE'] = transport_code['Password']

		sapDocument.forceAdd = True
		this = sapDocument.prepare_array()
		this['Content'] = [
			{
				'AdmInfo': {'Object': sapDocument.objetSAP},
				'Documents': Document,
				"Document_Lines": {"row": row}
			}
		]
		this["GetNewId"] = True

		if force_add:
			log = EDIMSSSLogs.objects.filter(filename=filename).first()
			if not log:
				log = EDIMSSSLogs()
			log.filename = filename
			log.download = datetime.datetime.now()
			log.document_850 = self.document
			log.payload = [this]
			save = sapDocument.api.saveBatch([this])
			log.response = [save]
			log.process_date = datetime.datetime.now()
			log.save()

			follow = EDIMSSSDocuments.objects.filter(filename=filename).first()
			if not follow:
				follow = EDIMSSSDocuments()
				follow.filename = filename
				follow.download = datetime.datetime.now()
				follow.save()

			for key, val in json.loads(save).items():
				if val[0]["typeErreur"] == 'Succ':
					if key and follow:
						follow.order = key
						follow.save()
					# 855 ICI
					poa = PurchaseOrderAcknowledgment(
						reader=self,
						sap=sapDocument.get_document_with_lines(key)
					)
					str_return, send_report = poa.create(transfert=force_add)
					if send_report:
						log.document_855 = poa.get_document()
						log.save()

					# send notification
					self.bot.send(self.webhook.url, f"855 - {filename} - {key}")
					
					# transfert File to folder
					self.mv_file(filename)
			del follow
			del log
			return save
		else:
			return {
				'file_name': path.split('/')[-1],
				'to_sap': this,
				'show_button': True,
				'parsed_data': parsed_data,
				'file': {
					'header': self.header,
					'lines': self.lines,
					'footer': self.footer
				}
			}

	def list_files(self):
		return self._list_remote_file(self.remote_download_path)

	def notify_files(self):
		files = self.list_files()
		s = ""
		print(f'len({len(files)})')
		if len(files) > 1:
			s = "s"
		if len(files):
			self.bot.send(self.webhook.url, f"{len(files)} fichier{s} disponible{s}:<br>{'<br>'.join(files)}")
			return True
		return False

	def import_files(self,):
		files_to_get = self._list_remote_file(self.remote_download_path)
		files_existing = self._list_local_file(self.local_download_path)
		self.get_files()
		for file in [*files_to_get, *files_existing]:
			log = EDIMSSSLogs.objects.filter(filename=file).first()
			if not log:
				log = EDIMSSSLogs()
			log.filename = file
			log.download = datetime.datetime.now()
			local = f"{self.local_download_path}/{file}"
			remote = f"{self.remote_download_path}/{file}"
			try:
				os.stat(local)
				log.download = datetime.datetime.now()
			except Exception as e:
				Bot().errorSappy(f"FILE NOT DOWNLOADED {remote}")
				log.errors = {**log.errors, 'import_files': e}
			log.save()

		self.local_files = self._list_local_file(self.local_download_path)
		return self._list_local_file(self.local_download_path)

	def loop_files(self, filename: str = None, force: bool = False):
		_return = []
		for file in self._list_local_file(self.local_download_path):
			if not filename or filename == file:
				try:
					local = f"{self.local_download_path}/{file}"
					_return.append(self.process_files(local, force))
				except OSError:
					print(f'Error in file {file}')

		return _return

	def import_routine(self, send:bool = False) -> None:
		for file in self.import_files():
			self.loop_files(file, send)
		
	def create_delivery_notice(self, sap, document, force:bool=False):
		follow = document
		log = EDIMSSSLogs.objects.get(filename=follow.filename)
		self.document = log.document_850
		self.parse_document()
		notice = ShipNotice(reader=self, sap=sap)
		notice.filename = document.filename
		str_return, send_report = notice.create(force)
		if send_report and force:
			log.document_856.append(notice.get_document())
			log.save()
			self.bot.send(self.webhook.url, f"856 - {follow.filename} - {notice.sap['doc']['DocNum']}")
			return True, notice.get_document()
		return False, None

	def create_invoice(self, sap, document, force:bool=False):
		follow = document
		log = EDIMSSSLogs.objects.get(filename=follow.filename)
		self.document = log.document_850
		self.parse_document()
		invoice = Invoice(reader=self, sap=sap)
		invoice.filename = document.filename
		str_return, send_report = invoice.create(force)
		if send_report and force:
			log.document_810.append(invoice.get_document())
			log.save()
			self.bot.send(self.webhook.url, f"810 - {follow.filename} - {invoice.sap['doc']['DocNum']}")
			return True, invoice.get_document()
		return False, None

	def check_for_deliveries(self, document=None, docs=None, force=False) -> None:
		new_odln = []
		odln_list = docs['ODLN_List'].split(',')
		if odln_list and docs['ODLN_List'] != '':
			new_odln = [int(x) for x in odln_list if int(x) not in document.deliveries]
		
		if new_odln:
			self.bot.send(self.webhook.url, f"{document.filename} - Nouvelle(s) expédition(s) à créer")
			# SEND NOTICE

		for odln in new_odln:
			sap = DeliveryNotes().get_document_with_lines(odln)
			is_process, document_856 = self.create_delivery_notice(sap, document, force)
			if is_process:
				document.deliveries.append(odln)
				document.save()

	def check_for_invoices(self, document=None, docs=None, force=False) -> None:
		new_oinv = []
		oinv_list = docs['OINV_List'].split(',')
		if oinv_list and docs['OINV_List'] != '':
			new_oinv = [int(x) for x in oinv_list if int(x) not in document.invoices]
		
		if new_oinv:
			self.bot.send(self.webhook.url, f"{document.filename} - Nouvelle(s) facture(s) à créer")

		for oinv in new_oinv:
			sap = Invoices().get_document_with_lines(oinv)
			is_process, document_810 = self.create_invoice(sap, document, force)
			if is_process:
				document.invoices.append(oinv)
				document.save()

	def check_close_doc(self, document=None, docs=None, force=False) -> None:
		if force:
			if docs['Stat'] == 'C':
				document.is_complete = True
				document.save()

	def check_for_docs_next_step(self, force:bool=False) -> None:
		for document in EDIMSSSDocuments.objects.filter(is_complete=False):
			docs = None
			if document.order:
				docs = Orders().get_ordr_ref_docs(document.order)
			if docs:
				print(docs)
				# CREATE DELIVERIES
				self.check_for_deliveries(document, docs, force)

				# CREATE INVOICES
				self.check_for_invoices(document, docs, force)

				# Close doc
				self.check_close_doc(document, docs, force)

	def return_error(self, path, message):
		return {
			'file_name': path.split('/')[-1],
			'to_sap': message,
			'parsed_data': [],
			'show_button': False,
			'file': {
				'header': [],
				'lines': [],
				'footer': []
			}
		}

	"""
		Pour re exporté des fichiers déjà traité.
		Ne pas executé les 3 tests dans la meme "run" python
		ca crée un bug que tous les fichier sont vide.

		les docEntry sont trouvable dans le EDIMSSSDocuments
		MSSS().test_855(<Order_DocEntry>)
		MSSS().test_856(<Delivery_DocEntry>, EDIMSSSDocuments.objects.get(order=<Order_DocEntry>))
		MSSS().test_810(<Invoice_DocEntry>, EDIMSSSDocuments.objects.get(order=<Order_DocEntry>))
	"""

	def test_855(self, key, force=True):
		doc = EDIMSSSDocuments.objects.get(order=key)
		log = EDIMSSSLogs.objects.get(filename=doc.filename)
		date= f"{log.process_date}"[:10]
		path = f"{settings.storage}/edimsss/inbound/process/{date}/import/{log.filename}"
		self.process_files(path)
		sapDocument = Orders()
		poa = PurchaseOrderAcknowledgment(
			reader=self,
			sap=sapDocument.get_document_with_lines(key)
		)
		str_return, send_report = poa.create(transfert=force)
		#print('test_855, str_return, send_report', str_return, send_report)
	
	def test_856(self, key, document, force=True):
		sap = DeliveryNotes().get_document_with_lines(key)
		is_process, document_856 = self.create_delivery_notice(sap, document, force)
		#print('test_856, is_process, document_856', is_process, document_856)

	def test_810(self, key, document, force=True):
		sap = Invoices().get_document_with_lines(key)
		is_process, document_810 = self.create_invoice(sap, document, force)
		#print('test_810, is_process, document_810, sap', is_process, document_810, sap)