frappe.pages['data-management'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'data management',
		single_column: true
	});

	// Ajout du formulaire d'import
	let import_form = new ImportForm({
		parent: page.main,
	});
}

class ImportForm {
	constructor(opts) {
		Object.assign(this, opts);
		this.make();
	}

	make() {
		this.form = new frappe.ui.FieldGroup({
			parent: this.parent,
			fields: [
				{
					label: 'Select CSV File for Supplier',
					fieldname: 'csv_file_supplier',
					fieldtype: 'Attach',
					reqd: 1,
					options: 'csv'
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: 'Select CSV File for Material Request references',
					fieldname: 'csv_file_material_request',
					fieldtype: 'Attach',
					reqd: 1,
					options: 'csv'
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: 'Select CSV File for quotation',
					fieldname: 'csv_file_req_quotation',
					fieldtype: 'Attach',
					reqd: 1,
					options: 'csv'
				},
				{
					fieldtype: 'Section Break'
				},
				{
					label: 'Import',
					fieldname: 'import',
					fieldtype: 'Button',
					click: () => this.import_data()
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: 'Reinit base',
					fieldname: 'action_button',
					fieldtype: 'Button',
					click: () => {
						frappe.call({
							method: 'erpnext.data_management.data_management.reinit_base',
							args: {},
							callback: (r) => {
								frappe.msgprint(__('Re init done'));
							}
						});
					}
				}
			]
		});
		this.form.make();
	}

	import_data() {
		const file_url_supplier = this.form.get_value('csv_file_supplier');
		const file_url_material_request = this.form.get_value('csv_file_material_request');
		const file_url_quotation = this.form.get_value('csv_file_req_quotation');
	
		console.log("SUPPLIER:", file_url_supplier);
		console.log("REQUEST:", file_url_material_request);
		console.log("QUOTATION:", file_url_quotation);
	
		if (!file_url_supplier || !file_url_material_request || !file_url_quotation) {
			frappe.throw(__('Veuillez sélectionner les trois fichiers CSV.'));
			return;
		}
	
		frappe.call({
			method: 'erpnext.data_management.data_management.import_data',
			args: {
				file_url_supplier: file_url_supplier,
				file_url_material_request: file_url_material_request,
				file_url_quotation: file_url_quotation
			},
			callback: (r) => {
				if (!r.exc) {
					frappe.msgprint(__('Import successful'));
					this.form.get_field('csv_file_supplier').set_value('');
					this.form.get_field('csv_file_material_request').set_value('');
					this.form.get_field('csv_file_req_quotation').set_value('');
				}
			}
		});
	}
	
}
