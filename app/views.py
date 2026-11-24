from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm
from django.contrib.auth.decorators import login_required
@login_required
def home(request):

    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = ExpenseForm()

    category = request.GET.get('category', '')
    search = request.GET.get('search', '')

    expenses = Expense.objects.all().order_by('-date', '-id')

    # Category filtering
    if category:
        expenses = expenses.filter(category=category)

    # Search functionality
    if search:
        expenses = expenses.filter(title__icontains=search)

    # Total expense calculation
    total = Expense.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Total transaction count
    count = Expense.objects.count()

    return render(request, 'expenses/home.html', {
        'form': form,
        'expenses': expenses,
        'total': total,
        'count': count,
        'category': category,
        'search': search,
    })

@login_required
def delete_expense(request, pk):

    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        expense.delete()

    return redirect('home')


def edit_expense(request, pk):

    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/edit.html', {
        'form': form,
        'expense': expense,
    })