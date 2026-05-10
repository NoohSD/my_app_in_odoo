from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    state = fields.Selection(
        selection_add=[
            ('waiting_approval', 'Waiting Approval'),
            ('cancel', 'Cancelled'),
        ],
        ondelete={
            'waiting_approval': 'cascade',
            'cancel': 'cascade',
        },
    )

    approved_by = fields.Many2one(
        comodel_name='res.users',
        string='Approved By',
        readonly=True,
        copy=False,
        tracking=True,
    )

    approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        copy=False,
    )

    approval_note = fields.Text(
        string='Order Notes',
    )
    
    @api.depends('create_uid')
    def _compute_owner_id(self):
        for rec in self:
            rec.owner_id = rec.create_uid

    def action_validate(self):
        for rec in self:
            if rec.state == 'draft':
                raise UserError(_('يجب إرسال الطلب للموافقة أولاً قبل التحقق.'))
            if rec.state == 'cancel':
                raise UserError(_('لا يمكن التحقق من طلب ملغي.'))
        return super().action_validate()

    def action_submit_for_approval(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Scrap orders can only be sent to approval in Draft status.'))
            rec.state = 'waiting_approval'
            rec._notify_operations_managers()

    def action_approve(self):
        self._check_is_operations_manager()
        for rec in self:
            if rec.state != 'waiting_approval':
                raise UserError(_('Approval is only possible in the status Waiting Approval.'))
            rec.approved_by = self.env.user
            rec.approved_date = fields.Datetime.now()
        # نستدعي super مباشرة لتجاوز الـ check أعلاه
        return super(StockScrap, self).action_validate()

    def action_cancel(self):
        self._check_is_operations_manager()
        for rec in self:
            if rec.state != 'waiting_approval':
                raise UserError(_('Cancel is only possible in the status Waiting Approval'))
            rec.state = 'cancel'
            rec.approved_by = self.env.user
            rec.approved_date = fields.Datetime.now()

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError(_('Reset toonly possible in the status canceled.'))
            rec.state = 'draft'
            rec.approved_by = False
            rec.approved_date = False

    def _check_is_operations_manager(self):
        group = self.env.ref(
            'scrap_approval.group_scrap_operations_manager',
            raise_if_not_found=False
        )
        if not group or self.env.user not in group.users:
            raise AccessError(_('Only the operations manager can approve or cancel scrap orders.'))

    def _notify_operations_managers(self):
        group = self.env.ref(
            'scrap_approval.group_scrap_operations_manager',
            raise_if_not_found=False
        )
        if not group:
            return
        partner_ids = group.users.mapped('partner_id').ids
        for rec in self:
            rec.message_post(
                body=_(
                    'Scrap order sent for <b>%s</b> approval.<br/>'
                    'Product: %s | Quantity: %s %s'
                ) % (
                    rec.name,
                    rec.product_id.display_name,
                    rec.scrap_qty,
                    rec.product_uom_id.name,
                ),
                partner_ids=partner_ids,
                subtype_xmlid='mail.mt_comment',
            )