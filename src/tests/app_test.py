import unittest
from app import app, warehouses


class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        warehouses.clear()

    def tearDown(self):
        warehouses.clear()

    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Management', response.data)

    def test_index_shows_no_warehouses_message(self):
        response = self.client.get('/')
        self.assertIn(b'No warehouses yet', response.data)

    def test_add_warehouse(self):
        response = self.client.post('/add_warehouse', data={
            'name': 'TestWarehouse',
            'tilavuus': '100',
            'alku_saldo': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('TestWarehouse', warehouses)
        self.assertEqual(warehouses['TestWarehouse'].tilavuus, 100)
        self.assertEqual(warehouses['TestWarehouse'].saldo, 10)

    def test_add_warehouse_without_initial_balance(self):
        response = self.client.post('/add_warehouse', data={
            'name': 'EmptyWarehouse',
            'tilavuus': '50',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('EmptyWarehouse', warehouses)
        self.assertEqual(warehouses['EmptyWarehouse'].saldo, 0)

    def test_add_warehouse_empty_name_not_added(self):
        response = self.client.post('/add_warehouse', data={
            'name': '',
            'tilavuus': '100',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_add_warehouse_zero_capacity_not_added(self):
        response = self.client.post('/add_warehouse', data={
            'name': 'ZeroCapacity',
            'tilavuus': '0',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_remove_warehouse(self):
        self.client.post('/add_warehouse', data={
            'name': 'ToRemove',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertIn('ToRemove', warehouses)

        response = self.client.post(
            '/remove_warehouse/ToRemove',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('ToRemove', warehouses)

    def test_remove_nonexistent_warehouse(self):
        response = self.client.post(
            '/remove_warehouse/NonExistent',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_view_warehouse(self):
        self.client.post('/add_warehouse', data={
            'name': 'ViewTest',
            'tilavuus': '100',
            'alku_saldo': '25'
        })
        response = self.client.get('/warehouse/ViewTest')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ViewTest', response.data)
        self.assertIn(b'25', response.data)
        self.assertIn(b'100', response.data)

    def test_view_nonexistent_warehouse_redirects(self):
        response = self.client.get('/warehouse/NonExistent')
        self.assertEqual(response.status_code, 302)

    def test_add_to_warehouse(self):
        self.client.post('/add_warehouse', data={
            'name': 'AddTest',
            'tilavuus': '100',
            'alku_saldo': '10'
        })
        response = self.client.post('/warehouse/AddTest/add', data={
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses['AddTest'].saldo, 30)

    def test_add_to_warehouse_overflow(self):
        self.client.post('/add_warehouse', data={
            'name': 'OverflowTest',
            'tilavuus': '50',
            'alku_saldo': '40'
        })
        self.client.post('/warehouse/OverflowTest/add', data={
            'amount': '100'
        }, follow_redirects=True)
        self.assertEqual(warehouses['OverflowTest'].saldo, 50)

    def test_remove_from_warehouse(self):
        self.client.post('/add_warehouse', data={
            'name': 'RemoveTest',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/RemoveTest/remove', data={
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses['RemoveTest'].saldo, 30)

    def test_remove_from_warehouse_more_than_available(self):
        self.client.post('/add_warehouse', data={
            'name': 'EmptyTest',
            'tilavuus': '100',
            'alku_saldo': '30'
        })
        self.client.post('/warehouse/EmptyTest/remove', data={
            'amount': '100'
        }, follow_redirects=True)
        self.assertEqual(warehouses['EmptyTest'].saldo, 0)

    def test_add_to_nonexistent_warehouse(self):
        response = self.client.post('/warehouse/NonExistent/add', data={
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Management', response.data)

    def test_remove_from_nonexistent_warehouse(self):
        response = self.client.post('/warehouse/NonExistent/remove', data={
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Management', response.data)

    def test_invalid_capacity_value(self):
        response = self.client.post('/add_warehouse', data={
            'name': 'InvalidTest',
            'tilavuus': 'invalid',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('InvalidTest', warehouses)

    def test_invalid_amount_to_add(self):
        self.client.post('/add_warehouse', data={
            'name': 'InvalidAddTest',
            'tilavuus': '100',
            'alku_saldo': '10'
        })
        self.client.post('/warehouse/InvalidAddTest/add', data={
            'amount': 'invalid'
        }, follow_redirects=True)
        self.assertEqual(warehouses['InvalidAddTest'].saldo, 10)

    def test_invalid_amount_to_remove(self):
        self.client.post('/add_warehouse', data={
            'name': 'InvalidRemoveTest',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        self.client.post('/warehouse/InvalidRemoveTest/remove', data={
            'amount': 'invalid'
        }, follow_redirects=True)
        self.assertEqual(warehouses['InvalidRemoveTest'].saldo, 50)

    def test_warehouse_displayed_in_list(self):
        self.client.post('/add_warehouse', data={
            'name': 'ListTest',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.get('/')
        self.assertIn(b'ListTest', response.data)
        self.assertNotIn(b'No warehouses yet', response.data)
