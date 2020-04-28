from django.contrib.auth import (
	authenticate, 
	get_user_model,
	login,
	logout)
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils import timezone


from .models import User, UserProfile, PropertyEntry, Request, Match
from .tokens import default_token_generator

from .forms import UserLoginForm, UserSignUpForm, PropertyEntryForm, UserAccountForm, RequestEntryForm

from comments.forms import CommentForm, ReviewForm
from comments.models import Comment, Review

from django import forms

# Create your views here.


# using choices field:
# userprofile = UserProfile()
# userprofile.user_type = CharityType.BUYER
# userprofile.save()


# Decorators
# login required 



def get_manual_field_add_listing(context, form, form_type):

	property_type = "property_type" 
	no_of_bedrooms = "no_of_bedrooms"
	no_of_bathrooms = "no_of_bathrooms"
	location = "location"
	price = "price"
	dsq = "dsq"
	other_details = "other_details"
	property_number = "property_number"

	first_name = 'first_name'
	last_name = 'last_name'
	email = 'email'
	phone_number = 'phone_number'
	password1 = 'password1'
	password2 = 'password2'

	content = "content"
	ratings = "ratings"
	

	if form_type == "UserSignUpForm" or form_type == "UserAccountForm":
		

		context["first_name_field"] = form.fields[first_name].get_bound_field(form, first_name)
		context["last_name_field"] = form.fields[last_name].get_bound_field(form, last_name)
		context["email_field"] = form.fields[email].get_bound_field(form, email)
		context["phone_number_field"] = form.fields[phone_number].get_bound_field(form, phone_number)
		try:
			context["password1_field"] = form.fields[password1].get_bound_field(form, password1)
			context["password2_field"] = form.fields[password2].get_bound_field(form, password2)
		except:
			pass

	elif form_type == "PropertyEntryForm":


		context["property_type_field"] = form.fields[property_type].get_bound_field(form, property_type)
		context["no_of_bedrooms_field"] = form.fields[no_of_bedrooms].get_bound_field(form, no_of_bedrooms)
		context["no_of_bathrooms_field"] = form.fields[no_of_bathrooms].get_bound_field(form, no_of_bathrooms)
		context["location_field"] = form.fields[location].get_bound_field(form, location)
		context["price_field"] = form.fields[price].get_bound_field(form, price)
		context["dsq_field"] = form.fields[dsq].get_bound_field(form, dsq)
		context["other_details_field"] = form.fields[other_details].get_bound_field(form, other_details)
		context["property_number_field"] = form.fields[property_number].get_bound_field(form, property_number)
		context["other_details_field"] = form.fields[other_details].get_bound_field(form, other_details)

	elif form_type == "RequestEntryForm":
		context["property_type_field"] = form.fields[property_type].get_bound_field(form, property_type)
		context["no_of_bedrooms_field"] = form.fields[no_of_bedrooms].get_bound_field(form, no_of_bedrooms)
		context["no_of_bathrooms_field"] = form.fields[no_of_bathrooms].get_bound_field(form, no_of_bathrooms)
		context["location_field"] = form.fields[location].get_bound_field(form, location)
		context["price_field"] = form.fields[price].get_bound_field(form, price)
		context["dsq_field"] = form.fields[dsq].get_bound_field(form, dsq)

	elif form_type == "CommentForm":
		context["content_field"] = form.fields[content].get_bound_field(form, content)

	elif form_type == "ReviewForm":
		context["content_field"] = form.fields[content].get_bound_field(form, content)

	return context


def login_must(f):
	
	def login_inner(*args, **kwargs):
		account_owner = args[0].user
		if not account_owner.is_authenticated:
			raise PermissionDenied
		return f(*args, **kwargs)
	return login_inner

# ======================================================



def activation_sent_view(request, template_name="activation_sent.html"):
	return render(request, template_name)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and default_token_generator.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.userprofile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('mainapp:account')
    else:
        return render(request, 'activation_invalid.html')


def sign_in(request):
	next = request.GET.get("next")
	form = UserLoginForm(request.POST or None)

	if request.method == "POST":
		if form.is_valid():
			user = form.login(request)
			if user:	
				login(request, user)
				if next:
					return redirect(next)
		else:
			return redirect('mainapp:home')
		return redirect('mainapp:account')
	
@login_must
def sign_out(request):
	logout(request)
	return redirect('mainapp:home')


