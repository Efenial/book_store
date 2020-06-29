from PIL import Image
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from pytils.translit import slugify
from django.template.defaultfilters import slugify as django_slugify

alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 'ю': 'yu',
            'я': 'ya'}


def slugify(s):
    """
    Overriding django slugify that allows to use russian words as well.
    """
    return django_slugify(''.join(alphabet.get(w, w) for w in s.lower()))
# Create your models here.


class Category(models.Model):
    category = models.CharField(max_length=50, verbose_name = "Категория")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.category

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"


class Book(models.Model):
    title = models.CharField("Название", max_length=300)
    slug = models.SlugField(unique=True)
    description = models.TextField("Описание", max_length=1000, default="About book")
    image = models.ImageField( "Изображение", default='default_book.png', upload_to='books_pics')
    book_pdf = models.FileField("Загрузите книгу" ,null=True, blank=True, upload_to='books_pdf')
    author = models.CharField("Автор", max_length=100)
    book_amount = models.IntegerField("Колличество книг")
    publish_date = models.DateField("Дата публикации")
    number_of_pages = models.IntegerField("Колличество страниц")
    category = models.ForeignKey('Category', verbose_name = "Категория", on_delete=models.PROTECT)
    last_rating = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def actual_rating(self):
        list_of_stars = []
        for star in range(self.last_rating):
            list_of_stars.append(star)
        return list_of_stars

    @property
    def calc_rating(self):
        ratings = BookReview.objects.filter(book=self)
        if ratings:
            result = 0
            for rating in ratings:
                result += rating.rating
            result = int(result / len(ratings))
            return result
        else:
            return 0

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 200 or img.width > 200:
            output_size = (150, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    class Meta:
        verbose_name_plural = "Книги"
        verbose_name = "Книгу"


class BookRentHistory(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, editable=False, related_name='books')
    rent_date = models.DateField(auto_now_add=True, editable=False)
    back_date = models.DateField(
        default=datetime.now()+timedelta(days=30))

    @property
    def how_many_days(self):
        return str(self.back_date - datetime.now().date())[:2]

    class Meta:
        verbose_name_plural = "История скачивания книг"
        verbose_name = "Книгу"


class BookReview(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    rating = models.IntegerField()


class BookComment(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, verbose_name = "Пользователь", on_delete=models.PROTECT)
    text = models.CharField(verbose_name = "Комментарий", max_length=300)

    class Meta:
        verbose_name_plural = "Полученные комментарии"
        verbose_name = "Комментарии"
    


class InBoxMessages(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField(max_length=500)

    def __str__(self):
        return f'Message from {self.name}'

    class Meta:
        verbose_name_plural = "Полученные сообщения"
        verbose_name = "Сообщение"
