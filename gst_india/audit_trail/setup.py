import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from gst_india.audit_trail.constants.custom_fields import CUSTOM_FIELDS
from gst_india.audit_trail.utils import (
    enable_audit_trail,
    get_audit_trail_doctypes,
    is_audit_trail_enabled,
)

# Hooks


def setup_fixtures():
    create_custom_fields(CUSTOM_FIELDS)
    create_property_setters_for_versioning()


def create_property_setters_for_versioning():
    for doctype in get_audit_trail_doctypes():
        property_setter = frappe.new_doc("Property Setter")
        property_setter.update(
            {
                "doctype_or_field": "DocType",
                "doc_type": doctype,
                "property": "track_changes",
                "value": "1",
                "property_type": "Check",
                "is_system_generated": 1,
            }
        )
        property_setter.flags.ignore_permissions = True
        property_setter.insert()


def after_migrate():
    if is_audit_trail_enabled():
        create_property_setters_for_versioning()


# Setup Wizard


def get_setup_wizard_stages(args=None):
    if frappe.db.exists("Company"):
        return []

    fail_msg = _("Failed to enable Audit Trail")

    return [
        {
            "status": _("Wrapping up"),
            "fail_msg": fail_msg,
            "tasks": [
                {"fn": configure_audit_trail, "args": args, "fail_msg": fail_msg}
            ],
        },
    ]


def configure_audit_trail(args):
    if args.enable_audit_trail:
        enable_audit_trail()