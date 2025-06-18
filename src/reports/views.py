from django.shortcuts import render

# Create your views here.


def view_report(request):

    return render(request, "reports/report.html", {})