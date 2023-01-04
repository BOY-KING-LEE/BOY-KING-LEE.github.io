from django import forms

class PostSearchForm(forms.Form):
    search_word = forms.CharField(label='검색단어입력')


