from django.shortcuts import render
from .models import YourModel  # Replace with your actual model names

def index(request):
    # Query all objects from the database
    items = YourModel.objects.all()  # Adjust this to your model

    # Pass the items to the template
    context = {
        'items': items,
    }
    return render(request, 'interacciones/index.html', context)

def detail(request, item_id):
    # Get a specific item by ID
    item = YourModel.objects.get(id=item_id)  # Adjust this to your model

    # Pass the item to the template
    context = {
        'item': item,
    }
    return render(request, 'interacciones/detail.html', context)