from pandas.tseries.offsets import BDay
from .writer import Writer


class PurchaseOrderAcknowledgment(Writer):

    def __init__(self, reader=None, sap=None) -> None:
        super().__init__(reader=reader, sap=sap)
        self.reader = reader
        self.sap = sap

        self.document_type = '855'

        self.doyon = 'DOYONSDESPRES'

        self.interchange_id_qualifier = 'ZZ'
        self.interchange_ctrl_version = '00401'
        self.interchange_ctrl_number = '000000001'
        self.group_control = "00001"
        self.transaction_ctrl_number = '000000001'

        self.id_code_qualifier = '91'
        self.date_time_id = '010'

        self.functional_id = 'PR'

    def build_header(self) -> None:
        self.document_header = {
            'ISA': self.get_ISA(),
            'GS': self.get_GS(),
            'ST': self.get_ST(),
            'BAK': self.get_BAK(),
            'DTM': self.get_DTM(),
            **self.get_N_loop(),
        }

    def build_lines(self):
        self.document_lines = []
        order_document = self.reader.get_document()
        order_lines = self.order_lines
        next_open_shipment_day = self.now+BDay(2)
        for line in self.sap['lines']:
            order_line = self.get_order_line_by_item_code(line['ItemCode'])
            ack_code = 'IA' if order_line['uom'] == 'EA' else 'IC'
            
            is_stock = False
            code_stock = '017' if False else '068'
            delivery_date = '2000-01-01' if is_stock else next_open_shipment_day.strftime('%Y%m%d')

            pid = {'PID': ['PID','F','','', '',f"{line['ItmDescFr']} {line['Dscription']}"]}
            if len(line['ItmDescFr']) + len(line['Dscription']) > 80:
                pid = {
                    'PID1': ['PID','F','','', '',f"{line['ItmDescFr'][:79]}"],
                    'PID2': ['PID','F','','', '',f"{line['Dscription'][:79]}"],
                }

            if ack_code == 'IA' and float(line['Price']) != float(order_line['uprix']):
                ack_code = 'IP'

            self.document_lines.append({
                'PO1': [
                    'PO1', f"{order_line['line_num']}", f"{order_line['qty']}",f"{order_line['uom']}", 
                    f'{"{:.2f}".format(line["Price"])}', '','VN', f"{line['ItemCode']}", "IN", "23000809"
                ],
                **pid,
                'ACK': [
                    'ACK',f'{ack_code}',
                    f"{int(line['Quantity'])}", 'EA', 
                    f'{code_stock}', delivery_date,
                    '','VC', f"{line['ItemCode']}"
                ]
            })