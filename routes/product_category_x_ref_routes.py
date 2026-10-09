from flask import Blueprint

import controllers

product_category = Blueprint("product_category", __name__)

@product_category.route("/product/category", methods=["POST"])
def create_x_ref():
    return controllers.create_x_ref()