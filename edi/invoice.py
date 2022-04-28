from typing import Dict, List
from .writer import Writer

class Invoice(Writer):

    def __init__(self, reader=None, sap=None) -> None:
        super().__init__(reader=reader, sap=sap)
        self.reader = reader
        self.sap = sap

        self.document_type = '810'

        self.doyon = 'DOYONSDESPRES'

        self.id_code_qualifier = '91'

        #self.related_po = '0'

        self.functional_id = 'IN'

    def build_header(self) -> None:
        self.document_header = {
            'ISA': self.get_ISA(),
            'GS': self.get_GS(),
            'ST': self.get_ST(),
            'BIG': self.get_BIG(),
            'CUR': self.get_CUR(),
            'REF': self.get_REF(),
            'PER': self.get_PER(),
            **self.get_N_loop(),
            'ITD': self.get_ITD(),
            'DTM': ["DTM", "011", f'{self.sap["doc"]["DocDate"].strftime("%Y%m%d")}'],
        }

        # assigne DTM for exped date
        self.document_header['DTM'][1] = '011'

    def build_lines(self):
        self.document_lines = []
        t1sum = 0
        t2sum = 0
        for line in self.sap['lines']:
            #order_line = self.get_order_line_by_item_code(line['ItemCode'])
            unitMsr = 'EA'
            if line['unitMsr'] != "UN":
                unitMsr = 'CA'
            t1sum += line['T1Sum']
            t2sum += line['T2Sum']

            pid = {'PID': ['PID','F','','', '',f"{line['ItmDescFr']} {line['Dscription']}"]}
            if len(line['ItmDescFr']) + len(line['Dscription']) > 80:
                pid = {
                    'PID1': ['PID','F','','', '',f"{line['ItmDescFr'][:79]}"],
                    'PID2': ['PID','F','','', '',f"{line['Dscription'][:79]}"],
                }

            self.document_lines.append({
                'IT1': [
                    'IT1', f"{line['U_WebOrderItemId']}", f"{int(line['Quantity'])}", 
                    f'{unitMsr}', f"{line['Price']}".strip('0'), "", "VN", f"{line['ItemCode']}"
                ],
                'TXI1': ['TXI', "PS", f"{float(line['T1Sum'])}","*****","1216054501TQ0001"],
                'TXI2': ['TXI', "GS", f"{float(line['T2Sum'])}","*****","834261869RT0001"],
                **pid,
            })

        self.document_lines.append({
            'TDS': ['TDS', f"{float(self.sap['doc']['DocTotal'])}".replace(".","")],
            'TXI3': ['TXI', "PS", f"{float(t1sum)}","*****","1216054501TQ0001"],
            'TXI4': ['TXI', "GS", f"{float(t2sum)}","*****","834261869RT0001"],
        })


    def get_CTT(self) -> List:
        return ['CTT', f'{len(self.document_lines)-1}']
    
    def get_REF(self) -> List:
        document = self.reader.get_document()
        return [
            "REF",
            "PK",
            f"{self.sap['lines'][0]['BaseEntry']}",
        ]