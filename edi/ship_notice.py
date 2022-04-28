from typing import Dict, List
from pandas.tseries.offsets import BDay
from .writer import Writer

from models.Mongo.edimsss import EDIMSSSLogs, EDIMSSSDocuments

class ShipNotice(Writer):

    def __init__(self, reader=None, sap=None) -> None:
        super().__init__(reader=reader, sap=sap)
        self.reader = reader
        self.sap = sap

        self.document_type = '856'

        self.doyon = 'DOYONSDESPRES'

        self.interchange_id_qualifier = 'ZZ'
        self.interchange_ctrl_version = '00401'
        self.interchange_ctrl_number = '000000001'
        self.group_control = "00001"
        self.transaction_ctrl_number = '000000001'

        self.id_code_qualifier = '91'

        self.functional_id = 'SH'

    def build_header(self) -> None:
        self.document_header = {
            'ISA': self.get_ISA(),
            'GS': self.get_GS(),
            'ST': self.get_ST(),
            'BSN': self.get_BSN(),
            'HL': self.get_HL(),
            'REF': self.get_REF(),
            'PER': self.get_PER(),
            'DTM': ["DTM", "011", f'{self.sap["doc"]["DocDate"].strftime("%Y%m%d")}'],
            **self.get_N_loop(),
        }

    def build_lines(self):
        print(self.get_REF())
        document = self.order_document
        self.document_lines = []
        next_open_shipment_day = self.now+BDay(2)
        self.document_lines.append({
            'HL': ['HL','2','1','O'],
            'PRF': ['PRF', f'{document["reference"]}', '','',f'{document["date"]}']
        })
        hl_no = 3
        for line in self.sap['lines']:
            #order_line = self.get_order_line_by_item_code(line['ItemCode'])

            pid = {'PID': ['PID','F','','', '',f"{line['ItmDescFr']} {line['Dscription']}"]}
            if len(line['ItmDescFr']) + len(line['Dscription']) > 80:
                pid = {
                    'PID1': ['PID','F','','', '',f"{line['ItmDescFr'][:79]}"],
                    'PID2': ['PID','F','','', '',f"{line['Dscription'][:79]}"],
                }

            line = {
                'HL': ['HL',f'{hl_no}','2','I'],
                'LIN': ['LIN', f"{line['U_WebOrderItemId']}", 'VN', f"{line['ItemCode']}"],
                'SN1': ['SN1', '', f"{int(line['Quantity'])}", 'EA','', f"{int(line['OrderedQty'])}", 'EA'],
                **pid,
            }
            self.document_lines.append(line)
            hl_no += 1 


    def get_N_loop(self) -> Dict:
        return {
            'N1_ST': [
                'N1',
                'ST', # Entity Identifier Code
                f'{self.ship_to["name"][:59]}',  # Name
                f"{self.id_code_qualifier}", # Identification Code Qualifier
                f'{self.ship_to["code"]}', # Identification Code
            ],
            'N1_VN': [
                'N1', 
                'VN', # Entity Identifier Code
                'DOYONDESPRES', # Name
                f"{self.id_code_qualifier}", # Identification Code Qualifier
                'DOYONDESPRES', # Identification Code
            ]
        }

    def get_CTT(self) -> List:
        return ['CTT', f'{len(self.document_lines)+1}']