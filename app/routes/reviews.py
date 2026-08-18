from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.utils import secure_filename
from pathlib import Path

from app.services.reviews_service import ReviewService


reviews_bp = Blueprint("reviews", __name__)


# ============================================================
# PRODUCT REVIEWS
# ============================================================

@reviews_bp.route("/reviews/product/<int:product_id>")
def product_reviews(product_id):

    reviews = ReviewService.get_product_reviews(
        product_id
    )

    return render_template(
        "customer/reviews.html",
        reviews=reviews,
        product_id=product_id
    )


# ============================================================
# ADD REVIEW
# ============================================================

@reviews_bp.route(
    "/reviews/add/<int:product_id>",
    methods=["POST"]
)
def add_review(product_id):

    if "user_id" not in session:

        flash(
            "Please login to write a review.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # ========================================================
    # RATING
    # ========================================================

    rating = request.form.get(
        "rating",
        type=int
    )


    if not rating or rating < 1 or rating > 5:

        flash(
            "Please select a rating between 1 and 5 stars.",
            "error"
        )

        return redirect(
            url_for(
                "reviews.product_reviews",
                product_id=product_id
            )
        )


    # ========================================================
    # REVIEW TEXT
    # ========================================================

    review_text = request.form.get(
        "review_text",
        ""
    ).strip()


    if not review_text:

        flash(
            "Please write your review.",
            "error"
        )

        return redirect(
            url_for(
                "reviews.product_reviews",
                product_id=product_id
            )
        )


    # ========================================================
    # REVIEW IMAGE
    # ========================================================

    review_image = None

    image = request.files.get(
        "review_image"
    )


    if image and image.filename:

        allowed_extensions = {
            "jpg",
            "jpeg",
            "png",
            "webp"
        }


        extension = (
            image.filename
            .rsplit(".", 1)[-1]
            .lower()
        )


        if extension not in allowed_extensions:

            flash(
                "Please upload JPG, JPEG, PNG or WEBP image.",
                "error"
            )

            return redirect(
                url_for(
                    "reviews.product_reviews",
                    product_id=product_id
                )
            )


        # Review upload folder
        upload_folder = (
            Path(__file__).resolve().parent.parent
            / "static"
            / "uploads"
            / "reviews"
        )


        upload_folder.mkdir(
            parents=True,
            exist_ok=True
        )


        # Secure filename
        original_name = secure_filename(
            image.filename
        )


        # Unique filename
        import uuid

        review_image = (
            str(uuid.uuid4())
            + "_"
            + original_name
        )


        image.save(
            upload_folder / review_image
        )


    # ========================================================
    # SAVE REVIEW
    # ========================================================

    try:

        success, message = ReviewService.add_review(

            user_id=session["user_id"],

            product_id=product_id,

            rating=rating,

            review_text=review_text,

            review_image=review_image
        )


        if success:

            flash(
                message,
                "success"
            )

        else:

            # If review wasn't saved, remove uploaded image
            if review_image:

                image_path = (
                    upload_folder / review_image
                )

                if image_path.exists():

                    image_path.unlink()


            flash(
                message,
                "error"
            )


    except Exception as error:

        print(
            "REVIEW ERROR:",
            error
        )


        # Remove uploaded image if database failed
        if review_image:

            image_path = (
                upload_folder / review_image
            )

            if image_path.exists():

                image_path.unlink()


        flash(
            "Something went wrong while submitting your review.",
            "error"
        )


    return redirect(
        url_for(
            "reviews.product_reviews",
            product_id=product_id
        )
    )


# ============================================================
# ADMIN REVIEWS
# ============================================================

@reviews_bp.route("/admin/reviews")
def admin_reviews():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    reviews = ReviewService.get_all_reviews()


    return render_template(
        "admin/reviews.html",
        reviews=reviews
    )


# ============================================================
# DELETE REVIEW
# ============================================================

@reviews_bp.route(
    "/admin/reviews/delete/<int:review_id>",
    methods=["POST"]
)
def delete_review(review_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    ReviewService.delete_review(
        review_id
    )


    flash(
        "Review deleted successfully.",
        "success"
    )


    return redirect(
        url_for("reviews.admin_reviews")
    )