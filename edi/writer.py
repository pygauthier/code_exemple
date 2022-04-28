import os
import datetime
from typing import List, Dict, Union
from pandas.tseries.offsets import BDay
from .sftp import SFTP

"""
    855 APK paylaod 

    ISA:Authorization Information Qualifier, 
        Authorization Information,
        Security Information Qualifier, 
        Security Information.
        Interchange ID Qualifier, 
        Interchange Sender ID,
        Interchange ID Qualifier, 
        Interchange Receiver ID,
        Interchange Date, 
        Interchange Time,
        Interchange Control Standards Identifier, 
        Interchange Control Version Number,
        Interchange Control Number, 
        Acknowledgment Requested,
        Usage Indicator,
        Component Element Separator,

    GS: Functional Identifier Code
        Application Sender's Code
        Application Receiver's Code
        Date
        Time
        Group Control Number
        Responsible Agency Code
        Version / Release / Industry Identifier Code
    
    ST: Transaction Set Identifier Code
        Transaction Set Control Number

    BAK:Transaction Set Purpose Code (
            06: Confirmation
        )
        Acknowledgment Type (
            AC: Acknowledge - With Detail and Change
            AD: Acknowledge - With Detail, No Change
            AE: Acknowledge - With Exception Detail Only
            AT: Accepted
            RD: Reject with Detail
        )
        Purchase Order Number
        Date (YYYYMMDD)
        Release Number
        Reference Identification
        Date (YYYYMMDD)

    BSN:Transaction Set Purpose Code (
            00: Original, 
            14: Advance Notification
        )
        Shipment Identification
        Date
        Time
        Hierarchical Structure Code (
            0004 : Shipment, Order, Item
        )

    DTM:Date/Time Qualifier (
            002 Delivery Requested
            010 Requested Ship
            017 Estimated Delivery
            069 Promised for Delivery
        )
        Date (YYYYMMDD)

    ---- LOOP Loop Hierarchical Level ----
    HL: Hierarchical Level (
            Hierarchical ID Number,
            Hierarchical Parent ID Number,
            Hierarchical Level Code
        )
    REF:Reference Identification (
            Reference Identification Qualifier (
                BM: Bill of Lading Number
                CN: Carrier's Reference Number (PRO/Invoice)
                MB: Master Bill of Lading
                PK: Packing List Number
                ZZ: Mutually Defined
            )
        )
    PER:Administrative Communications Contact
    DTM:Date/Time Reference

    ---- LOOP Loop Reference Identification ----
    N9: Reference Identification Qualifier
        Reference Identification

    MSG:Free-Form Message Text

    ---- LOOP Addresses ----
    N1: Name (
            Entity Identifier Code (
                BT: Bill-to-Party
                ST: Ship To
                VN: Vendor
            )
            Identification Code Qualifier (
                91: Assigned by Seller or Seller's Agent
                92: Assigned by Buyer or Buyer's Agent
                ZZ: Mutually Defined
            )
            Identification Code
        )

    N2: Additional Name Information (
            Name
            Name
        )

    N3: Address Information (
            Address Information
            Address Information
        )

    N4: Geographic Location (
            City Name
            State or Province Code
            Postal Code
            Country Code
        )

    ---- LOOP ITEMS ----
    PO1:Assigned Identification
            Quantity Ordered
            Unit or Basis for Measurement Code (CA: Case, EA: Each)
            Unit Price
            Product/Service ID Qualifier (
                VC: Vendor's (Seller's) Catalog Number
                VN: Vendor's (Seller's) Item Number
        )
        Product/Service ID
    
    PID:Item Description Type (F: Free-form)
            Description
    
    ACK:Line Item Status Code (
            AC: Item Accepted and Shipped
            AR: Item Accepted and Released for Shipment
            BP: Item Accepted - Partial Shipment, Balance Backordered
            IA: Item Accepted
            IB: Item Backordered
            IC: Item Accepted - Changes Made
            ID: Item Deleted
            IF: Item on Hold, Incomplete Description
            IP: Item Accepted - Price Changed
            IQ: Item Accepted - Quantity Changed
            IR: Item Rejected
            IS: Item Accepted - Substitution Made
            R1: Item Rejected, Not a Contract Item
            R2: Item Rejected, Invalid Item Product Number
            R3: Item Rejected, Invalid Unit of Issue
            R4: Item Rejected, Contract Item not Available
            )
            Quantity
            Unit or Basis for Measurement Code (
                CA: Case
                EA: Each
            )
            Date/Time Qualifier (
                017 Estimated Delivery
                068 Current Schedule Ship
            )
            Date (YYYYMMDD)
            Product/Service ID Qualifier (
                VC: Vendor's (Seller's) Catalog Number
                VN: Vendor's (Seller's) Item Number
            )
            Product/Service ID

    CTT:Number of Line Items
    
    SE: Number of Included Segments, 
        Transaction Set Control Number
    
    GE: Number of Transaction Sets Included, 
        Group Control Number

    IEA:Number of Included Functional Groups, 
        Interchange Control Number

"""
class Writer(SFTP):

    def __init__(self, reader=None, sap=None) -> None:
        super().__init__()
        self.reader = reader
        self.sap = sap
        self.now = datetime.datetime.now()
        self.date = self.now.strftime('%y%m%d')
        self.fulldate = self.now.strftime('%Y%m%d')
        self.time = self.now.strftime('%H%M')

        self.document_type = ''

        self.document_header = {}
        self.document_lines = []
        self.document_footer = {}

        self.doyon = 'DOYONSDESPRES  '
        self.receiver_id = ''

        self.interchange_id_qualifier = 'ZZ'
        self.interchange_ctrl_version = '00401'
        self.interchange_ctrl_number = '000000001'
        self.group_control = "00001"
        self.transaction_ctrl_number = '000000001'

        self.id_code_qualifier = '91'

        self.order_document = self.reader.get_document()
        self.order_lines = self.reader.get_lines()
        self.receiver_id = self.reader.header[0][6]
        self.ship_to = self.reader.get_ship_to()
        self.bill_to = self.reader.get_bill_to()
        self.related_po = self.order_document['reference']
        self.ref_order = self.order_document['po_ref']
        
        self.functional_id = 'PR'
        self.date_time_id = '011'

        if hasattr(self.reader, "filename"):
            self.filename = self.reader.filename
            
    def get_ISA(self) -> List:
        return [
            'ISA', 
            '00', # Authorization Information Qualifier
            '          ', # Authorization Information
            '00', # Security Information Qualifier
            '          ', # Security Information
            f'{self.interchange_id_qualifier}', # Interchange ID Qualifier
            f'{self.doyon}'.ljust(15), # Interchange Sender ID
            f'{self.interchange_id_qualifier}', # Interchange ID Qualifier
            f'{self.receiver_id}'.ljust(15), # Interchange Receiver ID
            f'{self.date}', # Interchange Date
            f'{self.time}', # Interchange Time
            'U', # Interchange Control Standards Identifier
            f'{self.interchange_ctrl_version}', # Interchange Control Version Number
            f'{self.interchange_ctrl_number}', # Interchange Control Number
            '0', # Acknowledgment Requested
            'P', # Usage Indicator
            '|' # Component Element Separator
        ]

    def get_GS(self) -> List:
        return [
            "GS",
            f"{self.functional_id}", # Functional Identifier Code
            f'{self.doyon}', # Application Sender's Code
            f'{self.receiver_id}'.strip(' '), # Application Receiver's Code
            f'{self.fulldate}', # Date
            f'{self.time}', # Time
            f"{self.group_control}".strip("0"), # Group Control Number
            "X", # Responsible Agency Code
            f'{self.interchange_ctrl_version}0', # Version / Release / Industry Identifier Code
        ]

    def get_ST(self) -> List:
        return [
            "ST",
            f"{self.document_type}", # Transaction Set Identifier Code
            f"{self.transaction_ctrl_number[-4:]}" # Transaction Set Control Number
        ]

    def get_BIG(self) -> List:
        return [
            "BIG",
            f"{self.sap['doc']['DocDate'].strftime('%Y%m%d')}",
            f"{self.sap['doc']['DocNum']}",
            f"{self.fulldate}",
            f"{self.sap['doc']['NumAtCard']}",
            '', '',
            "DI",
        ]
        
    def get_CUR(self) -> List:
        return ["CUR", "SE", "CAD"]

    def get_REF(self) -> List:
        document = self.reader.get_document()
        return [
            "REF",
            "PK",
            f"{self.sap['doc']['DocNum']}",
        ]

    def get_PER(self) -> List:
        return [
            "PER",
            "DI",
            f"{self.sap['doc']['SlpName']}",
            f"EM",
            f"{self.sap['doc']['SlpEmail']}",
        ]
    
    def get_BSN(self) -> List:
        return [
            "BSN",
            "00", # Transction Set Purpose Code (00 - Original, 14 - Advance Notification)
            f"{self.sap['doc']['DocNum']}", # Shipment Identification
            f"{self.fulldate}", # Date YYYYMMDD
            f"{self.time}", # Time HHMM
            "0004", # Hierarchical Structure Code
        ]

    def get_HL(self) -> List:
        return ["HL","1","","S"]

    def get_BAK(self) -> List:
        return [
            "BAK",
            "06", # Transaction Set Purpose Code
            "AC", # Acknowledgment Type
            f"{self.sap['doc']['NumAtCard']}", # Purchase Order Number
            f'{self.order_document["date"]}', # Date / is the date assigned by the purchaser to purchase order
            #"", # Release Number
            #f"{self.ref_order[:-3]}", # Reference Identification
            #f'{self.fulldate}', # Date
        ]

    def get_DTM(self) -> List:
        return [
            "DTM",
            f"{self.date_time_id}", # Date/Time Qualifier
            f'{self.fulldate}', # Date
        ]

    def get_N_loop(self) -> Dict:
        return {
            'N1_ST': [
                'N1',
                'ST', # Entity Identifier Code
                f'{self.ship_to["name"][:59]}',  # Name
                f"{self.id_code_qualifier}", # Identification Code Qualifier
                f'{self.ship_to["code"]}', # Identification Code
            ],
            'N1_BT': [
                'N1',
                'BT', # Entity Identifier Code
                f'{self.bill_to["name"][:59]}',  # Name
                f"{self.id_code_qualifier}", # Identification Code Qualifier
                f'{self.bill_to["code"]}', # Identification Code
            ],
            'N1_VN': [
                'N1', 
                'VN', # Entity Identifier Code
                'DOYONDESPRES', # Name
                f"{self.id_code_qualifier}", # Identification Code Qualifier
                'DOYONDESPRES', # Identification Code
            ]
        }
    
    def get_ITD(self) -> List:
        return [
            'ITD',
            '01',
            '3',
            '',
            f"{self.sap['doc']['DocDueDate'].strftime('%Y%m%d')}",
        ]
    
    def get_CTT(self) -> List:
        return ['CTT', f'{len(self.document_lines)}']

    def get_SE(self) -> List:
        str_count = len([x for x in self.document_header if x not in ['ISA', 'GS']])
        for line in self.document_lines:
            str_count += len(line)
        str_count += 2
        return ['SE', f'{str_count}', f'{self.transaction_ctrl_number[-4:]}']

    def get_GE(self) -> List:
        return ['GE', f"{self.group_control}".strip("0"), f"{self.group_control}".strip("0")]

    def get_IEA(self) -> List:
        return ['IEA', '1', f'{self.interchange_ctrl_number}']

    # Overrided function
    def build_header(self) -> None:
        pass

    # Overrided function
    def build_lines(self):
        pass

    # Overrided function
    def build_footer(self) -> None:
        self.document_footer = {
            'CTT': self.get_CTT(),
            'SE': self.get_SE(),
            'GE': self.get_GE(),
            'IEA': self.get_IEA()
        }

    def create(self, transfert=False):
        self.build_header()
        self.build_lines()
        self.build_footer()

        _rtn = []
        for prop in [self.document_header, *self.document_lines, self.document_footer]:
            for key, val in prop.items():
                _rtn.append("*".join(val))
        str_return = "~\n".join(_rtn)
        if str_return[-1] != "~":
            str_return += "~"
        
        path = f"{self.local_upload_path}/{self.filename}-{self.document_type}-{self.sap['doc']['DocNum']}"
        try:
            os.remove(path)
        except:
            pass
        file = open(path, 'a', encoding="ISO-8859-1")
        file.write(str_return)
        file.close()
        if transfert:
            send_report = self.upload_files()
        else:
            send_report = None

        return str_return, send_report

    def get_document(self) -> List:
        _rtn = []
        for prop in [self.document_header, *self.document_lines, self.document_footer]:
            for key, val in prop.items():
                _rtn.append(val)
        return _rtn

    def get_order_line_by_item_code(self, item_code) -> dict:
        order_line = None
        order_line = list(filter(lambda x: (x['code'] == item_code), self.order_lines))
        if order_line:
            return order_line[0]
        raise Exception('Order Line not found')

            