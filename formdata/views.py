from django.shortcuts import render

# Create your views here.
def show_form(request):
    template_name = "formdata/show_form.html"
    return render(request, template_name)