def index(request, template_name="index.html"):
	context = dict()	
	current_url = request.path
	context['current_url'] = current_url

	if current_url == "/sell/" or current_url == "/buy/":
		autoplay = False
	else:
		autoplay = True

	context['autoplay'] = autoplay

	return render(request, template_name, context)

def select_type(request, user_type=None):

	if user_type == "buyer":
		request.session['user_type'] = 'buyer'
	elif user_type == "seller":
		request.session['user_type'] = 'seller'
	else:
		raise Http404
	return redirect('mainapp:register')
	



def register(request, template_name="registration.html"):
	context = dict()
	form = UserSignUpForm(request.POST or None)
	form_type = "UserSignUpForm"
	context = get_manual_field_add_listing(context, form, form_type)
	try:
		user_type = request.session.get("user_type")
		context["user_type"] = user_type
	except:
		raise Http404
	
	
	if request.method  == 'POST':
		form = UserSignUpForm(request.POST)

		if form.is_valid():
			user = form.save()
			user.refresh_from_db()
			user.userprofile.first_name = form.cleaned_data.get('first_name')
			user.userprofile.last_name = form.cleaned_data.get('last_name')
			user.userprofile.email = form.cleaned_data.get('email')
			user.userprofile.user_type = user_type
			# user can't login until link confirmed
			user.is_active = False
			user.save()
			current_site = get_current_site(request)
			subject = 'Please Activate Your Account'
			# load a template like get_template() 
			# and calls its render() method immediately.
			message = render_to_string('activation_request.html', {'user': user,
	'domain': current_site.domain,
	'uid': urlsafe_base64_encode(force_bytes(user.pk)),
	# method will generate a hash value with user related data
	'token': default_token_generator.make_token(user),
	})

			to_email = form.cleaned_data.get('email')
			email = EmailMessage(subject, message, to=[to_email])
			email.send()
			return redirect('mainapp:activation_sent')
	# else:
	context["form"] = form

	
	return render(request, template_name, context)




@login_must
def account(request, template_name="account.html"):
	context = dict()
	account_owner = request.user
	
	user_obj = User.objects.get(email=account_owner.email)
	form = UserAccountForm(request.POST or None, instance=user_obj)
	form_type = "UserAccountForm"
	context = get_manual_field_add_listing(context, form, form_type)

	if request.user.userprofile.user_type == "Seller":
		properties = PropertyEntry.objects.filter(seller=request.user)
		context["properties"] = properties[:3]
		context["properties_count"] = properties.count()

		matched_requests_qs = Match.objects.valid_matches()
		matched_requests = matched_requests_qs.filter(property_entry__seller=request.user)
		context["matched_requests"] = matched_requests
		context["matched_requests_count"] = matched_requests.count()

		unmatched_requests_1 = Request.objects.filter(is_active=True).exclude(match__property_entry__seller=request.user)
		unmatched_requests_2 = Request.objects.filter(request_status="Pending")
		unmatched_requests = (unmatched_requests_1 | unmatched_requests_2)
		context["unmatched_requests"] = unmatched_requests
		context["unmatched_requests_count"] = unmatched_requests.count()

	elif request.user.userprofile.user_type == "Buyer":
		requests = Request.objects.filter(buyer=request.user)
		context["requests"] = requests
		context["requests_count"] = requests.count()

		
		matched_requests_qs = Match.objects.valid_matches()
		matched_requests = matched_requests_qs.filter(buyer_request__buyer=request.user)
		context["matched_requests"] = matched_requests
		context["matched_requests_count"] = matched_requests.count()
		context["properties"] = matched_requests

		unmatched_requests = Request.objects.filter(buyer=request.user, is_active=True, request_status="Pending").filter(match__isnull=True)
		context["unmatched_requests"] = unmatched_requests
		context["unmatched_requests_count"] = unmatched_requests.count()


		requests = Request.objects.filter(buyer=request.user)
		context["all_requests"] = requests
		context["all_requests_count"] = requests.count()
	
	if request.method == "POST":
		if form.is_valid():
			user = form.save(commit=False)
			user.email = form.cleaned_data.get('email')
			user.save()
		else:
			print(form.errors)
	
	context["form"] = form
	context["owner"] = account_owner

	

	return render(request, template_name, context)


