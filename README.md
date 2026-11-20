# Glow Salon

Salon booking site built with **Django**, **Django REST Framework** and **Safaricom Daraja (M-Pesa STK Push)**.
Customers pick a service, book a slot, and get an M-Pesa payment prompt on their phone.

## Features
- Pages: Home, Services, Book, Pay (HTML + CSS)
- REST API (DRF): `/api/services/`, `/api/bookings/`, `/api/mpesa/stk-push/`, `/api/mpesa/callback/`, `/api/payments/<id>/`
- Daraja STK Push with callback handling (booking becomes **Paid** when M-Pesa confirms)
- Demo mode when no Daraja keys are set (simulated prompt + "Simulate PIN" button)
- Django admin to manage services, bookings and payments

## Run locally
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
python manage.py migrate
python manage.py seed_services
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000 and the admin at http://127.0.0.1:8000/admin

## Daraja setup (real prompts)
1. Create an app at https://developer.safaricom.co.ke and copy the Consumer Key and Secret.
2. Put them in `.env` (`DARAJA_CONSUMER_KEY`, `DARAJA_CONSUMER_SECRET`).
3. Set `DARAJA_CALLBACK_URL` to a public HTTPS URL ending in `/api/mpesa/callback/`
   (your Render URL, or an ngrok URL when testing locally).
4. In the sandbox use the test shortcode `174379` and a number registered in the Daraja simulator.

## Deploy on Render
1. Push this folder to GitHub.
2. On https://render.com choose **New > Blueprint** and select the repo (it reads `render.yaml`).
3. Add `DARAJA_CONSUMER_KEY`, `DARAJA_CONSUMER_SECRET`, `DARAJA_CALLBACK_URL` in the service's Environment tab (optional).
4. Open the generated `https://glow-salon.onrender.com` link.

## Run tests
```bash
python manage.py test
```
