from django.shortcuts import render

from .forms import ProductForm#, RawProductForm

from .models import Product

# Create your views here.


def product_create_view(request):

    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ProductForm()

    context = {
        'form': form
    }

    return render(request, "product/product_create.html", context)

def product_detail_view(request):

    obj = Product.objects.get(id=4) #has the object with all it's attributes/variables

    context = {
        'object': obj
    }

    return render(request, "product/detail.html", context)

def dynamic_product_view(request, id):

    obj = Product.objects.get(id=id)

    context = {
        "object": obj
    }

    return render(request, "product/product_detail.html", context)