import imp
from django.shortcuts import render
from bookmark.models import Bookmark
from django.views.generic import ListView,DetailView

#사용자 권한생성
from django.views.generic import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin #장고에서 본래 가지고있는 기능
from django.urls import reverse_lazy #reverse랑 같은기능
from mysite.views import OwnerOnlyMixin

# Create your views here.

class BookmarkLV(ListView):
    model = Bookmark     #default로 html = bookmark_list.html

class BookmarkDV(DetailView):
    model = Bookmark  #html이름 지정 안했으면 default = bookmark_detail.html





class BookmarkCreateView(LoginRequiredMixin,CreateView): #로그인을 안했으면 로그인 창으로 넘겨준다.
    model = Bookmark
    fields = ['title','url'] #title, url을 입력받겠다.
    success_url = reverse_lazy('bookmark:index')

    def form_valid(self, form): #입력정보가 유효하다면, db에 저장 후 success_url로 이동한다.
        form.instance.owner = self.request.user #owner에 현재 로그인중인 사용자를 넣는다.
        return super().form_valid(form) 

class BookmarkChangeLV(LoginRequiredMixin, ListView):
    template_name = 'bookmark/bookmark_change_list.html'

    def get_queryset(self): #dlwltn6032가 만든 정보만 반환한다는 뜻.
        return Bookmark.objects.filter(owner=self.request.user) #로그인된 사용자가 접근할 수 있는 레코드만 반환해준다.

class BookmarkUpdateView(OwnerOnlyMixin, UpdateView): #로그인된 사용자가 이 레코드의 owner일때만, 접근가능하다.
    model = Bookmark
    fields = ['title','url'] #여기서 입력된 정보에 오류가 없으면, UpdateView자체적으로 form_valid()호출해서 db에 저장하고 success_url로 이동한다. 
    success_url = reverse_lazy('bookmark:index') #UpdateView 안에 이미 form_valid()메소드가 들어있다.

class BookmarkDeleteView(OwnerOnlyMixin, DeleteView): #로그인대상자 확인하고 접근가능한지 검사한 후, 접근하게 해준다.
    model = Bookmark
    success_url = reverse_lazy('bookmark:index')




