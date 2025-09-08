from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Review, Order, CartItem
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def movie_list(request):
    """Show all movies with optional search."""
    query = request.GET.get("q")
    if query:
        movies = Movie.objects.filter(Q(title__icontains=query))
    else:
        movies = Movie.objects.all()
    return render(request, "movies/movie_list.html", {"movies": movies, "query": query})

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.all().order_by('-created_at')  # latest first
    
    # Check if current user already has a review for this movie
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    return render(request, "movies/movie_detail.html", {
        "movie": movie, 
        "reviews": reviews,
        "user_review": user_review
    })

def register(request):
    """Sign up a new user."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # authenticate & login user immediately
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
            messages.success(request, f"Account created. Welcome, {username}!")
            return redirect("movie_list")
    else:
        form = SignUpForm()
    return render(request, "movies/register.html", {"form": form})

@login_required
def add_to_cart(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("view_cart")

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, "movies/cart.html", {"cart_items": cart_items})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect("view_cart")

@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items.exists():
        order = Order.objects.create(user=request.user)
        # Extract Movie objects from CartItems
        movies = [item.movie for item in cart_items]
        order.movies.add(*movies)  # use add() with unpacking
        cart_items.delete()  # clear cart
    return redirect("view_orders")

@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "movies/orders.html", {"orders": orders})

@login_required
def review_create(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    
    # Check if user already has a review for this movie
    existing_review = Review.objects.filter(movie=movie, user=request.user).first()
    if existing_review:
        # Redirect back if user already has a review
        return redirect("movie_detail", pk=movie.pk)
    
    if request.method == "POST":
        content = request.POST.get("content")
        if content and content.strip():
            Review.objects.create(movie=movie, user=request.user, content=content)
        return redirect("movie_detail", pk=movie.pk)
    return render(request, "movies/review_form.html", {"movie": movie})

@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            review.content = content
            review.save()
        return redirect("movie_detail", pk=review.movie.pk)
    return render(request, "movies/review_form.html", {"review": review})

@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    movie_pk = review.movie.pk
    review.delete()
    return redirect("movie_detail", pk=movie_pk)