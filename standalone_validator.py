#  type: ignore

from typing import Any

import json

from datetime import datetime, timedelta
from decimal import Decimal

from rest_framework.response import Response

from django.db.models import Q
from django.db.models import Max

from api.common.views import BaseApiViewSet
from api.validator.config import ComputedPrice, Config

from api.customers.models import PaymentTerm
from api.items.models import Item
from api.rules.models import PriceRule

from api.documents.serializers import OrderSerializer, QuoteSerializer
from api.users.models import User


class _Requests:
    user = User.objects.get(username='pygauthier')
    def build_absolute_uri(self):
        return "/hello/"


class DocumentValidator(BaseApiViewSet):

    def validator(self, request, pk: str = '', **kwargs: Any):  # Ignore PyLintBear (E0602)
        self.skip_validation_status = ['lost', 'cancelled', 'won', 'closed']
        self.request_user = request.user
        self.document = self.get_queryset().filter(code=pk.upper()).first()
        self.serialized_document = self.get_serializer(self.document).data
        self.pre_validation_status = self.document.status

        payment_qs = PaymentTerm.objects.filter(Q(with_credit=True) | Q(with_contract=True))
        # Liste de code de terme de paiement a valider
        self.PAYMENTS_TERMS_TO_CHECK = payment_qs.filter(with_credit=True).values_list('number', flat=True)
        # Liste de code de terme de paiement de contrat
        self.PAYMENT_TERMS_CONTRACT = payment_qs.filter(with_contract=True).values_list('number', flat=True)

        self._set_default_validation()
        is_exclude = self.serialized_document['customer_code'] in Config.EXCLUDED_CUSTOMERS
        is_closed = self.serialized_document['validation']['is_closed']
        is_sap = self.serialized_document['created_by_name'] == 'sap'

        print(f'is_exclude {is_exclude}')
        print(f'is_closed {is_closed}')
        print(f'is_sap {is_sap}')
        if is_closed or is_exclude or is_sap:
            return Response(self.serialized_document)

        self._validate_terms()
        self._validate_lines()
        self._validate_date()
        self._validate_margin()
        self._validate_credit()
        self._validate_approval()  # Need to be last.

        return Response(self.serialized_document)

    def _set_default_validation(self) -> dict:
        # define base validation
        is_close = False
        if self.serialized_document["status"] in self.skip_validation_status:
            is_close = True

        if 'approval' not in self.serialized_document:
            self.serialized_document['approval'] = []
        self.serialized_document['validation'] = {
            'is_closed': is_close,
            'wait_for_approval': False,
            'blocking_approval': False,
            'minimum_payment': 0,
            'transport': False,  # done
            'margin': False,
            'balance': False,  # done
            'non_roulant': False,
            'oversize': False,
            'transport_line_need': False,
            'transport_line_code': '',
            'codes': [],
            'errors': []
        }
        self._set_default_line_validation()
        self.serialized_document["approval_payload"] = []
        self.serialized_document['minimum_payment'] = 0

        return self.serialized_document

    def _set_default_line_validation(self) -> dict:
        line_color = 'green'
        if self.serialized_document["status"] in self.skip_validation_status:
            line_color = 'gray'
        for line in self.serialized_document['lines']:
            print('_set_default_line_validation', line['item_code'])
            line['validation'] = [{
                'code': line_color,
                'message': '',
                'field': '',
                'min_price': 0.00,
            }]

    def _validate_terms(self) -> dict:
        customer_excluded = self.serialized_document['customer_code'] in Config.EXCLUDED_CUSTOMERS
        payment_term_check = self.serialized_document['payment_term_number'] in self.PAYMENTS_TERMS_TO_CHECK
        if customer_excluded and payment_term_check:
            balance_value = self.serialized_document['grand_total'] + self.serialized_document['customer_balance']
            balance_approbation = balance_value > self.serialized_document['customer_credit_limit']
            if balance_approbation:
                self._term_do_balance_approval()
        return self.serialized_document

    def _validate_lines(self) -> dict:
        if self.serialized_document['lines_count'] > 0:
            self._transport_lines()
            self._acompte_non_roulant()

        return self.serialized_document

    def _validate_date(self) -> dict:
        code_message = {
            'type': 'date',
            'code': 'green',
            'message': '',
            'need_approval': False
        }
        now = datetime.now().date()
        if (self.document.due_date - now).days <= 0:
            code_message['message'] = Config.get_text('DATE_EXPIRED')
            code_message['code'] = 'red'

        if now > (self.document.due_date - timedelta(hours=24)):
            code_message['message'] = Config.get_text('DATE_NEAR_EXPIRED')
            code_message['code'] = 'orange'
        if code_message['code'] != 'green':
            self.serialized_document['validation']['codes'].append(code_message)

        return self.serialized_document

    def _validate_margin(self) -> dict:
        print('----------------------- _validate_margin ----------------------------')
        self.serialized_document['debug'] = {}
        q1 = Q(client=self.document.customer.code)
        q2 = Q(client=self.document.customer.group.number)
        rules = PriceRule.objects.filter(q1 | q2)
        minimal_sub_total = []
        minimal_cost_total = []
        for line in self.document.lines.all():
            print(f'line: {line} {line.item_code}')
            if line.status != "deleted":
                price = self._get_lowest_price(rules, line)
                minimal_sub_total.append(price.amount * line.quantity)
                minimal_cost_total.append(price.item.cost * line.quantity)
                print(f'minimal_sub_total: {minimal_sub_total}')
                for _line in self.serialized_document['lines']:
                    if line.id == _line['pk']:
                        print(price)
                        _line['validation'][0]['min_price'] = float(f"{price.amount:.2f}")

        sum_minimal_sub_total = sum(minimal_sub_total)
        sum_minimal_cost_total = sum(minimal_cost_total)
        try:
            approvals_existing = {x.code: x.value for x in self.document.approval.filter(code='margin').all()}
        except:
            approvals_existing = {}

        self.serialized_document['debug']["approvals_existing"] = approvals_existing
        if 'margin' in approvals_existing:
            approved_margin = float(approvals_existing['margin'])
        else:
            approved_margin = float(0.00)

        condition_minimal = float(f"{sum_minimal_sub_total:.2f}") > float(f"{self.document.total:.2f}")
        condition_approved = float(f"{sum_minimal_sub_total:.2f}") > float(f"{approved_margin:.2f}")

        marge_reel = float(self.document.total) - float(sum_minimal_cost_total)
        marge_theorique = float(sum_minimal_sub_total-sum_minimal_cost_total)
        marge_diff = float(float(marge_reel) / float(marge_theorique))
        self.serialized_document['debug']["condition_minimal"] = condition_minimal
        self.serialized_document['debug']["sum_minimal_sub_total"] = f"{sum_minimal_sub_total}"
        self.serialized_document['debug']["sum_minimal_cost_total"] = f"{sum_minimal_cost_total}"
        self.serialized_document['debug']["marge_reel"] = marge_reel
        self.serialized_document['debug']["marge_theorique"] = marge_theorique
        self.serialized_document['debug']["marge"] = f"{marge_diff}"
        self.serialized_document['debug']["marge_int"] = f"{int(marge_diff*10000)}"
        self.serialized_document['debug']["self.document.total"] = float(self.document.total)
        self.serialized_document['debug']["approved_margin"] = float(approved_margin)
        self.serialized_document['debug']["condition_approved_equal"] = float(
            sum_minimal_sub_total) == float(approved_margin)
        self.serialized_document['debug']["condition_approved"] = condition_approved

        if condition_minimal:
            text_format = {
                'total': '{:.2f}'.format(self.document.total),
            }
            self.serialized_document['validation']['blocking_approval'] = True
            approval_payload = {
                'reason': Config.get_text('MARGIN', text_format),
                'value': f"{int(marge_diff*10000)}",
                'applicant_comments': '',
                'approving_comments': '',
                'status': 'unapproved',
                'code': 'margin',
            }
            code_to_push = {
                'type': 'margin',
                'code': 'red',
                'message': Config.get_text('MARGIN', text_format),
                'need_approval': True
            }
            self.serialized_document['validation']['codes'].append(code_to_push)
            approval_payload['order'] = self.document.pk
            approval_payload['created_by'] = self.request_user.pk
            self.serialized_document['approval_payload'].append(approval_payload)

        print('----------------------- _validate_margin ----------------------------')
        return self.serialized_document

    def _validate_credit(self) -> dict:
        print('----------------------- _validate_credit -----------------------')
        print('self.document.payment_term.with_credit', self.document.payment_term.with_credit)
        if self.document.payment_term.with_credit:
            new_blance = self.document.grand_total + float(self.document.customer.balance)
            print('new_blance', new_blance)
            credit_busted = new_blance > self.document.customer.credit_limit
            print('credit_busted', credit_busted)
            print('credit_busted or self.document.customer.credit_hold', credit_busted or self.document.customer.credit_hold)
            if credit_busted or self.document.customer.credit_hold:
                self.serialized_document['validation']['blocking_approval'] = True
                text_format = {
                    'total': '{:.2f}'.format(self.document.total),
                }
                approval_payload = {
                    'reason': Config.get_text('CREDIT', text_format),
                    'value': '{:.2f}'.format(self.document.total),
                    'applicant_comments': '',
                    'approving_comments': '',
                    'status': 'unapproved',
                    'code': 'credit',
                    'order': self.document.pk,
                    'created_by': self.request_user.pk,
                }
                code_to_push = {
                    'type': 'credit',
                    'code': 'red',
                    'message': Config.get_text('CREDIT', text_format),
                    'need_approval': True,
                    'approval_payload': approval_payload,
                }
                self.serialized_document['validation']['codes'].append(code_to_push)
        print('----------------------- /_validate_credit -----------------------')
        self._valid_cvt()

        return self.serialized_document

    def _valid_cvt(self) -> dict:
        print('----------------------- _valid_cvt -----------------------')
        if self.document.payment_term.number in (128, 134):
            print(f'self.document.payment_term.number {self.document.payment_term.number}')
            code_to_push = {
                'type': 'cvt',
                'code': 'red',
                'message': Config.get_text('CVT_NEED'),
                'need_approval': True,
                'approval_payload': {},
            }
            self.serialized_document['validation']['blocking_approval'] = True
            print(f'self.document.cvt_number {self.document.cvt_number}')
            if self.document.cvt_number != '':
                code_to_push['code'] = 'orange'
                code_to_push['message'] = Config.get_text('CVT_WAITING')

                print(f'self.document.cvt_status {self.document.cvt_status}')
                if self.document.cvt_status:
                    code_to_push['code'] = 'green'
                    code_to_push['message'] = Config.get_text('CVT_COMPLETED')
                    code_to_push['need_approval'] = False
                    self.serialized_document['validation']['blocking_approval'] = False

            self.serialized_document['validation']['codes'].append(code_to_push)
        print('----------------------- /_valid_cvt -----------------------')
        return self.serialized_document

    def _validate_approval(self) -> dict:
        print('unapproval', False)
        unapproval = False
        approvals_status = [x['status'] for x in self.serialized_document['approval']]
        codes = [x['type'] for x in self.serialized_document['validation']['codes']]
        print('approvals_status', approvals_status, "'unapproved' in approvals_status: ",'unapproved' in approvals_status)
        print('credit in codes','credit' in codes)
        checked_code = False
        check_codes = ['cvt']
        for code in check_codes:
            if code in codes:
                checked_code = True
        if 'unapproved' in approvals_status or checked_code:
            unapproval = True

        print("unapproval", unapproval)
        if unapproval:
            print('enter', unapproval)
            self.serialized_document['validation']['wait_for_approval'] = True
            if 'order' not in self.serialized_document and self.document.status != "draft":
                self.document.status = 'approval'
                self.serialized_document['status'] = 'approval'
                self.document.save()
        else:
            print('else')
            if self.document.status == 'approval':
                self.serialized_document['validation']['wait_for_approval'] = False
                self.serialized_document['validation']['blocking_approval'] = False
                self.document.status = 'open'
                self.serialized_document['status'] = 'open'
                self.document.save()

        return self.serialized_document

    def _term_do_balance_approval(self) -> dict:
        self.serialized_document['validation']['blocking_approval'] = True
        text_format = {
            'total': self.document.grand_total,
            'limit': self.document.customer.credit_limit
        }
        approval_payload = {
            'reason': Config.get_text('CREDIT', text_format),
            'value': self.document.grand_total,
            'applicant_comments': '',
            'approving_comments': '',
            'status': 'unapproved',
            'code': 'credit',
        }
        code_to_push = {
            'type': 'payment',
            'code': 'red',
            'message': Config.get_text('CREDIT', text_format),
            'need_approval': True
        }
        create_approval_need = True
        if 'approval' in self.serialized_document:
            for approval in self.document.approval.all():
                if approval.code == 'credit':
                    self.serialized_document['validation']['wait_for_approval'] = True
                    create_approval_need = False
                    balance_value = self.serialized_document['grand_total'] + \
                        self.serialized_document['customer_balance']
                    if balance_value != approval.value and self.document.status == 'open':
                        for key, val in approval_payload.items():
                            setattr(approval, key, val)
                        approval.approved_by = None
                        approval.save()
                    if approval.status == 'unapproved':
                        credit_message = Config.get_text('CREDIT_UNAPPROVED', text_format)
                        code_to_push['message'] = f"{code_to_push['message']} {credit_message}"
                    if approval.status == 'approved':
                        self.serialized_document['validation']['wait_for_approval'] = False
                        self.serialized_document['validation']['blocking_approval'] = False
                        code_to_push['code'] = 'green'
                        code_to_push['message'] = Config.get_text('CREDIT_APPROVED')
                        code_to_push['need_approval'] = False

        self.serialized_document['validation']['codes'].append(code_to_push)
        approval_payload['order'] = self.document.pk
        approval_payload['created_by'] = self.request_user.pk
        if create_approval_need:
            self.serialized_document['validation']['balance'] = True
            self.serialized_document['approval_payload'].append(approval_payload)
        return self.serialized_document

    def _transport_lines(self) -> dict:
        print('----   _transport_lines   ------')
        self.ship_amount = 0
        items_codes = {x.item_code for x in self.document.lines.all()}
        transport_line_need = self.document.shipping_type_code in Config.SHIPPING_TYPE_ITEM_LINE
        print("self.ship_amount", self.ship_amount)
        print("items_codes", items_codes)
        print("transport_line_need", transport_line_need)

        # CHECK IS TRANSPORT LINE OF GROUP IS PRESENT
        line_shipping_set = set(Config.SHIPPING_TYPE_ITEM_LINE[self.document.shipping_type_code]['check'])
        line_transport_is_not_present = len(items_codes.intersection(  # Ignore PyLintBear (C1801)
        line_shipping_set)) == 0  # Ignore PyLintBear (C1801)
        print('line_shipping_set', line_shipping_set)
        print('line_transport_is_not_present', line_transport_is_not_present)
        print('line_shipping_set', line_shipping_set)
        if transport_line_need:
            print(f"Config.SHIPPING_TYPE_SMALL_PACKAGE {Config.SHIPPING_TYPE_SMALL_PACKAGE}", f"self.document.shipping_type_code: {self.document.shipping_type_code}")
            is_small_pakage = self.document.shipping_type_code in Config.SHIPPING_TYPE_SMALL_PACKAGE
            print("line_shipping_set", transport_line_need)
            print("line_transport_is_not_present", transport_line_need)
            print("is_small_pakage", is_small_pakage)
            if is_small_pakage:
                self._line_petits_colis()

            if line_transport_is_not_present:
                transport_line_code = Config.SHIPPING_TYPE_ITEM_LINE[self.document.shipping_type_code]['add']
                message = None
                print("transport_line_code", transport_line_code)
                print("message", message)
                print('self.document.status', self.document.status)
                if self.document.status == 'open':
                    ship_item = Item.objects.filter(code=transport_line_code).first()
                    if is_small_pakage is False:
                        self.ship_amount = ship_item.list_price

                    if self.ship_amount > 0:
                        message = Config.get_text('ADD_TRANSPORT', {'code': transport_line_code})
                        ln_num = self.document.lines.aggregate(Max('line_num')).get('line_num__max', 0)
                        if not ln_num:
                            ln_num = 0
                        print('TRY ADD LINE')
                        '''
                        self.document.lines.create(
                            item=ship_item,
                            item_name=ship_item.name_fr,
                            quantity=1,
                            list_price=Decimal(self.ship_amount),
                            open_quantity=1,
                            discount=0.00,
                            visual_order=self.serialized_document['lines_count'] + 1,
                            tax_code=self.document.shipped_to_address.tax_code,
                            create_item={}
                        )
                        self.document.line_num_pointer += 1
                        self.document.save()
                        '''
                        new_serialized = self.get_serializer(self.document).data
                        print(new_serialized)
                        # check to replace with loop, 
                        # not working when i write
                        self.serialized_document['lines'] = new_serialized['lines']
                        self.serialized_document['line_count'] = new_serialized['line_count']
                        self.serialized_document['total'] = new_serialized['total']
                        self.serialized_document['tax_1_amount'] = new_serialized['tax_1_amount']
                        self.serialized_document['tax_2_amount'] = new_serialized['tax_2_amount']
                        self.serialized_document['grand_total'] = new_serialized['grand_total']
                        self.serialized_document['balance_due'] = new_serialized['balance_due']
                        self._set_default_line_validation()
                else:
                    if self.ship_amount > 0:
                        message = Config.get_text('WILL_ADD_TRANSPORT', {'code': transport_line_code})

                if message:
                    self.serialized_document['validation']['transport'] = True
                    self.serialized_document['validation']['codes'].append({
                        'type': 'transport',
                        'code': 'orange',
                        'message': message,
                        'need_approval': False,
                    })

        else:
            if line_transport_is_not_present == False:
                for line in self.document.lines.all():
                    if line.item_code in line_shipping_set:
                        print('TRY DELETE LINE', line.item_code)
                        """
                        if self.document.code_sap:
                            line.status = 'deleted'
                            line.save()
                        else:
                            line.delete()
                        """
                self.document.save()
                self.serialized_document = self.get_serializer(self.document).data
                # check to replace with loop, 
                # not working when i write
                self.serialized_document['lines'] = new_serialized['lines']
                self.serialized_document['line_count'] = new_serialized['line_count']
                self.serialized_document['total'] = new_serialized['total']
                self.serialized_document['tax_1_amount'] = new_serialized['tax_1_amount']
                self.serialized_document['tax_2_amount'] = new_serialized['tax_2_amount']
                self.serialized_document['grand_total'] = new_serialized['grand_total']
                self.serialized_document['balance_due'] = new_serialized['balance_due']
                self._set_default_line_validation()

        print('----   /_transport_lines   ------')
        return self.serialized_document

    def _acompte_non_roulant(self) -> dict:
        print('------------------------------------ _acompte_non_roulant --------------------------------------')
        items_code = ('S9911', 'D9911', 'G9911', 'E9911',)
        doc_total_not_r = 0
        for line in self.document.lines.all():
            condition_item_code = line.item_code in items_code or line.item.inventoried
            condition_type = line.item.status != 'R' and line.item.group_name != 'Z'
            if condition_item_code and condition_type:
                doc_total_not_r += line.total
        print(f'doc_total_not_r: {doc_total_not_r}')
        if doc_total_not_r < 300:
            self.serialized_document['minimum_payment'] = doc_total_not_r
        if doc_total_not_r >= 300:
            self.serialized_document['minimum_payment'] = 300 + ((doc_total_not_r - 300) * 0.5)

        check_need_paid_condition = self.serialized_document['minimum_payment'] > float(
            self.serialized_document['paid'])

        if self.serialized_document['payment_term_number'] in Config.EXCLUDED_ACOMPTE_NON_ROULANT_NUMBER:
            check_need_paid_condition = False
            
        print(f'check_need_paid_condition: {check_need_paid_condition}')
        is_paid = float(self.serialized_document['paid']) >= self.serialized_document['minimum_payment']
        print(f'is_paid: {is_paid}')
        if is_paid and self.document.status == 'approval':
            self.serialized_document['validation']['wait_for_approval'] = False

        if self.serialized_document['minimum_payment'] > 0 and check_need_paid_condition:
            text_format = {
                'amount': '{:.2f}'.format(self.serialized_document['minimum_payment']),
            }
            payload = {
                'type': 'acompte',
                'code': 'red',
                'message': Config.get_text('ACOMPTE_NON_ROULANT', text_format),
                'need_approval': False,
                'status':'unapproved'
            }
            self.serialized_document['validation']['codes'].append(payload)
            self.serialized_document['approval'].append(payload)
        print('------------------------------------ /_acompte_non_roulant --------------------------------------')
        return self.serialized_document

    def _line_petits_colis(self) -> dict:
        print('----   _line_petits_colis   ------')
        group_code = self.document.customer.group.number
        if group_code in Config.TRANSPORT_CONDITION_SMALL_PARCEL:
            rule = Config.TRANSPORT_CONDITION_SMALL_PARCEL[group_code]
        else:
            rule = Config.TRANSPORT_CONDITION_SMALL_PARCEL["limit"]

        if group_code not in Config.TRANSPORT_NO_CHARGE_GROUPS:
            self.ship_amount = Config.transport_rule(rule, self.document.total)

        print('group_code', group_code)
        print('rule', rule)
        print('self.ship_amount', self.ship_amount)
        print('----   /_line_petits_colis   ------')
        return self.serialized_document

    def _get_lowest_price(self, rules: list, line: Any) -> ComputedPrice:
        item = line.item
        computed_price = ComputedPrice(item=item)
        if computed_price.amount == 0.00:
            computed_price.amount = line.list_price

        price_lists = {
            '1': 'list_price',
            '3': 'cost',
            '6': 'list_six',
            '7': 'list_seven',
        }
        if item.special is not None and item.special is not None:
            computed_price.is_special = True
            computed_price.amount = item.special
            computed_price.rule.item_type = 'special'

        if rules:
            for rule in rules:
                condition_global = rule.item_type == '*'
                condition_group = rule.item_type == 'G' and rule.item == item.group_name
                condition_code = rule.item == item.code
                if condition_global or condition_group or condition_code:
                    if rule.price_list:
                        temp_price = getattr(item, price_lists[rule.price_list])
                        rebated_price = temp_price * ((100 + rule.value) / 100)
                    else:
                        rebated_price = rule.value
                    if rebated_price < computed_price.amount:
                        computed_price.price_list_name = rebated_price
                        computed_price.price_list_number = f"{rule.price_list}"
                        computed_price.is_special = False
                        computed_price.amount = rebated_price
                        computed_price.rule = rule

        if line.item.marge_min:
            vendant_min = line.item.cost / ((100 - line.item.marge_min) / 100)
            if vendant_min < computed_price.amount:
                computed_price.price_list_name = 'marge_min'
                computed_price.price_list_number = f'cost_{line.item.marge_min}'
                computed_price.is_special = False
                computed_price.amount = vendant_min
                computed_price.rule = PriceRule(**computed_price.temp_rule)

        return computed_price


class OrderValidator(DocumentValidator):
    def get_serializer_class(self):
        return OrderSerializer

    def get_serializer_context(self):
        return {
            'request': _Requests,
            'format': {},
            'view': self
        }


class QuoteValidator(DocumentValidator):
    def get_serializer_class(self):
        return QuoteSerializer

    def get_serializer_context(self):
        return {
            'request': _Requests,
            'format': {},
            'view': self
        }



#dictionary = QuoteValidator().validator(_Requests, 'S0395009').data
dictionary = OrderValidator().validator(_Requests, 'C0239802').data
#print(json.dumps(dictionary, indent=4, sort_keys=False))
