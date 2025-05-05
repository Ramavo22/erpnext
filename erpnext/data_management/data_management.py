import csv
import os
import frappe
from frappe import _


@frappe.whitelist()
def import_data(file_url_supplier=None, file_url_material_request=None, file_url_quotation=None):
    try:
        if not file_url_supplier or not file_url_material_request or not file_url_quotation:
            frappe.throw(_("Tous les fichiers CSV doivent être fournis."))

        file_path_supplier = frappe.get_site_path('private', 'files', os.path.basename(file_url_supplier))
        file_path_material_request = frappe.get_site_path('private', 'files', os.path.basename(file_url_material_request))
        file_path_quotation = frappe.get_site_path('private', 'files', os.path.basename(file_url_quotation))

        # Vérifier si le fichier existe
        if not os.path.exists(file_path_supplier):
            frappe.throw(_("Le fichier n'existe pas : ") + file_path_supplier)
        if not os.path.exists(file_path_material_request):
            frappe.throw(_("Le fichier n'existe pas : ") + file_path_material_request)
        if not os.path.exists(file_path_quotation):
            frappe.throw(_("Le fichier n'existe pas : ") + file_path_quotation)

        # Importer les données
        supplier_import(file_path_supplier)
        material_request_import(file_path_material_request)
        quotation_import(file_path_quotation)

        # Nettoyage
        for file_path, file_url in zip(
            [file_path_supplier, file_path_material_request, file_path_quotation],
            [file_url_supplier, file_url_material_request, file_url_quotation]
        ):
            if os.path.exists(file_path):
                os.remove(file_path)
                frappe.logger().info(f"File deleted: {file_path}")

            file_doc = frappe.get_all("File", filters={"file_url": file_url}, fields=["name"])
            if file_doc:
                frappe.delete_doc("File", file_doc[0].name)
                frappe.logger().info(f"File document deleted: {file_url}")

        return "Lecture terminée avec succès"

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=str(e), title="Import CSV Error")
        frappe.throw(_("Une erreur est survenue pendant l'import : ") + str(e))






def supplier_import(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i,row in enumerate(reader):
            print(f"Ligne {i+1}: {row}")
    
    print("==========================")

def material_request_import(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i,row in enumerate(reader):
            print(f"Ligne {i+1}: {row}")
    print("==========================")
    
def quotation_import(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i,row in enumerate(reader):
            print(f"Ligne {i+1}: {row}")
    print("==========================")
    


@frappe.whitelist()
def reinit_base():
    
    doctype_list=[
        "Article",
        "Item",
        "Supplier",
        "Supplier Item",
        "Material Request",
        "Material Request Item",
        "Request for Quotation",
        "Request for Quotation Item",
        "Supplier Quotation",
        "Supplier Quotation Item",
        "Purchase Order",
        "Purchase Order Item",
        "Purchase Invoice",
        "Purchase Invoice Item",
        "Purchase Receipt",
        "Purchase Receipt Item",
        "Payment Request",
        "Payment Entry"
    ]
    
    for doctype in doctype_list:
        frappe.db.sql(f"TRUNCATE TABLE `tab{doctype}`")
    
    return "Reinit done"
            
# /erpnext.data_management.data_management


# Champ	Description
# articlename	Nom de l’article
# description	Description de l’article
# categorie	Catégorie de l’article
# attachment


