app_name = "peppol_4_erpnext"
app_title = "Peppol 4 Erpnext"
app_publisher = "Grynn GmbH"
app_description = "ERPNext client for sending and receiving e-invoices"
app_email = "deepak.pai@grynn.ch"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "peppol_4_erpnext",
# 		"logo": "/assets/peppol_4_erpnext/logo.png",
# 		"title": "Peppol 4 Erpnext",
# 		"route": "/peppol_4_erpnext",
# 		"has_permission": "peppol_4_erpnext.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/peppol_4_erpnext/css/peppol_4_erpnext.css"
# app_include_js = "/assets/peppol_4_erpnext/js/peppol_4_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/peppol_4_erpnext/css/peppol_4_erpnext.css"
# web_include_js = "/assets/peppol_4_erpnext/js/peppol_4_erpnext.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "peppol_4_erpnext/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Fixtures
# --------
fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			["name", "in", [
				"Company-peppol_section",
				"Company-peppol_id",
				"Company-peppol_scheme",
				"Customer-peppol_section",
				"Customer-peppol_id",
				"Customer-peppol_scheme",
				"Supplier-peppol_section",
				"Supplier-peppol_id",
				"Supplier-peppol_scheme",
				"Sales Invoice-peppol_section",
				"Sales Invoice-peppol_status",
				"Sales Invoice-peppol_document_name",
				"Sales Invoice-peppol_column_break",
				"Sales Invoice-peppol_sent_on",
				"Sales Invoice-peppol_error",
				"Purchase Invoice-peppol_section",
				"Purchase Invoice-peppol_reference",
				"Purchase Invoice-peppol_sender_id",
				"Purchase Invoice-peppol_column_break",
				"Purchase Invoice-peppol_received_on",
				"Purchase Invoice-is_peppol_invoice",
			]]
		]
	}
]

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "peppol_4_erpnext/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "peppol_4_erpnext.utils.jinja_methods",
# 	"filters": "peppol_4_erpnext.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "peppol_4_erpnext.install.before_install"
# after_install = "peppol_4_erpnext.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "peppol_4_erpnext.uninstall.before_uninstall"
# after_uninstall = "peppol_4_erpnext.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "peppol_4_erpnext.utils.before_app_install"
# after_app_install = "peppol_4_erpnext.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "peppol_4_erpnext.utils.before_app_uninstall"
# after_app_uninstall = "peppol_4_erpnext.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "peppol_4_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"peppol_4_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"peppol_4_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"peppol_4_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"peppol_4_erpnext.tasks.weekly"
# 	],
# 	"monthly": [
# 		"peppol_4_erpnext.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "peppol_4_erpnext.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "peppol_4_erpnext.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "peppol_4_erpnext.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["peppol_4_erpnext.utils.before_request"]
# after_request = ["peppol_4_erpnext.utils.after_request"]

# Job Events
# ----------
# before_job = ["peppol_4_erpnext.utils.before_job"]
# after_job = ["peppol_4_erpnext.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"peppol_4_erpnext.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

