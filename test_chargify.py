import unittest

from chargify import Chargify, ChargifyError


class ChargifyHttpClientStub(object):

    def make_request(self, url, method, params, data, api_key):
        return url, method, params, data


class ChargifyTestCase(unittest.TestCase):

    def setUp(self):
        subdomain = 'subdomain'
        self.chargify = Chargify('api_key', subdomain,
                                 client=ChargifyHttpClientStub())
        self.host = 'https://%s.chargify.com' % subdomain

    def assertResult(self, result, expected_url, expected_method,
                     expected_params, expected_data):
        """
        A little helper method to help verify that the correct URL, HTTP
        method, and POST data are being constructed from the Chargify API.
        """
        url, method, params, data = result
        self.assertEqual(url, '%s%s' % (self.host, expected_url))
        self.assertEqual(method, expected_method)
        self.assertEqual(params, expected_params)
        self.assertEqual(data, expected_data)


class TestCustomers(ChargifyTestCase):

    def test_construct_request(self):
        # List
        result = self.chargify.customers()
        self.assertResult(
            result,
            '/customers.json',
            'GET',
            {},
            {}
        )

        # Read/show (via chargify id)
        result = self.chargify.customers(customer_id=123)
        self.assertResult(
            result,
            '/customers/123.json',
            'GET',
            {},
            {}
        )

        # Read/show (via reference value)
        result = self.chargify.customers.lookup(reference=123)
        self.assertResult(
            result,
            '/customers/lookup.json',
            'GET',
            {'reference': 123},
            {}
        )

        # Create
        result = self.chargify.customers.create(
            data={
                'customer': {
                    'first_name': 'Joe',
                    'last_name': 'Blow',
                    'email': 'joe@example.com',
                }
            }
        )
        self.assertResult(
            result,
            '/customers.json',
            'POST',
            {},
            {'customer': {'first_name': 'Joe', 'last_name': 'Blow', 'email': 'joe@example.com'}}
        )

        # Edit/update
        result = self.chargify.customers.update(
            customer_id=123,
            data={
                'customer': {
                    'email': 'joe@example.com',
                }
            }
        )
        self.assertResult(
            result,
            '/customers/123.json',
            'PUT',
            {},
            {'customer': {'email': 'joe@example.com'}}
        )

        # Delete
        result = self.chargify.customers.delete(customer_id=123)
        self.assertResult(
            result,
            '/customers/123.json',
            'DELETE',
            {},
            {}
        )


class TestProducts(ChargifyTestCase):

    def test_construct_request(self):
        # List
        result = self.chargify.products()
        self.assertResult(
            result,
            '/products.json',
            'GET',
            {},
            {}
        )

        # Read/show (via chargify id)
        result = self.chargify.products(product_id=123)
        self.assertResult(
            result,
            '/products/123.json',
            'GET',
            {},
            {}
        )

        # Read/show (via api handle)
        result = self.chargify.products.handle(handle='myhandle')
        self.assertResult(
            result,
            '/products/handle/myhandle.json',
            'GET',
            {},
            {}
        )


