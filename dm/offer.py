import time
import offer_step

from osv import fields
from osv import osv

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('freeze', 'Freeze'),
    ('closed', 'Close')
]

class dm_media(osv.osv):
    _name = "dm.media"
    _columns = {
        'name' : fields.char('Media', size=64, required=True),
    }
    
dm_media()

class dm_offer_category(osv.osv):
    _name = "dm.offer.category"
    _rec_name = "name"
    
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = self.name_get(cr, uid, ids)
        return dict(res)
    
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from dm_offer_category where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True     

    _columns = {
        'complete_name' : fields.function(_name_get_fnc, method=True, type='char', string='Category'),
        'parent_id' : fields.many2one('dm.offer.category', 'Parent'),
        'name' : fields.char('Name', size=64, required=True),
        'child_ids': fields.one2many('dm.offer.category', 'parent_id', 'Childs Category'),
        'domain' : fields.selection([('view','View'),('general','General'),('production','Production'),('purchase','Purchase')], 'Category Domain')
    }
    
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]
        
dm_offer_category()

class dm_offer_production_cost(osv.osv):
    _name = "dm.offer.production.cost"
    _columns = {
        'name' : fields.char('Name', size=32, required=True)
    }               
    
dm_offer_production_cost()

class dm_offer_delay(osv.osv):
    _name = "dm.offer.delay"
    _columns = {
        'name' : fields.char('Name', size=32, required=True),
		'value' : fields.integer('Number of days'),
    }
    
dm_offer_delay()

class dm_offer(osv.osv):
    _name = "dm.offer"
    _rec_name = 'name'
    
    def __history(self, cr, uid, cases, keyword, context={}):
        for case in cases:
            data = {
                'date' : time.strftime('%Y-%m-%d'),
                'user_id': uid,
                'state' : keyword,
                'offer_id': case.id
            }
            obj = self.pool.get('dm.offer.history')
            obj.create(cr, uid, data, context)
        return True
    
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'lang_orig' : fields.many2one('res.lang', 'Original Language'),
        'copywriter_id' : fields.many2one('res.partner', 'Copywriter'),
        'recommended_trademark' : fields.char('Recommended Trademark',size=64),
        'offer_origin_id' : fields.many2one('dm.offer', 'Original Offer'),
        'active' : fields.boolean('Active'),
        'quotation' : fields.char('Quotation', size=16),
        'legal_state' : fields.selection([('validated','validated'), ('notvalidated','notvalidated'), ('inprogress','inprogress'), ('refused','refused')],'Legal State'),
        'category_ids' : fields.many2many('dm.offer.category','dm_offer_category_rel', 'offer_id', 'offer_category_id', 'Categories', domain="[('domain','=','general')]"),
        'notes' : fields.text('Notes'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        
        'desc' : fields.text('Description'),
        
        'note_layout' : fields.text('Layout Notes'),
        'layout_category_ids' : fields.many2many('dm.offer.category','dm_offer_layout_category','offer_id','offer_layout_categ_id', 'Layout Categories') ,# domain="[('domain','=','production')]"),
        'note_mark' : fields.text('Mark Notes'),
        'mark_category_ids' : fields.many2many('dm.offer.category','dm_offer_mark_category','offer_id','offer_mark_categ_id','Mark Categories'),# domain="[('domain','=','purchase')]"),
        'production_note' : fields.text('Production Notes'),
        'production_category_ids' : fields.many2many('dm.offer.category','dm_offer_production_category','offer_id','offer_production_categ_id', 'Production Categories' , domain="[('domain','=','production')]"),
        'production_delay' : fields.many2one('dm.offer.delay', 'Delay'),
        'production_cost' : fields.many2one('dm.offer.production.cost', 'Production Cost'),
        'purchase_note' : fields.text('Purchase Notes'),
        'purchase_category_ids' : fields.many2many('dm.offer.category','dm_offer_purchase_category','offer_id','offer_purchase_categ_id', 'Purchase Categories', domain="[('domain','=','purchase')]"),

        'history_ids' : fields.one2many('dm.offer.history', 'offer_id', 'History', ondelete="cascade"),

        'order_date' : fields.date('Order Date'),
        'last_modification_date' : fields.date('Last Modification Date'),
        'plannned_delivery_date' : fields.date('Planned Delivery Date'),
        'delivery_date' : fields.date('Delivery Date'),
        'fixed_date' : fields.date('Fixed Date'),
        'buffer_delay' : fields.integer('Buffer Delay'),

        'trademark_sex' : fields.selection([('',''),('female','Female'),('male','male')],"Sex"), 
        'trademark_age' : fields.integer('Age'),        
        'trademark_country_ids' : fields.many2many('res.country','dm_offer_trademark_country', 'offer_id', 'country_id', 'Nationality'),
        'forbidden_country_ids' : fields.many2many('res.country','dm_offer_forbidden_country', 'offer_id', 'country_id', 'Forbidden Countries'),
        'forbidden_state_ids' : fields.many2many('res.country.state','dm_offer_forbidden_state', 'offer_id', 'state_id', 'Forbidden States'),
   
#       (still to be defined by the client)
    
    }
    
    _defaults = {
        'active': lambda *a: 1,
        'state': lambda *a: 'draft',
    }

    def state_close_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'closed')
        self.write(cr, uid, ids, {'state':'closed'})
        return True  

    def state_open_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'open')
        self.write(cr, uid, ids, {'state':'open'})
        return True 
    
    def state_freeze_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'freeze')
        self.write(cr, uid, ids, {'state':'freeze'})
        return True
    
    def state_draft_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'draft')
        self.write(cr, uid, ids, {'state':'draft'})
        return True  
dm_offer()

class dm_offer_history(osv.osv):
    _name = "dm.offer.history"
    _order = 'date'
    _columns = {
        'offer_id' : fields.many2one('dm.offer', 'Offer', required=True, ondelete="cascade"),
        'date' : fields.date('Date'),
        'user_id' : fields.many2one('res.users', 'User'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16)
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }   

dm_offer_history()

class dm_preoffer(osv.osv):
    _name = "dm.preoffer"
    _columns = {    
        'name' : fields.char("Name",size=64,required=True),
        'creator_id' : fields.many2one('res.country','Creator'),
        'copywriter_id' : fields.many2one('res.partner','Ordered To'),
        'market_id' : fields.many2one('res.country','Market'),
        'media_id' : fields.many2one('dm.media','Media',ondelete="cascade"),
        'type' : fields.selection([('new','New'),('rewrite','Rewrite')],'Type'),
        'order_number' : fields.char('Order Number',size=16),
        'order_date' : fields.date('Order Date'),
        'plannned_delivery_date' : fields.date('Planner Delivery Date') ,
        'delivery_date' : fields.date('Delivery Date'),
        'summary' : fields.text('Summary')
    }
dm_preoffer()