import base64
import os.path

from flask_restful import Resource
from flask import request, url_for
from werkzeug.utils import secure_filename
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
import os
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)


class Selfie(Resource):

    def post(self):
        image = request.files.get("image")
        data = request.form.to_dict()
        caption = data["caption"]
        # description = data["description"]
        id = data["id"]
        upload_folder = "static/uploads"
        file_name = secure_filename(image.filename)
        img_dir = os.path.join(upload_folder, file_name)
        image.save(img_dir)

        url = url_for('static', filename=f'uploads/{file_name}')
        img_full_url = f'http://localhost:6160{url}'
        return {
            "image": url,
            "caption": caption,
            # "description": description,
            "id": id
        }, 200


class Daraja(Resource):

    def post(self):
        payload = request.get_json()
        access_token = self.get_access_token()
        if access_token is not None:
            result, status_code = self.post_payment_request(access_token, payload)

            #TODO Persist order_id, merchant_request_id,
            # checkout_request_id, amount: return simple success message to
            # customer

            return result, status_code


    def get_access_token(self):
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        consumer_key = os.getenv('CONSUMER_KEY')
        consumer_secret = os.getenv('CONSUMER_SECRET')
        response = requests.get(url=url,
                                auth=HTTPBasicAuth(consumer_key,consumer_secret))
        if response.status_code == 200:
            return response.json()["access_token"]
        return None

    def post_payment_request(self, access_token, payload):
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        short_code = os.getenv('TILL_NUMBER')
        passkey = os.getenv('DARAJA_PASSKEY')

        password = base64.b64encode(bytes(f"{short_code}{passkey}{timestamp}", "utf-8"))
        req_body = {
            "BusinessShortCode": short_code,
            "Password": password.decode("utf-8"),
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": payload["amount"],
            "PartyA": payload["phone_number"],
            "PartyB": short_code,
            "PhoneNumber": payload["phone_number"],
            "CallBackURL": "https://7841-105-163-157-134.ngrok-free.app/daraja-callback",
            "AccountReference": "DUKA SAFI LTD",
            "TransactionDesc": payload["description"]
          }

        try:
            response = requests.post(url,headers=headers,json=req_body)
            return response.json(), response.status_code
        except Exception as exc:
            logging.debug(exc)
            return {"error": f"Sumn went wrong {exc}"}, 400
class PaymentCallBack(Resource):

    def post(self):
        data = request.get_json()
        logging.debug("received daraja callback\n")
        logging.debug(data)
        result_code = data["Body"]["stkCallback"]["ResultCode"]
        if result_code == 0:
            merchant_req_id = data["Body"]["stkCallback"]["MerchantRequestID"]
            checkout_req_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
            callback_metadatas = data["Body"]["stkCallback"][
                "CallbackMetadata"]["Item"]
            amount = 0
            mpesa_code = ""
            timestamp=""
            for item in callback_metadatas:
                if item["Name"]=="Amount":
                    amount = item["Value"]
                if item["Name"]=="MpesaReceiptNumber":
                    mpesa_code = item["Value"]
                if item["Name"]=="TransactionDate":
                    timestamp = item["Value"]
            #TODO update payment record with mpesa_code and status depending on
            # amount. Update client with transaction status