# -*- coding: utf-8 -*-
{
    'name': "MRP order by lot",

    'summary': """ MRP order by lot """,

    'description': """
        Crear mrp orders by lot
    """,

    'author': "JS",
    'website': "",

    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['stock','base','mrp','sale_stock'],

    'data': [
        'data/ir_sequence_data.xml',
        #'security/ir.model.access.csv',
        'views/mpr_order_production_lot.xml',
        #'report/report.xml',
    ],
    'license': 'LGPL-3',
}
