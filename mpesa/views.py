import base64
import requests
from datetime import datetime
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MpesaRequest, MpesaResponse, MpesaCallback
from .serializers import MpesaRequestSerializer, MpesaResponseSerializer

@api_view(['POST'])
def stk_push(request):
    serializer = MpesaRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        mpesa_request = serializer.save()
        print("MPESA Request created:", mpesa_request)

        try:
            response_data = initiate_stk_push(mpesa_request)
            print("STK Push Response Data:", response_data)
        except Exception as e:
            print("Failed to initiate STK Push:", str(e))
            return Response({"error": "Failed to initiate STK Push", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        mpesa_response = MpesaResponse.objects.create(
            request=mpesa_request,
            merchant_request_id=response_data.get('MerchantRequestID', ''),
            checkout_request_id=response_data.get('CheckoutRequestID', ''),
            response_code=response_data.get('ResponseCode', ''),
            response_description=response_data.get('ResponseDescription', ''),
            customer_message=response_data.get('CustomerMessage', '')
        )

        response_serializer = MpesaResponseSerializer(mpesa_response)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("Unexpected error during STK push:", str(e))
        return Response({"error": "Unexpected error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def initiate_stk_push(mpesa_request):
    try:
        access_token = get_access_token()
    except Exception as e:
        raise Exception(f"Access token error: {str(e)}")

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    callback_url = f"{settings.MPESA_CALLBACK_URL}/mpesa/api/mpesa/callback/"
    print("Callback URL being sent to Safaricom:", callback_url)

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": generate_password(timestamp),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": float(mpesa_request.amount),
        "PartyA": mpesa_request.phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": mpesa_request.phone_number,
        "CallBackURL": callback_url,
        "AccountReference": mpesa_request.account_reference,
        "TransactionDesc": mpesa_request.transaction_desc
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print("STK push request failed:", str(e))
        raise Exception(f"STK push request failed: {getattr(e.response, 'text', str(e))}")


def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        access_token = response.json().get('access_token')
        if not access_token:
            raise Exception("Access token not found in response")
        return access_token
    except requests.exceptions.RequestException as e:
        print("Token request failed:", str(e))
        raise Exception(f"Token request failed: {getattr(e.response, 'text', str(e))}")


def generate_password(timestamp):
    try:
        shortcode = settings.MPESA_SHORTCODE
        passkey = settings.MPESA_PASSKEY
        data_to_encode = shortcode + passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode())
        return encoded_string.decode('utf-8')
    except Exception as e:
        raise Exception(f"Password generation failed: {str(e)}")


@api_view(['POST'])
def mpesa_callback(request):
    print("Received callback:", request.data)
    try:
        callback_data = request.data.get('Body', {}).get('stkCallback')
        if not callback_data:
            return Response({"error": "Callback data missing"}, status=status.HTTP_400_BAD_REQUEST)

        merchant_request_id = callback_data.get('MerchantRequestID')
        result_code = callback_data.get('ResultCode')
        result_description = callback_data.get('ResultDesc')
        metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])

        mpesa_receipt_number = None
        transaction_date = None
        phone_number = None
        amount = None

        for item in metadata:
            name = item.get('Name')
            value = item.get('Value')
            if name == "MpesaReceiptNumber":
                mpesa_receipt_number = value
            elif name == "TransactionDate":
                transaction_date = datetime.strptime(str(value), '%Y%m%d%H%M%S') if value else None
            elif name == "PhoneNumber":
                phone_number = str(value)
            elif name == "Amount":
                amount = float(value) if value else None

        try:
            mpesa_request = MpesaRequest.objects.get(merchant_request_id=merchant_request_id)
        except MpesaRequest.DoesNotExist:
            return Response({"error": "Merchant Request ID not found"}, status=status.HTTP_404_NOT_FOUND)

        mpesa_request.status = 'SUCCESS' if result_code == 0 else 'FAILED'
        mpesa_request.save()

        MpesaCallback.objects.create(
            response=mpesa_request,
            result_code=result_code,
            result_description=result_description,
            mpesa_receipt_number=mpesa_receipt_number,
            transaction_date=transaction_date,
            phone_number=phone_number,
            amount=amount,
            callback_metadata=callback_data.get('CallbackMetadata')
        )

        return Response({"message": "Callback processed successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        print("Callback processing failed:", str(e))
        return Response({"error": f"Callback processing failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
