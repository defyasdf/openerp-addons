##############################################################################
#
# Copyright (c) 2004-2008 Tiny SPRL (http://tiny.be) All Rights Reserved.
#
# $Id: __terp__.py 8595 2008-06-16 13:00:21Z stw $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################

from osv import fields, osv
import pooler


class profile_manufacturing_config_install_modules_wizard(osv.osv_memory):
    _name='profile.manufacturing.config.install_modules_wizard'
    _columns = {
        'mrp_jit':fields.boolean('Just in Time Scheduling',
            help="The JIT module allows you to not run the scheduler "\
                "periodically. It's easier and faster for real time "\
                "stock computation but, in counter-part, it manages less "\
                "efficiently priorities in procurements."
        ),
        'sale_margin':fields.boolean('Margins on Sales Order',
            help="Display margins on the sale order form."),
        'crm_configuration':fields.boolean('CRM and Calendars',
            help="This installs the customer relationship features like: "\
            "leads and opportunities tracking, shared calendar, jobs "\
            "tracking, bug tracker, and so on."),
        'sale_journal':fields.boolean('Manage by Journals',
            help="This module  allows you to manage your " \
              "sales, invoicing and picking by journals. You can define "\
              "journals for trucks, salesman, departments, invoicing date "\
              "delivery period, etc."
            ),
        'mrp_operation': fields.boolean('Manufacturing Operations',
            help="This module allows you to not only manage by production order "\
            "but also by work order/operation. You will be able to planify, "\
            "analyse the cost, check times, ... on all operations of each "\
            "manufacturing order"),
        'stock_location': fields.boolean('Advanced Locations',
            help="Allows you to manage an advanced logistic with different "\
            "locations. You can define, by product: default locations, "\
            "path of locations for different operations, etc. This module "\
            "is often used for: localisation of products, managing a manufacturing "\
            "chain, a quality control location, product that you rent, etc."\
        ),
        'warning': fields.boolean('Alerts',
            help="Allows to manage alerts on products and partners that are "\
            "showed on different events: sale order, invoice, purchase order, ..."),
        'point_of_sale': fields.boolean('Point of Sale',
            help="This module allows you to manage a point of sale system. "\
            "It offers a basic form for pos operations. You must also check "\
            "our frontend point of sale for a perfect ergonomy with touchscreen "\
            "materials and payment processing hardware."),
        'portal': fields.boolean('Portal',
            help="This module allows you to manage a Portal system."),
        'mrp_subproduct': fields.boolean('Mrp Sub Product',
            help="This module allows you to add sub poducts in mrp bom."),
         'warning': fields.boolean('Warning',
            help="Able you to set warnings on products and partners."),
        'board_document':fields.boolean('Document Management', 
            help= "The Document Management System of Open ERP allows you to store, browse, automatically index, search and preview all kind of documents (internal documents, printed reports, calendar system). It opens an FTP access for the users to easily browse association's document."),

    }
    def action_cancel(self,cr,uid,ids,conect=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
         }
    def action_install(self, cr, uid, ids, context=None):
        result=self.read(cr,uid,ids)
        mod_obj = self.pool.get('ir.module.module')
        for res in result:
            for r in res:
                if r<>'id' and res[r]:
                    ids = mod_obj.search(cr, uid, [('name', '=', r)])
                    mod_obj.action_install(cr, uid, ids, context=context)
        cr.commit()
        db, pool = pooler.restart_pool(cr.dbname,update_module=True)
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
            }
profile_manufacturing_config_install_modules_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

