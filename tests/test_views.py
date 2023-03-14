import unittest
from app import app, db
from app.models import User, Post


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.create_all()
        self.client = app.test_client()

        user = User(username='testuser', email='testuser@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_route(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/login', data=dict(
            username='testuser',
            password='password',
            remember_me=False
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(b'Homepage' in response.data)

    def test_logout_route(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(b'Homepage' in response.data)

    def test_register_route(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/register', data=dict(
            username='newuser',
            email='newuser@example.com',
            password='password',
            confirm_password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(b'Login' in response.data)

    def test_add_post_route(self):
        self.client.post('/login', data=dict(
            username='testuser',
            password='password',
            remember_me=False
        ), follow_redirects=True)

        response = self.client.get('/add_post')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/add_post', data=dict(
            title='New post',
            body='This is a test post.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        post = Post.query.filter_by(title='New post').first()
        self.assertIsNotNone(post)

    def test_show_post_route(self):
        # Create a test post
        post = Post(title='Test post', body='This is a test post.')
        post.author = User.query.filter_by(username='testuser').first()
        db.session.add(post)
        db.session.commit()

        self.client.post('/login', data=dict(
            username='testuser',
            password='password',
            remember_me=False
        ), follow_redirects=True)

        response = self.client.get(f'/post/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Test post' in response.data)
        self.assertTrue(b'This is a test post.' in response.data)

        user = User(username='otheruser', email='otheruser@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        self.client.post('/login', data=dict(
            username='otheruser',
            password='password',
            remember_me=False
        ), follow_redirects=True)
        response = self.client.post(f'/post/{post.id}', follow_redirects=True)
        self.assertTrue(b'You cannot delete this post!' in response.data)

        self.client.post(f'/post/{post.id}', data=dict(
            delete=True
        ), follow_redirects=True)
        self.assertIsNone(Post.query.filter_by(title='Test post').first())
        self.assertTrue(b'Your post has been deleted.' in response.data)


if __name__ == '__main__':
    unittest.main()
