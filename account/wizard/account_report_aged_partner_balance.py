# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree

from osv import osv, fields
from tools.translate import _

class account_aged_trial_balance(osv.osv_memory):
    _inherit = 'account.common.partner.report'
    _name = 'account.aged.trial.balance'
    _description = 'Account Aged Trial balance Report'

    _columns = {
        'period_length':fields.integer('Period length (days)', required=True),
        'direction_selection': fields.selection([('past','Past'),
                                                 ('future','Future')],
                                                 'Analysis Direction', required=True),
    }
    _defaults = {
        'period_length': 30,
        'date_from': time.strftime('%Y-%m-%d'),
        'direction_selection': 'past',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        mod_obj = self.pool.get('ir.model.data')
        res = super(account_aged_trial_balance, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='journal_ids']")
        for node in nodes:
            node.set('invisible', '1')
            node.set('required', '0')
        res['arch'] = etree.tostring(doc)
        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['period_length', 'direction_selection'])[0])

        period_length = data['form']['period_length']
        if period_length<=0:
            raise osv.except_osv(_('UserError'), _('You must enter a period length that cannot be 0 or below !'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('UserError'), _('Enter a Start date !'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

        if data['form']['direction_selection'] == 'past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        data['form'].update(res)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.aged_trial_balance',
            'datas': data
        }

account_aged_trial_balance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
