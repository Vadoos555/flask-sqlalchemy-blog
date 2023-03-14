import unittest
from app import app, db
from app.models import User, Post
from app.forms import LoginForm, RegisterForm


class FormsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_form(self):
        form = LoginForm()
        self.assertFalse(form.validate())
        self.assertEqual(form.username.errors, ['Это поле обязательно к заполнению.'])
        self.assertEqual(form.password.errors, ['Это поле обязательно к заполнению.'])

    def test_register_form(self):
        form = RegisterForm()
        self.assertFalse(form.validate())
        self.assertEqual(form.username.errors, ['Это поле обязательно к заполнению.'])
        self.assertEqual(form.email.errors, ['Это поле обязательно к заполнению.'])
        self.assertEqual(form.password.errors, ['Это поле обязательно к заполнению.'])


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='john')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_user_creation(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(u.id)
        self.assertEqual(u.username, 'john')
        self.assertEqual(u.email, 'john@example.com')
        self.assertTrue(u.check_password('password'))

    def test_post_creation(self):
        u = User(username='test', email='test@example.com')
        p = Post(title='Test Post', body='This is a test post', author=u)
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        self.assertIsNotNone(p.id)
        self.assertEqual(p.author, u)

    def test_user_posts(self):
        u = User(username='test', email='test@example.com')
        p1 = Post(title='Test Post 1', body='This is a test post', author=u)
        p2 = Post(title='Test Post 2', body='This is another test post', author=u)
        db.session.add(u)
        db.session.add_all([p1, p2])
        db.session.commit()
        self.assertEqual(u.post.count(), 2)
        self.assertEqual(u.post.first().title, 'Test Post 1')
        self.assertEqual(u.post.first().body, 'This is a test post')
        self.assertEqual(u.post.order_by(Post.timestamp.desc()).first(), p2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