class TestSubscriptions(ChargifyTestCase):

    def test_construct_request(self):
        # List
        result = self.chargify.customers.subscriptions(customer_id=123)
        self.assertResult(
            result,
            '/customers/123/subscriptions.json',
            'GET',
            {},
            {}
        )

        # Read
        result = self.chargify.subscriptions(subscription_id=123)
        self.assertResult(
            result,
            '/subscriptions/123.json',
            'GET',
            {},
            {}
        )

        # Create
        result = self.chargify.subscriptions.create(
            data={
                'subscription': {
                    'product_handle': 'my_product',
                    'customer_attributes': {
                        'first_name': 'Joe',
                        'last_name': 'Blow',
                        'email': 'joe@example.com',
                    },
                    'credit_card_attributes': {
                        'full_number': '1',
                        'expiration_month': '10',
                        'expiration_year': '2020',
                    }
                }
            }
        )
        self.assertResult(
            result,
            '/subscriptions.json',
            'POST',
            {},
            {'subscription': {'product_handle': 'my_product', 'credit_card_attributes': {'expiration_month': '10', 'full_number': '1', 'expiration_year': '2020'}, 'customer_attributes': {'first_name': 'Joe', 'last_name': 'Blow', 'email': 'joe@example.com'}}}
        )

        # Update
        result = self.chargify.subscriptions.update(
            subscription_id=123,
            data={
                'subscription': {
                    'credit_card_attributes': {
                        'full_number': '2',
                        'expiration_month': '10',
                        'expiration_year': '2030',
                    }
                }
            }
        )
        self.assertResult(
            result,
            '/subscriptions/123.json',
            'PUT',
            {},
            {'subscription': {'credit_card_attributes': {'expiration_month': '10', 'full_number': '2', 'expiration_year': '2030'}}}
        )

        # Delete
        result = self.chargify.subscriptions.delete(
            subscription_id=123,
            data={
                'subscription': {
                    'cancellation_message': 'Goodbye!',
                }
            }
        )
        self.assertResult(
            result,
            '/subscriptions/123.json',
            'DELETE',
            {},
            {'subscription': {'cancellation_message': 'Goodbye!'}}
        )


class TestCharges(ChargifyTestCase):

    def test_construct_request(self):
        # Create
        result = self.chargify.subscriptions.charges.create(
            subscription_id=123,
            data={
                'charge': {
                    'amount': '1.00',
                    'memo': 'This is the description of the one time charge.',
                }
            }
        )
        self.assertResult(
            result,
            '/subscriptions/123/charges.json',
            'POST',
            {},
            {'charge': {'amount': '1.00', 'memo': 'This is the description of the one time charge.'}}
        )


class TestComponents(ChargifyTestCase):

    def test_construct_request(self):
        # List
        result = self.chargify.subscriptions.components.usages(
            subscription_id=123, component_id=456)
        self.assertResult(
            result,
            '/subscriptions/123/components/456/usages.json',
            'GET',
            {},
            {}
        )

        # Create
        result = self.chargify.subscriptions.components.usages.create(
            subscription_id=123,
            component_id=456,
            data={
                'usage': {
                    'quantity': 5,
                    'memo': 'My memo',
                }
            }
        )
        self.assertResult(
            result,
            '/subscriptions/123/components/456/usages.json',
            'POST',
            {},
            {'usage': {'memo': 'My memo', 'quantity': 5}}
        )


class TestMigrations(ChargifyTestCase):

    def test_construct_request(self):
        # Create
        result = self.chargify.subscriptions.migrations.create(
            subscription_id=123,
            data={
                'product_id': 1234,
            }
        )
        self.assertResult(
            result,
            '/subscriptions/123/migrations.json',
            'POST',
            {},
            {'product_id': 1234}
        )


class TestReactivate(ChargifyTestCase):

    def test_construct_request(self):
        # Reactivate
        result = self.chargify.subscriptions.reactivate.update(subscription_id=123)
        self.assertResult(
            result,
            '/subscriptions/123/reactivate.json',
            'PUT',
            {},
            {}
        )


class TestTransactions(ChargifyTestCase):

    def test_construct_request(self):
        # List transactions for a site
        result = self.chargify.transactions()
        self.assertResult(
            result,
            '/transactions.json',
            'GET',
            {},
            {}
        )

        # List transactions for a subscription
        result = self.chargify.subscriptions.transactions(subscription_id=123)
        self.assertResult(
            result,
            '/subscriptions/123/transactions.json',
            'GET',
            {},
            {}
        )


class TestInvoices(ChargifyTestCase):

    def test_construct_request(self):
        # List all invoices
        result = self.chargify.invoices()
        self.assertResult(
            result,
            '/invoices.json',
            'GET',
            {},
            {}
        )

        # Get a specific invoice
        result = self.chargify.invoices(invoice_id=123)
        self.assertResult(
            result,
            '/invoices/123.json',
            'GET',
            {},
            {}
        )


