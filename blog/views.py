from multiprocessing import context
from django.shortcuts import render

from django.views.generic import ListView,DetailView,TemplateView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView
from django.views.generic.dates import DayArchiveView, TodayArchiveView

from requests import post
from blog.models import Post
from django.conf import settings

from django.views.generic import FormView
from blog.forms import PostSearchForm
from django.db.models import Q
from django.shortcuts import render

from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from mysite.views import OwnerOnlyMixin
# Create your views here.


#ListView
class PostLV(ListView): #특정객체의 리스트를 모두 출력한다
    model = Post
    context_object_name = 'posts' #{'posts':Post} 이렇게 지정해도 , object_list(기본제공) 사용가능 ->context변수 어디로??
    template_name = 'blog/post_all.html'        #default인 post_list.html을 사용하지않고 이름 따로 지정                                                     # 여기로~!!!
    paginate_by = 2 #페이징기능 -> 한페이지에 보여주는 객체리스트는 2개



#DetailView
class PostDV(DetailView): #특정객체의 특정리스트(ex)1번째)의 상세정보를 출력한다 / pk대신 slug사용(urls.py에서)
    model = Post  #html이름지정x => default => post_detail.html

    def get_context_data(self, **kwargs): #댓글templates로 context변수를 넘겨주기 위한 메소드
        context = super().get_context_data(**kwargs)
        context['disqus_short'] = f"{settings.DISQUS_SHORTNAME}"
        context['disqus_id'] = f"post-{self.object.id}-{self.object.slug}"
        context['disqus_url'] = f"{settings.DISQUS_MY_DOMAIN}{self.object.get_absolute_url()}"
        context['disqus_title'] = f"{self.object.slug}"
        return context



#ArchiveView
class PostAV(ArchiveIndexView): #객체리스트를 가져와서 날짜기준으로 최신것부터 출력
    model = Post
    date_field = 'modify_dt' #기준은 수정날짜 기준

class PostYAV(YearArchiveView): #특정년도를 기준으로 그 해의 월을 출력한다.
    model = Post
    date_field = 'modify_dt'
    make_object_list = True # 해당연도에 해당하는 객체의 리스트를 만들어서 템플릿에 넘겨줍니다 => 컨텍스트변수 역할
    #month_format = '%b' default임.
class PostMAV(MonthArchiveView): #연월을 기준으로 최신것을 출력
    model = Post
    date_field = 'modify_dt'
    
class PostDAV(DayArchiveView):# 연월일을 기준으로 출력
    model = Post
    date_field = 'modify_dt'

class PostTAV(TodayArchiveView): #기준날짜가 오늘인 객체를 출력(DayArchiveView인데, 기준이 오늘!)
    model = Post
    date_field = 'modify_dt'



#taggit
class TagCloudTV(TemplateView):
    template_name = 'taggit/taggit_cloud.html'

class TaggedObjectLV(ListView):
    template_name = 'taggit/taggit_post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self,**kwargs):             #고정
        context = super().get_context_data(**kwargs) #문법 _ context변수를 사용하기 위한...
        context['tagname'] = self.kwargs['tag']
        return context #urls에서 넘겨온 <str:tag>를 'tagname'이라는 변수에 넣어서 templates로 return(보내준다)



#FormView
class SearchFormView(FormView):
    form_class = PostSearchForm
    template_name = 'blog/post_search.html'

    def form_valid(self, form): #입력값이 유효한지 검사
        searchWord = form.cleaned_data['search_word']  #유효하면 cleaned_date에 저장 / 이 사전에서 주황이를 뽑아내서 파랑이에 저장
        post_list = Post.objects.filter(Q(title__icontains=searchWord) | Q(description__icontains=searchWord)
        | Q(content__icontains=searchWord)).distinct #title des cont 다 검사/ 맞으면 post_list에 저장

        context = {} #넘겨줄 context형식지정(사전형식임)
        context['form'] = form
        context['search_term'] = searchWord
        context['object_list'] = post_list

        return render(self.request , self.template_name , context) #같은 페이지로 새로운 동작 / 13번을 2번으로 보낼거야


#사용자 c,u,d 권한
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title','slug','description','content','tags']
    initial = {'slug': 'auto-filling-do-not-input'} #초기에 / 슬러그에 미리 글씨를 저장
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.owner = self.request.user #dlwltn6032를 form.instance.owner에 넣는다.
        return super().form_valid(form) #db에 저장하고, success_url로 이동

class PostChangeLV(LoginRequiredMixin, ListView):
    template_name = 'blog/post_change_list.html'

    def get_queryset(self): #Post가 가진 모든 객체에서 dlwltn6032가 owner인 객체들만 반환(그것들만 접근할 수 있도록)
        return Post.objects.filter(owner=self.request.user)

class PostUpdateView(OwnerOnlyMixin, UpdateView): #UpdateView는 CreateView랑 같은html을 사용한다(django-default)
    model = Post
    fields = ['title','slug','description','content','tags']
    success_url = reverse_lazy('blog:index')

class PostDeleteView(OwnerOnlyMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')

    




