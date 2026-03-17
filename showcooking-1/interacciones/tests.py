from django.test import TestCase
from .models import YourModel  # Replace with your actual model

class InteraccionesTests(TestCase):

    def setUp(self):
        # Set up any initial data for your tests here
        YourModel.objects.create(field1='value1', field2='value2')  # Replace with actual fields and values

    def test_model_creation(self):
        """Test that the model instance is created correctly."""
        instance = YourModel.objects.get(field1='value1')
        self.assertEqual(instance.field2, 'value2')  # Replace with actual field checks

    def test_model_str(self):
        """Test the string representation of the model."""
        instance = YourModel.objects.create(field1='test')
        self.assertEqual(str(instance), 'Expected String Representation')  # Replace with actual expected value

    def test_view_response(self):
        """Test that the view returns a successful response."""
        response = self.client.get('/your-url/')  # Replace with your actual URL
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        """Test that the correct template is used."""
        response = self.client.get('/your-url/')  # Replace with your actual URL
        self.assertTemplateUsed(response, 'your_template.html')  # Replace with your actual template name

    def test_data_in_template(self):
        """Test that the data is passed to the template correctly."""
        response = self.client.get('/your-url/')  # Replace with your actual URL
        self.assertContains(response, 'value1')  # Replace with actual data you expect in the template