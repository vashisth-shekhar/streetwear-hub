# Repo-specific Copilot instructions

Purpose: Give an AI coding agent the minimal, actionable context to be productive in this Django app.

Quick facts
- Framework: Django (project root uses `manage.py`).
- App: single app `shop/` implementing products, variants, cart (session), orders and simple auth.
- Templates are served from `Templates/` (settings `TEMPLATES['DIRS']` points to BASE_DIR / "templates").
- Database: SQLite at `db.sqlite3` (defined in `config/settings.py`).
- Dev server: `python manage.py runserver`.

Key files to read first
- config/settings.py — project configuration (DEBUG=True, INSTALLED_APPS includes `shop`).
- config/urls.py — mounts `shop.urls` at root.
- shop/models.py — `Product`, `ProductVariant`, `CartItem`, `Order`, `OrderItem` (guest checkout: Order.user is nullable).
- shop/views.py — main business logic: session-backed cart, checkout, signup/login, and order creation. See session/cart structure and POST handlers.
- shop/urls.py — route names used throughout templates (e.g., `product_list`, `product_detail`, `cart_view`).
- Templates/shop/ — UI examples and form names (e.g., `product_detail.html` posts `variant_id`, `checkout.html` posts `name`, `email`, etc.).

Important runtime behaviors & examples
- Session cart shape: views append dicts like
  { 'product_id', 'product_name', 'variant_id', 'variant_text', 'price', 'quantity' } stored in `request.session['cart']`.
  - Price may be stored as string; convert safely before arithmetic (views use float()).
- Adding to cart: `product_detail` POST expects `variant_id`; then redirects to `cart_view`.
- Checkout: `checkout` view sums `price * quantity` from session cart, creates an `Order` and `OrderItem` rows, then clears `request.session['cart']`.
- Auth flows: `signup` uses `User.objects.create_user()` and `login()`. `profile` is protected with `@login_required(login_url='login_view')` (note custom login URL name).

Conventions & patterns specific to this repo
- Templates directory is `Templates/` (capital T) at project root, not the app templates directory only — use base templates in `Templates/base.html`.
- Cart is session-based (no requirement for a logged-in user) — maintain compatibility for both guest & authenticated flows.
- Product images are stored as a URL string on `Product.image` (CharField) rather than a file field.
- No explicit static files pipeline is configured beyond `STATIC_URL` in settings — avoid assuming `collectstatic` or remote storage in quick edits.

Developer workflows (commands you should use)
- Run dev server: `python manage.py runserver`
- Create migrations: `python manage.py makemigrations` then `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Run tests: `python manage.py test`
- Django shell: `python manage.py shell`

Safe-edit guidelines for agents (do not assume external context)
- Don't change `SECRET_KEY` or `DEBUG` without explicit instruction.
- When modifying models, always add/inspect migrations (`makemigrations`) and run `migrate` locally.
- Database is `db.sqlite3` in repo — be careful when running destructive SQL.

When changing UI or templates
- Use the existing template names in `Templates/shop/` and route names from `shop/urls.py`.
- For adding cart logic, prefer changing `shop/views.py` session operations and keep session structure backward compatible.

Integration points to check before editing
- `config/urls.py` includes `shop.urls` at the root — new top-level routes should be added there or in `shop/urls.py`.
- Views and templates rely on named URL patterns; use `reverse()` or `url` tag to avoid breaking links.

Examples to copy or reference
- Session cart append in `shop/views.py:product_detail` — use same keys and types when reading/writing the cart.
- Order creation in `shop/views.py:checkout` — follow same `Order`/`OrderItem` fields and clearing session after success.

Merge notes
- If this file already exists, merge by preserving any project-specific runtime secrets or deployment notes; prefer the concise examples above.

If unsure, ask the developer
- Which authentication flow is canonical (email-as-username?)
- Any preferred formatting or linting (no repo-level config detected)

End of instructions. Please ask if you want these expanded with examples of HTTP fixtures, tests, or a quick dev checklist.