class TestPaymentProfiles(ChargifyTestCase):

    def test_construct_request(self):
        # List all payment profiles
        result = self.chargify.payment_profiles()
        self.assertResult(
            result,
            '/payment_profiles.json',
            'GET',
            {},
            {}
        )

        # Get a specific payment profile
        result = self.chargify.payment_profiles(payment_profile_id=123)
        self.assertResult(
            result,
            '/payment_profiles/123.json',
            'GET',
            {},
            {}
        )


class TestCoupons(ChargifyTestCase):

    def test_construct_request(self):
        coupon = {
            "coupon": {
                "name": "15% off",
                "code": "15OFF",
                "description": "15% off",
                "percentage": "20",
                "allow_negative_balance": "false",
                "recurring": "false",
                "end_date": "2017-06-18T12:00:00+01:00",
                "product_family_id": "9876"
            }
        }

        # Create a new coupon
        result = self.chargify.coupons.create(data=coupon)
        self.assertResult(
            result,
            '/coupons.json',
            'POST',
            {},
            {"coupon": {"allow_negative_balance": "false", "code": "15OFF", "name": "15% off", "end_date": "2017-06-18T12:00:00+01:00", "product_family_id": "9876", "percentage": "20", "recurring": "false", "description": "15% off"}}
        )

        # Retrieve a coupon by id
        result = self.chargify.coupons(coupon_id='123')
        self.assertResult(result, '/coupons/123.json', 'GET', {}, {})

        # Find a specific coupon
        result = self.chargify.coupons.find(code='15OFF')
        self.assertResult(
            result,
            '/coupons/find.json',
            'GET',
            {'code': '15OFF'},
            {}
        )

        # Validate a coupon code
        result = self.chargify.coupons.validate(code='15OFF')
        self.assertResult(
            result,
            '/coupons/validate.json',
            'GET',
            {'code': '15OFF'},
            {}
        )

        # Validate a coupon code
        result = self.chargify.coupons.validate(code='15OFF')
        self.assertResult(
            result,
            '/coupons/validate.json',
            'GET',
            {'code': '15OFF'},
            {}
        )

        # Add a coupon to a specific subscription
        result = self.chargify.subscriptions.add_coupon.create(
            subscription_id=123, code='15OFF')
        self.assertResult(
            result,
            '/subscriptions/123/add_coupon.json',
            'POST',
            {'code': '15OFF'},
            {}
        )

        # Remove a coupon from a subscription
        result = self.chargify.subscriptions.remove_coupon.delete(
            subscription_id=123)
        self.assertResult(
            result,
            '/subscriptions/123/remove_coupon.json',
            'DELETE',
            {},
            {}
        )


class TestCouponSubCodes(ChargifyTestCase):

    def test_construct_request(self):
        # Create new subcodes
        result = self.chargify.coupons.codes.create(
            coupon_id=123,
            data={'codes': ['TEST1', 'TEST2']}
        )
        self.assertResult(
            result,
            '/coupons/123/codes.json',
            'POST',
            {},
            {"codes": ["TEST1", "TEST2"]}
        )

        # Update existing subcodes
        result = self.chargify.coupons.codes.update(
            coupon_id=123,
            data={'codes': ['TEST1', 'TEST3']}
        )
        self.assertResult(
            result,
            '/coupons/123/codes.json',
            'PUT',
            {},
            {"codes": ["TEST1", "TEST3"]}
        )

        # Retrieve all subcodes
        result = self.chargify.coupons.codes(coupon_id=123)
        self.assertResult(
            result,
            '/coupons/123/codes.json',
            'GET',
            {},
            {}
        )

        # Delete a subcode
        result = self.chargify.coupons.codes.delete(coupon_id=123,
                                                    code_id='TEST1')
        self.assertResult(
            result,
            '/coupons/123/codes/TEST1.json',
            'DELETE',
            {},
            {}
        )


class TestErrors(ChargifyTestCase):

    def test_catchall(self):
        assert ChargifyError()


if __name__ == '__main__':
    unittest.main()
