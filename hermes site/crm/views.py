from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.utils import timezone
from .forms import OrderForm

def orders(request):
    orders = Order.objects.filter(order_date__lte=timezone.now()).order_by('id')
    return render(request, 'orders/index.html', {'orders': orders})

def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'orders/order_detail.html', {'order': order})

def order_new(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_manager = request.user
            order.order_date = timezone.now()
            order.save()
            return redirect('order_detail', id=order.id)
    else:
        form = OrderForm()
    return render(request, 'orders/order_edit.html', {'form': form})


def order_edit(request, id):
    post = get_object_or_404(Order, id=id)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=post)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_manager = request.user
            order.order_date = timezone.now()
            order.save()
            return redirect('order_detail', id=post.id)
    else:
        form = OrderForm(instance=post)
    return render(request, 'orders/order_edit.html', {'form': form})


# Create your views here.
