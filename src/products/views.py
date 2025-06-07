from django.shortcuts import render

from .forms import ProductForm#, RawProductForm

from .models import Product

# Create your views here.

# def product_create_view(request):

#     form = RawProductForm()

#     if request.method == 'POST':
#         form = RawProductForm(request.POST or None)

#         if form.is_valid():
#             print(form.cleaned_data) #data that comes through after validation
#             Product.objects.create(**form.cleaned_data)
#         else:
#             print(form.errors)

#     context = {
#         'form': form
#     }

#     return render(request, "product/product_create.html", context)

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