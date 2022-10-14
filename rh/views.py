import pandas as pd
import datetime
import sqlite3
import json
import re, urllib
from dateutil.relativedelta import relativedelta



from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site  

from django.utils.encoding import force_bytes, force_str  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  

from django.core.mail import EmailMessage  
from django.views.decorators.cache import cache_control
from django.conf import settings
from django.forms import modelformset_factory, inlineformset_factory
from django import forms

from .models import *
from .forms import *
from .decorators import unauthenticated_user
from .tokens import account_activation_token 


#############################################
########### Authntication Views #############
#############################################
def activate_account(request, uidb64, token):
    """Activate User account"""
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation, you can login now into your account.")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('login')


def send_account_activation_email(request, user, to_email):
    """Email verification for resigtration """
    current_site = get_current_site(request)  
    mail_subject = 'Activation link has been sent to your email id'  
    message = loader.render_to_string('registration/activation_email_template.html', {  
        'user': user,  
        'domain': current_site.domain,  
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),  
        'token': account_activation_token.make_token(user),  
        'protocol': 'https' if request.is_secure() else 'http', 
    })  
    email = EmailMessage(  
        mail_subject, message, to=[to_email]  
    )
    if email.send():
        template = loader.get_template('registration/activation_email_done.html')
        context = {'user': user, 'to_email': to_email}
        return HttpResponse(template.render(context, request))
    else:
        messages.error(request, 
            f"""Problem sending email to <b>{to_email}</b>m check if you typed it correctly."""
        )


