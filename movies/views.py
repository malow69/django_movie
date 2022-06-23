from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View


from .models import Movie, Actor, Genre, Rating
from .forms import ReviewForm, RatingForm


class GenreYear():
    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values("year").distinct()


class MoviesView(GenreYear, ListView):
    "Список фильмов"
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    # template_name = "movies/movie_list.html"
    paginate_by = 6


class MovieDetailView(GenreYear, DetailView):
    """Полное описание фильма"""
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    slug_field = "url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        return context


class AddReview(View):
    "Отзывы"
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())


class ActorView(GenreYear, DetailView):
    model = Actor
    template_name = 'movies/actor.html'
    slug_field = "name"


class FilterMoviesView(GenreYear, ListView):
    paginate_by = 6

    def get_queryset(self):
        queryset = Movie.objects.all()
        if "year" in self.request.GET:
            queryset = queryset.filter(year__in=self.request.GET.getlist("year"), draft=False).distinct()
        if "genre" in self.request.GET:
            queryset = queryset.filter(genres__in=self.request.GET.getlist("genre"), draft=False).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] = ''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] = ''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context


class AddStarRating(View):
    """Добавление рейтинга фильму"""
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class Search(GenreYear, ListView):
    """Поиск фильмов"""
    paginate_by = 6

    def get_queryset(self):
        q = self.request.GET.get('q').capitalize()
        return Movie.objects.filter(title__icontains=q, draft=False)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context

    def get_years(self):
        return sorted(Movie.objects.filter(draft=False).values_list("year", flat=True).distinct())