from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label='Имя')
    email = forms.EmailField(label='E-mail')
    message = forms.CharField(label='Сообщение', widget=forms.Textarea())


class CommentForm(forms.Form):
    text = forms.CharField(label='Добавить комментарий:', widget=forms.Textarea(
        attrs={'rows': 4, 'cols': 15}))