@cache_control(no_store=True)
@unauthenticated_user
def register_view(request):
    """Registration view for creating new signing up"""
    template = loader.get_template('registration/signup.html')
    form = RegisterForm()
    organizations = Organization.objects.all()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            # Registration with email confirmation step.
            if settings.DEBUG==True:
                # If development mode then go ahead and create the user.
                user = form.save()
                messages.success(request, f'Account created successfully for {username}.')
            else:
                # If production mode send a verification email to the user for account activation
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                return send_account_activation_email(request, user, email)  
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
        
    context = {'form': form, 'organizations': organizations}
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@unauthenticated_user
def login_view(request):
    """User Login View """
    template = loader.get_template('registration/login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('index')
        else:
            messages.error(request, f'Enter correct username and password.')
    context = {}
    return HttpResponse(template.render(context, request))


def logout_view(request):
    """User Logout View"""
    messages.info(request, f'{request.user} logged out.')
    logout(request)
    return redirect("/login")


#############################################
############### Index Views #################
#############################################
@cache_control(no_store=True)
def index(request):
    template = loader.get_template('index.html')

#     play_db = settings.PLAY_DB
#     con = sqlite3.connect(play_db)

#     play = con.execute("""
# SELECT 
# DATE('2022-0' || (r.month +1) || '-01') as month,
# SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
# FROM benef b 
# INNER JOIN report r on b.report_id=r.id
# INNER JOIN activity a on a.id = b.activity_id
# INNER JOIN project p on p.id=r.project_id
# INNER JOIN org o on o.id=p.org_id
# INNER JOIN locs on locs.id = b.loc_id
# WHERE substr(locs.code, 0, 3) = 'AF' AND 
# o.short <> 'iMMAP' AND 
# r.year = 2022
# GROUP BY r.month
# ORDER BY month
# """)

#     types = []
#     nb_benef = []
#     for x in play:
#         types.append(
#             datetime.date.fromisoformat(x[0]).strftime('%B')
#         )
#         nb_benef.append(x[1])

    
#     months = str(types[0:10])
#     benefs = str(nb_benef[0:10])

#     df = pd.read_sql("""
# SELECT 
# DATE('2022-0' || (r.month +1) || '-01') as month, p.cluster,
# --a.activity_type || ' - ' || a.activity_desc as activity,
# SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
# FROM benef b 
# INNER JOIN report r on b.report_id=r.id
# INNER JOIN activity a on a.id = b.activity_id
# INNER JOIN project p on p.id=r.project_id
# INNER JOIN org o on o.id=p.org_id
# INNER JOIN locs on locs.id = b.loc_id
# WHERE substr(locs.code, 0, 3) = 'AF' AND 
# o.short <> 'iMMAP' AND 
# r.year = 2022 AND
# p.cluster IN ('ESNFI', 'FSAC', 'Protection', 'WASH')
# GROUP BY r.month, p.cluster
# ORDER BY month, cluster;
#     """, con=con)
    
#     clusters = df.pivot(index='month', columns='cluster', values='people_recieved').convert_dtypes().fillna(0).to_dict('list')

#     df = pd.read_sql("""
#     SELECT 
# a.activity_type || ' - ' || a.activity_desc as activity, o.short, l2.name,
# printf("%,d", SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men)) AS people_recieved
# FROM benef b 
# INNER JOIN report r on b.report_id=r.id
# INNER JOIN activity a on a.id = b.activity_id
# INNER JOIN project p on p.id=r.project_id
# INNER JOIN org o on o.id=p.org_id
# INNER JOIN locs on locs.id = b.loc_id
# INNER JOIN locs l2 on locs.parent_id = l2.id
# WHERE substr(locs.code, 0, 3) = 'AF' AND 
# o.short <> 'iMMAP' AND 
# r.year = 2022 AND
# r.month = 6 AND r.status='complete'
# GROUP BY l2.id, activity_type, activity_desc HAVING people_recieved IS NOT NULL
# ORDER BY month, l2.name, people_recieved desc;
#     """, con=con)

#     activities = df.to_dict('records')
#     # import pdb; pdb.set_trace()
#     context = {
#         'months': months, 
#         'benefs': benefs,
#         'ESNFI': clusters['ESNFI'],
#         'FSAC': clusters['FSAC'],
#         'Protection': clusters['Protection'],
#         'WASH': clusters['WASH'],
#         'activities': activities,
#     }
    context = {}
    return HttpResponse(template.render(context, request))


#############################################
############### Profile Views #################
#############################################
@cache_control(no_store=True)
@login_required
def profile(request):
    template = loader.get_template('profile.html')
    user = request.user
    context = {'user': user}
    return HttpResponse(template.render(context, request))


#############################################
############# Activities Views ##############
#############################################
@cache_control(no_store=True)
@login_required
def load_activity_json_form(request):
    """Create form elements and return JsonResponse to template"""
    data = None
    json_fields = {}
    if request.GET.get('activity', '') or request.GET.get('activity_plan_id'):
        if request.GET.get('activity'):
            activity_id = int(request.GET.get('activity', ''))
            json_fields = Activity.objects.get(id=activity_id).fields
        else:
            activity_plan = int(request.GET.get('activity_plan_id', ''))
            json_fields = ActivityPlan.objects.get(id=activity_plan).activity.fields
        
    if request.GET.get('activity_plan_id') != 'None':
        activity_plan_id = int(request.GET.get('activity_plan_id', ''))
        data = ActivityPlan.objects.get(id=activity_plan_id).activity_fields
    form_class = get_dynamic_form(json_fields, data)
    form = form_class()
    temp = loader.render_to_string("dynamic_form_fields.html", {'form': form})
    return JsonResponse({"form": temp})


@cache_control(no_store=True)
@login_required
def activity_plans(request):
    """Activity Plans"""
    activity_plans = ActivityPlan.objects.all()
    return render(request, 'activities/activity_plans.html', {'activity_plans': activity_plans})


@cache_control(no_store=True)
@login_required
def create_activity_plan(request):
    """Create Activity Plans"""
    if request.method == 'POST':
        form = ActivityPlanForm(request.POST)
        if form.is_valid():
            json_data = {}
            activity = Activity.objects.get(id=request.POST.get('activity'))
            json_class = get_dynamic_form(activity.fields)
            json_form = json_class(request.POST)
            if json_form.is_valid():
                json_data = json_form.cleaned_data
            activity_plan = form.save(commit=False)
            activity_plan.activity_fields = json_data
            form.save()
            return redirect('/activity_plans')
    else:
        form = ActivityPlanForm()
    return render(request, 'activities/activity_plans_form.html', {'form': form})


@cache_control(no_store=True)
@login_required
def update_activity_plan(request, pk):
    """Update Activity"""
    activity_plan = ActivityPlan.objects.get(id=pk)
    form = ActivityPlanForm(instance=activity_plan)
    json_class = get_dynamic_form(activity_plan.activity.fields, initial_data=activity_plan.activity_fields)
    json_form = json_class()
    if request.method == 'POST':
        form = ActivityPlanForm(request.POST, instance=activity_plan)
        if form.is_valid():
            json_data = {}
            activity = Activity.objects.get(id=request.POST.get('activity'))
            json_class = get_dynamic_form(activity.fields)
            json_form = json_class(request.POST)
            if json_form.is_valid():
                json_data = json_form.cleaned_data
            activity_plan = form.save(commit=False)
            activity_plan.activity_fields = json_data
            form.save()
            return redirect('/activity_plans')
    context = {'form': form, 'activity_plan': activity_plan.id}
    return render(request, 'activities/activity_plans_form.html', context)



#############################################
############## Project Views ################
#############################################
@cache_control(no_store=True)
@login_required
def load_activities_details(request):
    """Load activities related to a cluster"""
    cluster_ids = dict(request.GET.lists()).get('clusters[]', [])
    listed_activity_ids = dict(request.GET.lists()).get('listed_activities[]', [])
    cluster_ids = list(map(int, cluster_ids))
    listed_activity_ids = list(map(int, listed_activity_ids))
    activities = Activity.objects.filter(clusters__in=cluster_ids).order_by('title').distinct()
    activities_options = """"""
    for activity in activities:
        option = f"""
        <option value="{activity.pk}">{activity.title}</option>
        """
        activities_options+=option
    return HttpResponse(activities_options)


@cache_control(no_store=True)
@login_required
def load_locations_details(request):
    """Load Locations with group info"""
    countries = Location.objects.filter(type='Country')
    provinces = Location.objects.filter(type='Province').order_by('name')
    country_group = """"""
    province_group = """"""
    for country in countries:
        for province in provinces:
            district_options = """"""
            districts = Location.objects.filter(parent=province)
            for district in districts:
                district_options += f"""
                <option value="{district.pk}">
                    {district.name}
                </option>"""
            
            province_group += f"""
            <optgroup label="{province.name}">
                <option value="{province.pk}">{province.name} ({province.type})</option>
                {district_options}
            </optgroup>"""

        country_group += f"""
        <optgroup label="{country.name}">
            <option value="{country.pk}">{country.name}</option>
        </optgroup>
        {province_group}
        """
    return HttpResponse(country_group)


@cache_control(no_store=True)
@login_required
def projects_view(request):
    """Projects Plans"""
    projects = Project.objects.all()
    return render(request, 'projects/projects.html', {'projects': projects})


@cache_control(no_store=True)
@login_required
def create_project_view(request):
    """Create Project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project_id = form.save()
            return redirect('create_project_activity_plan', project=project_id.pk)
    else:
        form = ProjectForm(initial={'user': request.user})
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def update_project_view(request, pk):
    """Update Project view"""
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project_id = form.save()
            return redirect('update_project_activity_plan', project=project_id.pk)
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_activity_plan(request, project):
    project = Project.objects.get(id=project)
    activities = project.activities.all()
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, exclude=['project', 'activity'], form=ActivityPlanForm, extra=len(activities))
    if request.method == 'POST':
        formset = ActivityPlanFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form_data = form.cleaned_data
                json_data = {}
                activity = Activity.objects.get(id=form_data['activity_id'])
                json_class = get_dynamic_form(activity.fields)
                json_form = json_class(request.POST)
                if json_form.is_valid():
                    json_data = json_form.cleaned_data

                activity_plan = form.save(commit=False)
                activity_plan.activity = activity
                activity_plan.project = project
                activity_plan.activity_fields = json_data
                activity_plan.save()
            return redirect('projects')
    else:
        initials = []
        for activity in activities:
            initials.append({'project': project, 'activity': activity, 'activity_id': activity.id})
        formset = ActivityPlanFormSet(queryset=ActivityPlan.objects.none(), initial=initials)
    context = {'formset': formset}
    return render(request, "projects/project_activity_plan_form.html", context)


@cache_control(no_store=True)
@login_required
def update_project_activity_plan(request, project):
    project = Project.objects.get(id=project)
    activity_plans = ActivityPlan.objects.filter(project__id=project.pk, activity__in=[a.pk for a in project.activities.all()])
    if not activity_plans:
        return redirect('create_project_activity_plan', project=project.pk)
    activities = project.activities.all()
    extras = len(project.activities.all()) - len(activity_plans)
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, exclude=['project', 'activity'], form=ActivityPlanForm, extra=extras)
    initials = []
    for activity in activities:
        if activity.pk not in [a.activity.pk for a in activity_plans]:
            initials.append({'project': project, 'activity': activity, 'activity_id': activity.id})

    formset = ActivityPlanFormSet(request.POST or None, initial=initials, queryset=activity_plans)
    if request.method == "POST":
        if formset.is_valid():
            for form in formset:
                form_data = form.cleaned_data
                json_data = {}
                if form_data.get('id', False):
                    activity = ActivityPlan.objects.get(id=form_data.get('id', False).id).activity
                if form_data.get('activity_id', False):
                    activity = Activity.objects.get(id=form_data.get('activity_id', False))

                json_class = get_dynamic_form(activity.fields)
                json_form = json_class(request.POST)
                if json_form.is_valid():
                    json_data = json_form.cleaned_data
                activity_plan = form.save(commit=False)
                activity_plan.activity = activity
                activity_plan.project = project
                activity_plan.activity_fields = json_data
                activity_plan.save()
            return redirect('projects')
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {form.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    context = {'formset': formset}

    return render(request, "projects/project_activity_plan_form.html", context)


@cache_control(no_store=True)
@login_required
def stock_index_view(request):
    """Stock Views"""
    WarehouseLocationFormset = modelformset_factory(WarehouseLocation, fields='__all__', form=WarehouseLocationForm)
    if request.method == 'POST':
        enurl = urllib.parse.urlencode(request.POST)  # To convert POST into a string
        delete_btn = re.search(r'delete_(.*?)_warehouse', enurl)  # To match for e.g. delete_<num>_warehouse
        if delete_btn:
            warehouse_id = delete_btn.group(1)
            try:
                warehouse_location_id = WarehouseLocation.objects.get(pk=warehouse_id)
            except:
                warehouse_location_id = None
            if warehouse_location_id:
                warehouse_location_id.delete()
            
            formset = WarehouseLocationFormset(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()

        formset = WarehouseLocationFormset(request.POST, queryset=WarehouseLocation.objects.all())
        if formset.is_valid():
            instances = formset.save()
            for instance in instances:
                now =  datetime.datetime.now(datetime.timezone.utc)
                due_date = now + relativedelta(day=31)

                stock_report = StockReports.objects.filter(created_at__range=[now.date(), due_date.date()])
                if not stock_report:
                    stock_report = StockReports(due_date=due_date)
                    stock_report.save()
                instance.save()

            return redirect('stocks')
    formset = WarehouseLocationFormset(queryset=WarehouseLocation.objects.all())

    stock_reports = StockReports.objects.all()

    return render(request, 'stocks/stocks_index.html', {'warehouse_location_formset': formset, 'stock_reports': stock_reports})


def stock_report_view(request, pk):
    stock_report = StockReports.objects.get(id=pk)
    stock_location_details = stock_report.stock_location_details.all()
    warehouse_locations = WarehouseLocation.objects.all()
    warehouse_location_stocks = {}

    for warehouse in warehouse_locations:
        StockLocationDetailsFormSet = modelformset_factory(StockLocationDetails, exclude=['warehouse_location'], form=StockLocationDetailsForm, extra=1)
        warehouse_stock_details = stock_location_details.filter(warehouse_location__id=warehouse.id)
        formset = StockLocationDetailsFormSet(queryset=warehouse_stock_details, prefix=f'warehouse-{warehouse.id}-stock')
        warehouse_location_stocks.update({ warehouse: formset })

        if request.method == 'POST':
            enurl = urllib.parse.urlencode(request.POST)  # To convert POST into a string
            delete_btn = re.search(r'delete_(.*?)_stock_detail', enurl)  # To match for e.g. delete_<num>_warehouse
            if delete_btn:
                stock_detail_id = delete_btn.group(1)
                try:
                    stock_location_id = StockLocationDetails.objects.get(pk=stock_detail_id)
                except:
                    stock_location_id = None

                if stock_location_id:
                    stock_location_id.delete()
                    return redirect('stock_report', pk=pk)

            formset = StockLocationDetailsFormSet(request.POST, request.FILES, queryset=warehouse_stock_details, prefix=f'warehouse-{warehouse.id}-stock')
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.warehouse_location = warehouse
                    instance.save()
                    stock_report.stock_location_details.add(instance)
            else:
                for form in formset:
                    for error in form.errors:
                        error_message = f"Something went wrong {form.errors}"
                        if form.errors[error]:
                            error_message = f"{error}: {form.errors[error][0]}"
                        messages.error(request, error_message)

    context = {'report': stock_report, 'warehouse_location_stocks': warehouse_location_stocks}

    return render(request, 'stocks/stock_location_reports.html', context)