def add_listing(request, template_name="add-listing.html"):
	context = dict()
	
	if request.user.userprofile.user_type == "Seller":
		form = PropertyEntryForm(request.POST or None)
		form_type = "PropertyEntryForm"
		context = get_manual_field_add_listing(context, form, form_type)
		# context["form"] = seller_form
	elif request.user.userprofile.user_type == "Buyer":
		form = RequestEntryForm(request.POST or None)
		form_type = "RequestEntryForm"
		context = get_manual_field_add_listing(context, form, form_type)
	else:
		raise PermissionDenied()
		
	
	if request.method == "POST":
		if form.is_valid():
			if form_type == "PropertyEntryForm":
				property_entry = form.save(commit=False)
				property_entry.seller = request.user
				property_entry.is_available = True
				property_entry.save()
			elif form_type == "RequestEntryForm":
				request_entry = form.save(commit=False)
				request_entry.buyer = request.user
				request_entry.request_status = "Pending"
				request_entry.is_active = True
				request_entry.save()
			
			return redirect('mainapp:account')
	context["form"] = form
	return render(request, template_name, context)


@login_must
def explore(request, template_name="explore.html"):
	context = dict()	

	if request.user.userprofile.user_type == "Buyer":
		matches_qs = Match.objects.valid_matches()
		matches = matches_qs.filter(buyer_request__buyer=request.user)
		context["entries"] = matches

		
	elif request.user.userprofile.user_type == "Seller":
		properties = PropertyEntry.objects.filter(seller=request.user)
		context["entries"] = properties

	else:
		raise PermissionDenied()

	return render(request, template_name, context)



@login_must
def matches(request, template_name="seller-matches.html"):
	context = dict()

	if request.user.userprofile.user_type == "Seller":
		matches_qs = Match.objects.valid_matches()
		matches = matches_qs.filter(property_entry__seller=request.user).order_by('engagement_status')
		context["matches"] = matches
	elif request.user.userprofile.user_type == "Buyer":
		return redirect('mainapp:explore')

	return render(request, template_name, context)





@login_must
def all_requests(request, template_name="all-requests.html"):

	if request.user.userprofile.user_type == "Buyer":
		context = dict()
		context["all_requests"] = Request.objects.filter(buyer=request.user)
		return render(request, template_name, context)


	elif request.user.userprofile.user_type == "Seller":
		return redirect('mainapp:unmatched-requests')


@login_must
def unmatched_requests(request, template_name="unmatched-requests.html"):
	context = dict()
	if request.user.userprofile.user_type == "Seller":
		context["unmatched_requests"] = Request.objects.filter(is_active=True).exclude(match__property_entry__seller=request.user).order_by('location')
	elif request.user.userprofile.user_type == "Buyer":
		unmatched_requests = Request.objects.filter(buyer=request.user, is_active=True, request_status="Pending").filter(match__isnull=True).order_by('location')
		context["unmatched_requests"] = unmatched_requests
	else:
		raise PermissionDenied()


	return render(request, template_name, context)


@login_must
def remove_request(request, id=None):

	buyer_request = get_object_or_404(Request, id=id)

	buyer_request.request_status = "Inactive"
	buyer_request.is_active = False
	buyer_request.save()

	return redirect('mainapp:all-requests')

@login_must
def activate_request(request, id=None):

	buyer_request = get_object_or_404(Request, id=id)

	buyer_request.is_active = True
	buyer_request.save()

	return redirect('mainapp:all-requests')





@login_must
def list_inside(request, id=None, template_name="list-inside.html"):


	context = dict()
	property_entry = get_object_or_404(PropertyEntry, id=id)
	if not property_entry.is_available:
		messages.info(request, "That property is no longer available")
		return redirect('mainapp:explore')
	context["property"] = property_entry

	if property_entry.is_favourite(request):

		css_class = 'fas'
		fav_status = "Remove From Favourites"
	else:
		css_class = 'far' 
		fav_status = "Add to Favourites"
	context["css_class"] = css_class
	context["add_or_remove"] = fav_status


	################
	#Rating stuff
	this_review, created= Review.objects.get_or_create(buyer=request.user, seller=property_entry.seller)
	print("B-{} - S-{} - thisbuyerrating-{} -avg_rating: {}".format(
		request.user.email,
		property_entry.seller.email,
		this_review.rating,
		this_review.average_rating))
	context["ratings"] = this_review.rating
	context["average_rating"] = this_review.average_rating

	###############

	
	comment_form = CommentForm(request.POST or None)
	form_type = "CommentForm"
	context = get_manual_field_add_listing(context, comment_form, form_type)
	
	if request.method == "POST":
		if comment_form.is_valid():
			content = comment_form.cleaned_data.get('content')
			
			new_comment, created = Comment.objects.get_or_create(
				buyer = request.user,
				property_entry = property_entry,
				content = content)
			print(new_comment)
			print(created)
			return HttpResponseRedirect(new_comment.property_entry.get_absolute_url()) 
	context["comments"] = property_entry.comments
	
	if request.user.userprofile.user_type == "Buyer":	
		try:
			match_id = request.GET['mid']
		except:
			match_id = request.session["match_id_orig"]
		
		request.session["match_id_orig"] = match_id
		match = get_object_or_404(Match, id=match_id)
		context["match"] = match
		print(match.engagement_status)
		

	return render(request, template_name, context)




