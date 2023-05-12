from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import get_user_model
import hashlib

# Create your tests here.
class TestViews(TestCase):
	def setUp(self):
		self.client = Client()
		self.signup_url = reverse('signup')
		self.signin_url = reverse('signin')
		self.deposit_url = reverse('deposit')
		self.invoice_url = reverse('invoice')
		self.pay_url = reverse('pay')
		self.transfer_url = reverse('transfer')
		self.balance_url = reverse('balance')
		self.statement_url = reverse('statement')
		self.signout_url = reverse('signout')
		self.signout_all_url = reverse('signout_all')

		self.User = get_user_model()
		self.user_data = {
		    "nickname": "tommy",
		    "name": "Tommy Lee",
		    "user_id_number": "340323198705157512",
		    "user_phone": "+8615812345679",
		    "user_email": "tommyleeexample.com",
		    "password": "abc123"
		}

	def airline_signup(self):
		request = {
			"nickname": "GreenBamboo",
			"name": "Bamboo Li",
			"user_id_number": "530322199812251234",
			"user_phone": "+8618301234567",
			"user_email": "greenbamboo@gmail.com",
			"password": "Abc123456"
		}
		self.client.post(self.signup_url, request)
	
	def signin(self):
		request = {
		    "nickname": "lily",
		    "name": "lily",
		    "user_id_number": "110101199001011234",
		    "user_phone": "+8613800100100",
		    "user_email": "lily@example.com",
		    "password": "abcdef"
		}
		self.client.post(self.signup_url, request)
		request = {
		    "username": "+8613800100100",
		    "password": "abcdef"
		}
		response = self.client.post(self.signin_url, request)
		return response
	
	def invoice(self):
		request = {
		    "orderId": 1,
		    "AID": 1,
		    "totalAmount": 100,
		    "airline": "boyboy"
		}
		response = self.client.post(self.invoice_url, request)
		return response

	def deposit(self, amount):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}

		request = {
	    	"depositMoney": amount
		}
		response = self.client.post(self.deposit_url, request, **headers)
		return response

	
	# create superuser
	def test_create_superuser(self):
		user = self.User.objects.create_superuser(**self.user_data)
		self.assertTrue(user.is_staff)
		self.assertTrue(user.is_superuser)
		self.assertTrue(user.is_active)

		self.assertEqual(user.username, self.user_data['user_phone'])

		hashed_id_number = hashlib.sha256(self.user_data['user_id_number'].encode()).hexdigest()
		self.assertEqual(user.user_id_number, hashed_id_number)

		for field, value in self.user_data.items():
			if field not in ('password', 'user_id_number', 'user_phone', 'user_email'):
				self.assertEqual(getattr(user, field), value)
	
	# signup
	def test_signup_successful(self):
		request = {
		    "nickname": "lily",
		    "name": "lily",
		    "user_id_number": "110101199001011234",
		    "user_phone": "+8613800100100",
		    "user_email": "lily@example.com",
		    "password": "abcdef"
		}
		response = self.client.post(self.signup_url, request)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'lily')
		self.assertContains(response, '+8613800100100')

	def test_signup_no_fields(self):
		request = {}
		response = self.client.post(self.signup_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'nickname')
		self.assertContains(HttpResponse(response.content.decode()), 'name')
		self.assertContains(HttpResponse(response.content.decode()), 'user_id_number')
		self.assertContains(HttpResponse(response.content.decode()), 'user_phone')
		self.assertContains(HttpResponse(response.content.decode()), 'user_email')
		self.assertContains(HttpResponse(response.content.decode()), 'password')

	def test_signup_existing_phone_number(self):
		request = {
		    "nickname": "lily",
		    "name": "lily",
		    "user_id_number": "110101199001011234",
		    "user_phone": "+8613800100100",
		    "user_email": "lily@example.com",
		    "password": "abcdef"
		}
		self.client.post(self.signup_url, request)
		response = self.client.post(self.signup_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'custom user with this user phone already exists.')

	def test_signup_invalid_phone_number(self):
		request = {
		    "nickname": "lily",
		    "name": "lily",
		    "user_id_number": "110101199001011234",
		    "user_phone": "+861380010010",
		    "user_email": "lily@example.com",
		    "password": "abcdef"
		}
		response = self.client.post(self.signup_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'The phone number entered is not valid.')
	
	def test_signup_invalid_id_number(self):
		request = {
		    "nickname": "lily",
		    "name": "lily",
		    "user_id_number": "11010119900101123",
		    "user_phone": "+8613800100100",
		    "user_email": "lily@example.com",
		    "password": "abcdef"
		}
		response = self.client.post(self.signup_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Please input right identification number')
	
	def test_signup_invalid_email(self):
		request = {
		    "nickname": "lily",
		    "name": "lily",
		    "user_id_number": "110101199001011234",
		    "user_phone": "+8613800100100",
		    "user_email": "lilyexample.com",
		    "password": "abcdef"
		}
		response = self.client.post(self.signup_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Enter a valid email address.')
	
	# signin
	def test_signin_successful(self):
		response = self.signin()
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'lily')
		self.assertContains(response, 'token')

	def test_signin_no_fields(self):
		request = {}
		response = self.client.post(self.signin_url, request)
		self.assertContains(HttpResponse(response.content.decode()), 'username')
		self.assertContains(HttpResponse(response.content.decode()), 'password')

	def test_signin_no_phone_number(self):
		request = {
		    "username": "+8613800100100",
		    "password": "abcdef"
		}
		response = self.client.post(self.signin_url, request)

		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Phone number does not exist')

	def test_signin_invalid_phone_number(self):
		request = {
		    "username": "+861380100100",
		    "password": "abcdef"
		}
		response = self.client.post(self.signin_url, request)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid phone number')

	def test_signin_wrong_credentials(self):
		request = {
		    "nickname": "lily",
		    "name": "lily",
		    "user_id_number": "110101199001011234",
		    "user_phone": "+8613800100100",
		    "user_email": "lily@example.com",
		    "password": "abcdef"
		}
		self.client.post(self.signup_url, request)
		request = {
		    "username": "+8613800100100",
		    "password": "abcde"
		}
		response = self.client.post(self.signin_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Wrong Credentials.')
	
	# signout
	def test_signout_successful(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		response = self.client.post(self.signout_url, **headers)
		self.assertEquals(response.status_code, 204)
	
	def test_signout_no_credential(self):
		response = self.client.post(self.signout_url)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Authentication credentials were not provided.')
	
	def test_signout_invalid_token(self):
		headers = {
        	'HTTP_AUTHORIZATION': 'Token 123',
    	}
		response = self.client.post(self.signout_url, **headers)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid token')
	
	# signout all
	def test_signout_all_successful(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		response = self.client.post(self.signout_all_url, **headers)
		self.assertEquals(response.status_code, 204)
	
	def test_signout_all_no_credential(self):
		response = self.client.post(self.signout_all_url)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Authentication credentials were not provided.')
	
	def test_signout_all_invalid_token(self):
		headers = {
        	'HTTP_AUTHORIZATION': 'Token 123',
    	}
		response = self.client.post(self.signout_all_url, **headers)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid token')
	
	# deposit
	def test_deposit_successful(self):
		response = self.deposit(100)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, '"userBalance":100')
	
	def test_deposit_no_credential(self):
		response = self.signin().json()
		request = {
	    	"depositMoney": 100
		}
		response = self.client.post(self.deposit_url, request)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), '"detail":"Authentication credentials were not provided."')

	def test_deposit_invalid_token(self):
		headers = {
        	'HTTP_AUTHORIZATION': 'Token 123',
    	}
		response = self.client.post(self.deposit_url, **headers)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid token')
	
	def test_deposit_no_fields(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		response = self.client.post(self.deposit_url, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'depositMoney')
	
	def test_deposit_negative_amount(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
		    "depositMoney": -100
		}
		response = self.client.post(self.deposit_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'The amount of money must be greater than zero!')
	
	# invoice
	def test_invoice_successful(self):
		response = self.invoice()
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'PID')
		self.assertContains(response, 'AID')
		self.assertContains(response, 'key')
	
	def test_invoice_no_field(self):
		request = {}
		response = self.client.post(self.invoice_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'orderId')
		self.assertContains(HttpResponse(response.content.decode()), 'AID')
		self.assertContains(HttpResponse(response.content.decode()), 'totalAmount')
		self.assertContains(HttpResponse(response.content.decode()), 'airline')

	def test_invoice_not_support_airline(self):
		request = {
		    "orderId": 1,
		    "AID": 1,
		    "totalAmount": 100,
		    "airline": "airline1"
		}
		response = self.client.post(self.invoice_url, request)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Please enter the correct airline name: boyboy, KingAirline, CandyAirline, Elephant, Frank')
	
	# pay
	def test_pay_successful(self):
		self.invoice()
		self.airline_signup()
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
	    	"depositMoney": 200
		}
		self.client.post(self.deposit_url, request, **headers)
		request = {
    		"orderId": 1
    	}
		response = self.client.post(self.pay_url, request, **headers)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'successful')
		self.assertContains(response, 'orderId')
		self.assertContains(response, 'key')
	
	def test_pay_no_credential(self):
		request = {
    		"orderId": 1
    	}
		response = self.client.post(self.pay_url, request)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Authentication credentials were not provided.')
	
	def test_pay_invalid_token(self):
		headers = {
	    	'HTTP_AUTHORIZATION': 'Token 123',
		}
		response = self.client.post(self.pay_url, **headers)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid token')
	
	def test_pay_no_fields(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		response = self.client.post(self.pay_url, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'orderId')
	
	def test_pay_no_order(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
    		"orderId": 1
    	}
		response = self.client.post(self.pay_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Order does not exist.')
	
	def test_pay_multiple_order(self):
		self.invoice()
		self.invoice()
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
    		"orderId": 1
    	}
		response = self.client.post(self.pay_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'More than one order to pay')
	
	def test_pay_no_enough_balance(self):
		self.invoice()
		self.airline_signup()
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
    		"orderId": 1
    	}
		response = self.client.post(self.pay_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Not enough money')
	
	# transfer
	def test_transfer_successful(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
		    "nickname": "tommy",
		    "name": "Tommy Lee",
		    "user_id_number": "340323198705157512",
		    "user_phone": "+8615812345678",
		    "user_email": "tommylee@example.com",
		    "password": "abc123"
		}
		self.client.post(self.signup_url, request)
		request = {
	    	"depositMoney": 200
		}
		self.client.post(self.deposit_url, request, **headers)
		request = {
		    "phoneNumber": "+8615812345678",
		    "userName": "Tommy Lee",
		    "transferMoney": 150
		}
		response = self.client.post(self.transfer_url, request, **headers)
		
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'successful')
		self.assertContains(response, '"balance":50.0')

	def test_transfer_no_credential(self):
		request = {
		    "phoneNumber": "+8615812345678",
		    "userName": "Tommy Lee",
		    "transferMoney": 150
		}
		response = self.client.post(self.transfer_url, request)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Authentication credentials were not provided.')
	
	def test_transfer_invalid_token(self):
		headers = {
	    	'HTTP_AUTHORIZATION': 'Token 123',
		}
		response = self.client.post(self.transfer_url, **headers)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid token')
	
	def test_transfer_no_fields(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		response = self.client.post(self.transfer_url, **headers)
		
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'phoneNumber')
		self.assertContains(HttpResponse(response.content.decode()), 'userName')
		self.assertContains(HttpResponse(response.content.decode()), 'transferMoney')
	
	def test_transfer_invalid_phone_number(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
		    "phoneNumber": "+861581234567",
		    "userName": "Tommy Lee",
		    "transferMoney": 150
		}
		response = self.client.post(self.transfer_url, request, **headers)
		
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid phone number')
	
	def test_transfer_negative_amount_of_money(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
		    "phoneNumber": "+8615812345678",
		    "userName": "Tommy Lee",
		    "transferMoney": -150
		}
		response = self.client.post(self.transfer_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Cannot transfer negative amount of money.')

	def test_transfer_payee_does_not_exist(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
		    "phoneNumber": "+8615812345678",
		    "userName": "Tommy Lee",
		    "transferMoney": 150
		}
		response = self.client.post(self.transfer_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Payee does not exist.')
	
	def test_transfer_mismatch_phone_number_and_name(self):
		response = self.signin().json()
		request = {
		    "nickname": "tommy",
		    "name": "Tommy Lee",
		    "user_id_number": "340323198705157512",
		    "user_phone": "+8615812345678",
		    "user_email": "tommylee@example.com",
		    "password": "abc123"
		}
		self.client.post(self.signup_url, request)

		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
		    "phoneNumber": "+8615812345678",
		    "userName": "Tommy Le",
		    "transferMoney": 150
		}
		response = self.client.post(self.transfer_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Payee\'s name and phone number does not match')

	def test_transfer_not_enough_money(self):
		response = self.signin().json()
		request = {
		    "nickname": "tommy",
		    "name": "Tommy Lee",
		    "user_id_number": "340323198705157512",
		    "user_phone": "+8615812345678",
		    "user_email": "tommylee@example.com",
		    "password": "abc123"
		}
		self.client.post(self.signup_url, request)

		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
		    "phoneNumber": "+8615812345678",
		    "userName": "Tommy Lee",
		    "transferMoney": 150
		}
		response = self.client.post(self.transfer_url, request, **headers)
		self.assertEquals(response.status_code, 400)
		self.assertContains(HttpResponse(response.content.decode()), 'Not enough money')
	
	# balance
	def test_balance_successful(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		response = self.client.get(self.balance_url, **headers)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'successful')
		self.assertContains(response, '"balance":0')
		request = {
	    	"depositMoney": 200
		}
		self.client.post(self.deposit_url, request, **headers)
		response = self.client.get(self.balance_url, **headers)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'successful')
		self.assertContains(response, '"balance":200')
	
	def test_balance_no_credential(self):
		response = self.client.get(self.balance_url)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Authentication credentials were not provided.')
	
	def test_balance_invalid_token(self):
		headers = {
	    	'HTTP_AUTHORIZATION': 'Token 123',
		}
		response = self.client.post(self.balance_url, **headers)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid token')
	
	# statement
	def test_statement_successful(self):
		response = self.signin().json()
		token = response["data"]["token"]
		headers = {
        	'HTTP_AUTHORIZATION': f'Token {token}',
    	}
		request = {
	    	"depositMoney": 200
		}
		self.client.post(self.deposit_url, request, **headers)
		request = {
		    "nickname": "tommy",
		    "name": "Tommy Lee",
		    "user_id_number": "340323198705157512",
		    "user_phone": "+8615812345678",
		    "user_email": "tommylee@example.com",
		    "password": "abc123"
		}
		self.client.post(self.signup_url, request)
		request = {
		    "phoneNumber": "+8615812345678",
		    "userName": "Tommy Lee",
		    "transferMoney": 150
		}
		self.client.post(self.transfer_url, request, **headers)
		response = self.client.get(self.statement_url, request, **headers)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, 'successful')
		self.assertContains(response, 'deposit')
		self.assertContains(response, '200')
		self.assertContains(response, 'transfer to Tommy Lee')
		self.assertContains(response, '150')
	
	def test_statement_no_credential(self):
		response = self.client.get(self.statement_url)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Authentication credentials were not provided.')

	def test_statement_invalid_token(self):
		headers = {
	    	'HTTP_AUTHORIZATION': 'Token 123',
		}
		response = self.client.post(self.statement_url, **headers)
		self.assertEquals(response.status_code, 401)
		self.assertContains(HttpResponse(response.content.decode()), 'Invalid token')
	
# print(response.content.decode())