######################################################################

####Some Javascript Related Stuff


###GET Requests

#JSON Repsonse
@login_must
def view_match(request):
	data = dict()

	if request.user.userprofile.user_type == "Buyer":	
		if request.method == "GET":
			try:
				match_id = request.GET['match_id']
			except:
				match_id = request.session["match_id_orig"]
			
		this_match = get_object_or_404(Match, id=match_id)
		data["match_buyer_first_name"] = this_match.buyer_request.buyer.first_name
		data["match_buyer_last_name"] = this_match.buyer_request.buyer.last_name
		data["match_buyer_email"] = this_match.buyer_request.buyer.email
		

		data["match_seller_first_name"] = this_match.property_entry.seller.first_name
		data["match_seller_last_name"] = this_match.property_entry.seller.last_name
		data["match_property_location"] = this_match.property_entry.location


	return JsonResponse(data)

@login_must
def view_contact(request):
	data = dict()

	if request.method == "GET":
		match_id = request.GET['match_id']
		this_match = Match.objects.get(id=match_id)
		data["buyer_first_name"] = this_match.buyer_request.buyer.first_name
		data["buyer_last_name"] = this_match.buyer_request.buyer.last_name
		data["buyer_email"] = str(this_match.buyer_request.buyer.email)
		data["engagement_date"] = str(this_match.engagement_date)[:10]


	return JsonResponse(data)


@login_must
def favourite(request):

	data = dict()
	if request.user.userprofile.user_type == "Buyer":
		user = request.user
		property_id = request.GET.get("property_entry_id")
		this_property = get_object_or_404(PropertyEntry, id=property_id)
		
		if this_property.favourites.filter(id=user.id).exists():
			data["remove_favourite"] = True
			this_property.favourites.remove(user)
			data["flash_message"] = "This Property Has Been Removed From Your Favourites"
			data["fav_status"] = "Add to Favourites"
		else:
			data["add_favourite"] = True
			this_property.favourites.add(user)
			data["flash_message"] = "This Property Has Been Added To Your Favourites"
			data["fav_status"] = "Remove From Favourites"


	return JsonResponse(data)


###GET Requests

###POST Requests

#HTTP Response
@login_must
def engage(request, id=None):

	if request.method == "POST":
		match = get_object_or_404(Match, id=id)
		if match.is_valid:
			match.engagement_status = "Accepted"
			match.engagement_date = timezone.now()
			match.save()
		else:
			messages.info(request, "That property is no longer available")
			return redirect('mainapp:explore')

		return HttpResponseRedirect(match.property_entry.get_absolute_url())
	
@login_must
def decline_offer(request, id=None):
	if request.method == "POST":	
		match = get_object_or_404(Match, id=id)
		match.engagement_status = "Declined"
		match.engagement_date = timezone.now()
		match.save()
		return HttpResponseRedirect(match.property_entry.get_absolute_url())
###	POST Requests






####Some Javascript Related Stuff
######################################################################





######################################################################
#####Pages With No Code
def faqs(request, template_name="faq.html"):

	return render(request, template_name)

def terms(request, template_name="terms.html"):

	return render(request, template_name)

def contact(request, template_name="contact.html"):

	return render(request, template_name)

def pricing(request, template_name="pricing.html"):

	return render(request, template_name)


def listings(request, template_name="listings.html"):

	return render(request, template_name)

#####Pages With No Code
######################################################################


######################################################################
#####Error Pages, Temporary View Functions

def error_400(request, template_name="400.html"):

	return render(request, template_name)
def error_403(request, template_name="403.html"):

	return render(request, template_name)
def error_404(request, template_name="404.html"):

	return render(request, template_name)
def error_500(request, template_name="500.html"):

	return render(request, template_name)




#####Error Pages, Temporary View Functions
######################################################################
